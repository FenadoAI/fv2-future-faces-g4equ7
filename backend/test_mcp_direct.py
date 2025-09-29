#!/usr/bin/env python3
"""
Test MCP image generation directly with the Claude MCP image service
"""

import asyncio
import json

async def test_mcp_image_generation():
    """Test direct MCP image generation using Claude's image MCP service"""
    print("🎯 Testing MCP Image Generation with Claude's service...")

    try:
        # Use the mcp__image__generate_image function directly
        print("This should use Claude's actual MCP image generation service")

        # For now, let's make a simple call to see what happens
        prompt = "A portrait of a happy child with curly hair and bright eyes, professional portrait photography"

        print(f"Prompt: {prompt}")
        print("Note: This test requires Claude Code's MCP image generation service")

        # This would normally be called through Claude's MCP interface
        # Let's check if we can access it through the system

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_image_generation())