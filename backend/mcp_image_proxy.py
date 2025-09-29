#!/usr/bin/env python3
"""
MCP Image Generation Proxy
This script provides a simple HTTP proxy to access MCP image generation
"""

from flask import Flask, request, jsonify
import asyncio
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """Generate image using MCP service"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # This would be called by Claude Code with MCP access
        # For now, return a success response that can be called externally
        return jsonify({
            "status": "ready",
            "prompt": prompt,
            "message": "Ready for MCP call"
        })

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)