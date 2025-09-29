#!/usr/bin/env python3
"""
Test script to directly call MCP image generation
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_direct_mcp():
    """Test direct MCP image generation"""
    print("🎯 Testing Direct MCP Image Generation...")

    mcp_token = os.getenv("CODEXHUB_MCP_AUTH_TOKEN")
    print(f"MCP Token: {mcp_token[:20]}..." if mcp_token else "No token found")

    if not mcp_token or mcp_token == "dummy-key":
        print("❌ CODEXHUB_MCP_AUTH_TOKEN not configured properly")
        return

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            prompt = "A portrait of a happy, adorable child named Emma. Bright child with curly hair and sparkling eyes. High quality, professional portrait, soft lighting, warm and friendly expression, realistic style."

            print(f"Generating image with prompt: {prompt[:100]}...")

            # MCP uses JSON-RPC 2.0 protocol
            response = await client.post(
                "https://mcp.codexhub.ai/image/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "generate_image",
                        "arguments": {
                            "prompt": prompt,
                            "aspect_ratio": "1:1",
                            "output_format": "webp",
                            "megapixels": "1"
                        }
                    }
                },
                headers={
                    "x-team-key": mcp_token,
                    "Content-Type": "application/json"
                }
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if "url" in result:
                    print(f"✅ Image generated successfully!")
                    print(f"Image URL: {result['url']}")
                else:
                    print(f"❌ No URL in response: {result}")
            else:
                print(f"❌ API error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_mcp())