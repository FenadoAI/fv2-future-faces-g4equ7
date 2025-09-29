#!/usr/bin/env python3
"""
Test script for image generation functionality
"""

import asyncio
import httpx
import json

API_BASE = "http://localhost:8001/api"

async def test_image_generation():
    """Test the image generation endpoint"""
    print("🎯 Testing Image Generation API...")

    async with httpx.AsyncClient() as client:
        # Test 1: Generate child image
        print("\n1. Testing child image generation...")

        payload = {
            "child_name": "Emma",
            "description": "A happy, bright child with curly hair and sparkling eyes"
        }

        response = await client.post(f"{API_BASE}/generate-image", json=payload)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Image generated successfully!")
                print(f"Image URL: {data['image_url']}")
            else:
                print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ API request failed: {response.status_code}")

        print("\n" + "="*60)

        # Test 2: Generate age progression
        print("2. Testing age progression...")

        payload = {
            "base_image_prompt": "A portrait of a happy child named Emma. Bright child with curly hair and sparkling eyes. High quality, professional portrait.",
            "child_name": "Emma",
            "ages": [3, 6, 10]
        }

        response = await client.post(f"{API_BASE}/generate-age-progression", json=payload)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Age progression generated successfully!")
                for img in data.get("age_progression_images", []):
                    print(f"Age {img['age']}: {img['image_url']}")
            else:
                print(f"❌ Generation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ API request failed: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_image_generation())