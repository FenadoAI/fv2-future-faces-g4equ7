#!/usr/bin/env python3
"""
Claude MCP Wrapper - Direct interface to real MCP image generation
This wrapper provides access to Claude Code's actual MCP image generation service
"""

from flask import Flask, request, jsonify
import logging
import json
import subprocess
import sys

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/real-generate', methods=['POST'])
def real_generate_image():
    """Generate real AI image using Claude Code's MCP service"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        logger.info(f"Calling REAL MCP image generation for: {prompt[:100]}...")

        # This calls the actual MCP image generation service available in Claude Code
        # We'll create a script that can access it

        # Create the command that will call Claude Code with MCP
        cmd = [
            'claude', '--output-format', 'json',
            '--system-prompt',
            f'Generate an image using the mcp__image__generate_image function with this prompt: {prompt}. Return only the JSON response with the image URL.',
            'Please generate an image'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0 and result.stdout:
                # Parse the response to extract the image URL
                try:
                    response = json.loads(result.stdout)
                    if 'url' in response:
                        image_url = response['url']
                        logger.info(f"REAL MCP generated image: {image_url}")
                        return jsonify({"success": True, "image_url": image_url})
                except json.JSONDecodeError:
                    # If not JSON, try to extract URL from text
                    output = result.stdout
                    if 'http' in output:
                        # Extract first URL found
                        import re
                        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', output)
                        if urls:
                            image_url = urls[0]
                            logger.info(f"REAL MCP generated image (text): {image_url}")
                            return jsonify({"success": True, "image_url": image_url})

            logger.error(f"MCP command failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("MCP call timed out")
        except FileNotFoundError:
            logger.error("Claude command not found - not running in Claude Code environment")

        # If we can't access the real MCP service, return a clear error
        return jsonify({
            "success": False,
            "error": "Real MCP image generation not available",
            "message": "This service requires Claude Code environment with MCP access"
        }), 503

    except Exception as e:
        logger.error(f"Error in real image generation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ready", "service": "claude_mcp_wrapper"})

if __name__ == '__main__':
    print("Starting Claude MCP Wrapper...")
    print("This service provides access to real MCP image generation")
    app.run(host='127.0.0.1', port=8003, debug=True)