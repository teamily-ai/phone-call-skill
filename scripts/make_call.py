#!/usr/bin/env python3
"""
Make a phone call using the fluents.ai API
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

FLUENTS_API_KEY = os.getenv("FLUENTS_API_KEY")
FLUENTS_API_URL = os.getenv("FLUENTS_API_URL", "https://api.fluents.ai")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def get_agent(agent_id: str):
    """Retrieve agent details"""
    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"{FLUENTS_API_URL}/v1/agents",
        params={"id": agent_id},
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def make_call(
    agent_id: str,
    to_number: str,
    from_number: str,
    telephony_provider: str = "twilio",
    context: dict = None
):
    """
    Initiate a phone call with the specified agent

    Args:
        agent_id: The ID of the phone agent to use
        to_number: Target phone number (with country code, e.g., +1234567890)
        from_number: Caller ID number (with country code, e.g., +0987654321)
        telephony_provider: Telephony provider name (default: twilio)
        context: Optional context data for the call

    Returns:
        dict: Call initiation response with call_id
    """

    if not FLUENTS_API_KEY:
        raise ValueError("FLUENTS_API_KEY not found in environment variables")

    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    # Get agent details
    print(f"Fetching agent details for: {agent_id}")
    agent = get_agent(agent_id)

    # Construct the payload according to fluents.ai API spec
    payload = {
        "to_number": to_number,
        "from_number": from_number,
        "agent_phone_number": from_number,
        "agent": agent,
        "telephony_provider": {
            "name": telephony_provider
        },
        "context": context or {},
        "telephony_params": {},
        "is_outgoing": True,
        "run_do_not_call_detection": False
    }

    try:
        response = requests.post(
            f"{FLUENTS_API_URL}/v1/calls/create",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        print(f"✓ Call initiated successfully")
        print(f"  Call ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  From: {from_number}")
        print(f"  To: {to_number}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to initiate call: {e}", file=sys.stderr)
        if hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Make a phone call with fluents.ai")
    parser.add_argument("--agent-id", required=True, help="Phone agent ID")
    parser.add_argument("--to-number", required=True, help="Target phone number with country code (e.g., +1234567890)")
    parser.add_argument("--from-number", required=True, help="Caller ID number with country code (e.g., +0987654321)")
    parser.add_argument("--telephony-provider", default="twilio", help="Telephony provider (default: twilio)")
    parser.add_argument("--context", help="JSON string with call context data")

    args = parser.parse_args()

    # Parse context if provided
    context = None
    if args.context:
        import json
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            print("Warning: Invalid JSON for context, using empty context", file=sys.stderr)

    result = make_call(
        agent_id=args.agent_id,
        to_number=args.to_number,
        from_number=args.from_number,
        telephony_provider=args.telephony_provider,
        context=context
    )

    # Output call_id for tracking
    print(f"\nCall ID: {result.get('id')}")


if __name__ == "__main__":
    main()
