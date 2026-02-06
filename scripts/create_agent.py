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
    initial_message: str = None  # Auto-generated if not provided
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

    # Get default voice if not specified
    if not voice_id:
        # Use a default voice - fetch the first available voice
        try:
            voices_response = requests.get(
                f"{FLUENTS_API_URL}/v1/voices/list",
                params={"page": 1, "size": 1},
                headers={"Authorization": f"Bearer {FLUENTS_API_KEY}"},
                timeout=10
            )
            if voices_response.status_code == 200:
                voices = voices_response.json().get('items', [])
                if voices:
                    voice_id = voices[0]['id']
                    print(f"Using default voice: {voices[0].get('label', 'Unknown')}")
        except:
            pass

    if not voice_id:
        print("✗ No voice specified and couldn't fetch default voice", file=sys.stderr)
        sys.exit(1)

    # Set default initial message for OUTBOUND calls
    # Note: Caller should customize this based on their specific purpose
    if not initial_message:
        initial_message = "Hello, I'm calling regarding an important matter."
        print(f"⚠ Using default opening: \"{initial_message}\"")
        print(f"  TIP: Customize with --initial-message for better results")
        print(f"  Example: \"Hello, I'm calling to make a dinner reservation.\"")

    # Construct the payload according to fluents.ai API spec
    # IMPORTANT: Based on successful curl tests, the format must be:
    # - prompt.content (not prompt.text)
    # - voice as UUID string (not object)
    payload = {
        "name": name,
        "language": language,
        "initial_message": initial_message,
        "prompt": {
            "content": prompt_text  # ✅ FIXED: use "content" not "text"
        },
        "actions": [],
        "voice": voice_id,  # ✅ FIXED: direct UUID string, not object

        # ⚡ CRITICAL FOR OUTBOUND CALLS
        "wait_for_greeting": False,  # Agent speaks first (don't wait!)

        # ⚡ OPTIMIZED FOR QUICK RESPONSE (not speech speed!)
        "conversation_speed": 1.0,  # Normal speech speed (don't make it faster)
        "idle_time_seconds": 4,     # Quick response - only wait 4 seconds!
        "endpointing_sensitivity": "sensitive",  # Detect pauses quickly
        "initial_message_delay": 1000,  # 1s delay before speaking (natural)

        # Other settings
        "interrupt_sensitivity": "high",  # Allow natural interruptions
        "provider": "openai",
        "llm_temperature": 0.6,  # Consistent responses
        "noise_suppression": True,  # Better audio quality
        "ask_if_human_present_on_idle": False,  # Don't waste time asking
        "call_duration_sec": 300  # 5 min max
    }

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
    parser = argparse.ArgumentParser(description="Create a fluents.ai phone agent (FIXED)")
    parser.add_argument("--name", required=True, help="Name of the agent")
    parser.add_argument("--prompt", required=True, help="System prompt for agent behavior")
    parser.add_argument("--language", default="en", help="Language code (default: en)")
    parser.add_argument("--voice-id", help="Specific voice ID (will use default if not specified)")
    parser.add_argument("--initial-message",
                       help="Initial greeting (auto-generated from prompt if not provided)")

    args = parser.parse_args()

    result = create_agent(
        name=args.name,
        prompt_text=args.prompt,
        language=args.language,
        voice_id=args.voice_id,
        initial_message=args.initial_message
    )

    # Output agent_id for use in subsequent scripts
    print(f"\n✅ Agent created successfully!")
    print(f"Agent ID: {result.get('id')}")
    print(f"\nYou can now make calls with:")
    print(f"  python3 scripts/make_call_simple.py \\")
    print(f"    --agent-id \"{result.get('id')}\" \\")
    print(f"    --to-number \"+1234567890\" \\")
    print(f"    --from-number \"+15103982646\"")


if __name__ == "__main__":
    main()
