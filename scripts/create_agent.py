#!/usr/bin/env python3
"""
Create a phone agent using the fluents.ai API
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

FLUENTS_API_KEY = os.getenv("FLUENTS_API_KEY")
FLUENTS_API_URL = os.getenv("FLUENTS_API_URL", "https://api.fluents.ai")


def create_agent(
    name: str,
    prompt_text: str,
    language: str = "en",
    voice_provider: str = "elevenlabs",
    voice_id: str = None,
    initial_message: str = "Hello, how can I help you today?"
):
    """
    Create a phone agent with specified configuration

    Args:
        name: Name of the agent
        prompt_text: The system prompt for the agent's behavior
        language: Language code (en, es, de, hi, pt, fr, nl, id, it, ja, ko)
        voice_provider: Voice provider (elevenlabs, openai, etc.)
        voice_id: Specific voice ID to use
        initial_message: Greeting message

    Returns:
        dict: Agent creation response with agent id
    """

    if not FLUENTS_API_KEY:
        raise ValueError("FLUENTS_API_KEY not found in environment variables")

    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    # Construct the payload according to fluents.ai API spec
    payload = {
        "name": name,
        "language": language,
        "initial_message": initial_message,
        "prompt": {
            "text": prompt_text
        },
        "actions": [],  # Empty actions array for basic agent
        "voice": {
            "provider": voice_provider
        },
        "enable_recording": True,
        "interrupt_sensitivity": "high",
        "endpointing_sensitivity": "auto"
    }

    # Add voice_id if specified
    if voice_id:
        payload["voice"]["voice_id"] = voice_id

    try:
        response = requests.post(
            f"{FLUENTS_API_URL}/v1/agents/create",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        print(f"✓ Agent created successfully")
        print(f"  Agent ID: {result.get('id')}")
        print(f"  Name: {result.get('name')}")
        print(f"  Language: {result.get('language')}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to create agent: {e}", file=sys.stderr)
        if hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Create a fluents.ai phone agent")
    parser.add_argument("--name", required=True, help="Name of the agent")
    parser.add_argument("--prompt", required=True, help="System prompt for agent behavior")
    parser.add_argument("--language", default="en", help="Language code (default: en)")
    parser.add_argument("--voice-provider", default="elevenlabs", help="Voice provider (default: elevenlabs)")
    parser.add_argument("--voice-id", help="Specific voice ID to use")
    parser.add_argument("--initial-message", default="Hello, how can I help you today?",
                       help="Initial greeting message")

    args = parser.parse_args()

    result = create_agent(
        name=args.name,
        prompt_text=args.prompt,
        language=args.language,
        voice_provider=args.voice_provider,
        voice_id=args.voice_id,
        initial_message=args.initial_message
    )

    # Output agent_id for use in subsequent scripts
    print(f"\nAgent ID: {result.get('id')}")


if __name__ == "__main__":
    main()
