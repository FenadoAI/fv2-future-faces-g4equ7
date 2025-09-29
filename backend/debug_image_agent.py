#!/usr/bin/env python3
"""
Debug script to check ImageAgent responses
"""
import asyncio
import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agents.agents import ImageAgent, AgentConfig

async def test_image_agent():
    """Test the ImageAgent directly"""
    print("🎯 Testing ImageAgent directly...")

    try:
        config = AgentConfig()
        image_agent = ImageAgent(config)

        prompt = "Generate an image based on this description: A portrait of a happy, adorable child named Emma. A happy child with curly hair. High quality, professional portrait, soft lighting, warm and friendly expression. Provide only the image URL in your response."

        print(f"Sending prompt: {prompt}")

        result = await image_agent.execute(prompt, use_tools=True)

        print(f"Success: {result.success}")
        print(f"Content: '{result.content}'")
        print(f"Error: {result.error}")
        print(f"Metadata: {result.metadata}")

        # Test URL extraction patterns
        import re
        url_pattern = r'https?://[^\s<>"\'{}|\\^`[\]]+\.(jpg|jpeg|png|gif|webp|svg)'
        urls = re.findall(url_pattern, result.content, re.IGNORECASE)
        print(f"Extracted URLs: {urls}")

        # More flexible URL pattern
        general_url_pattern = r'https?://[^\s<>"\'{}|\\^`[\]]+'
        general_urls = re.findall(general_url_pattern, result.content, re.IGNORECASE)
        print(f"General URLs found: {general_urls}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_agent())