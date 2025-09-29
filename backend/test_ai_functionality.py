#!/usr/bin/env python3
"""
Quick test to verify if the AI agent functionality is working vs placeholder responses
"""

import requests
import json

BASE_URL = "https://8001-ia0ee7e4rjy1vzrlgo9b0.e2b.app"

def test_ai_vs_placeholder():
    """Test if we're getting real AI responses or just placeholders"""

    print("🧠 Testing AI Agent vs Placeholder Responses")
    print("=" * 50)

    # Test name generation with specific descriptions
    descriptions = [
        "A child who loves mathematics and solving puzzles",
        "A very artistic child who paints and draws all day",
        "An adventurous child who loves climbing trees and exploring"
    ]

    names_generated = []

    for i, description in enumerate(descriptions, 1):
        print(f"\nTest {i}: {description}")

        try:
            response = requests.post(
                f"{BASE_URL}/api/generate-name",
                json={"description": description},
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("suggested_names"):
                    # Clean up the suggested names (remove markdown formatting)
                    clean_names = []
                    for name in data["suggested_names"]:
                        clean_name = name.replace('"', '').replace('`', '').strip()
                        if clean_name and not clean_name.startswith('{') and not clean_name.startswith('['):
                            clean_names.append(clean_name)

                    names_generated.extend(clean_names[:3])  # Take first 3 names
                    print(f"✅ Names: {clean_names[:3]}")

                    # Check if explanation seems AI-generated
                    explanation = data.get("explanation", "")
                    if len(explanation) > 100 and "based on" in explanation.lower():
                        print(f"✅ AI-generated explanation (length: {len(explanation)} chars)")
                    else:
                        print(f"⚠️  Short explanation (length: {len(explanation)} chars)")
                else:
                    print("❌ No names in response")
            else:
                print(f"❌ HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Analyze uniqueness and variety
    print(f"\n📊 ANALYSIS:")
    print("=" * 50)
    print(f"Total names generated: {len(names_generated)}")
    print(f"Unique names: {len(set(names_generated))}")
    print(f"Variety score: {len(set(names_generated)) / max(len(names_generated), 1) * 100:.1f}%")

    if len(set(names_generated)) > len(names_generated) * 0.7:
        print("✅ Good name variety - likely AI-generated")
    else:
        print("⚠️  Low variety - might be using fixed responses")

    print(f"\nGenerated names: {sorted(set(names_generated))}")

if __name__ == "__main__":
    test_ai_vs_placeholder()