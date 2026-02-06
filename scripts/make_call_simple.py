#!/usr/bin/env python3
"""
Simplified make_call script - more robust and better error handling
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv
import json

load_dotenv()

FLUENTS_API_KEY = os.getenv("FLUENTS_API_KEY")
FLUENTS_API_URL = os.getenv("FLUENTS_API_URL", "https://api.fluents.ai")


def get_agent_safe(agent_id: str):
    """Safely retrieve agent details with proper error handling"""
    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print(f"[1/3] Fetching agent details: {agent_id}")
        response = requests.get(
            f"{FLUENTS_API_URL}/v1/agents",
            params={"id": agent_id},
            headers=headers,
            timeout=30
        )

        if response.status_code == 404:
            print(f"✗ Agent not found: {agent_id}", file=sys.stderr)
            print(f"  Please verify the agent ID is correct", file=sys.stderr)
            return None

        response.raise_for_status()
        agent = response.json()
        print(f"✓ Agent found: {agent.get('name', 'Unknown')}")
        return agent

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get agent: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Status: {e.response.status_code}", file=sys.stderr)
            print(f"  Response: {e.response.text[:200]}", file=sys.stderr)
        return None


def make_call_safe(
    agent_id: str,
    to_number: str,
    from_number: str,
    telephony_provider: str = "twilio",
    context: dict = None
):
    """
    Safely initiate a phone call with comprehensive error handling
    """

    if not FLUENTS_API_KEY:
        print("✗ FLUENTS_API_KEY not found in environment variables", file=sys.stderr)
        return None

    # Step 1: Get agent details
    agent = get_agent_safe(agent_id)
    if not agent:
        return None

    # Step 2: Prepare call payload
    print(f"\n[2/3] Preparing call...")
    print(f"  From: {from_number}")
    print(f"  To: {to_number}")
    print(f"  Agent: {agent.get('name', 'Unknown')}")

    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

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

    # Step 3: Make the call
    try:
        print(f"\n[3/3] Initiating call...")
        response = requests.post(
            f"{FLUENTS_API_URL}/v1/calls/create",
            json=payload,
            headers=headers,
            timeout=30
        )

        # Better error handling
        if response.status_code == 500:
            print(f"✗ Server error (500) - This might be a temporary issue", file=sys.stderr)
            print(f"  Response: {response.text[:300]}", file=sys.stderr)
            print(f"\nTroubleshooting tips:", file=sys.stderr)
            print(f"  1. Check if your telephony provider is properly configured", file=sys.stderr)
            print(f"  2. Verify your from_number is valid and active", file=sys.stderr)
            print(f"  3. Try again in a few moments", file=sys.stderr)
            return None

        response.raise_for_status()

        result = response.json()
        print(f"\n✓ Call initiated successfully!")
        print(f"  Call ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Telephony ID: {result.get('telephony_id', 'N/A')}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"\n✗ Failed to initiate call: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Status: {e.response.status_code}", file=sys.stderr)
            try:
                error_data = e.response.json()
                print(f"  Error: {json.dumps(error_data, indent=2)}", file=sys.stderr)
            except:
                print(f"  Response: {e.response.text[:300]}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Make a phone call with fluents.ai (robust version)")
    parser.add_argument("--agent-id", required=True, help="Phone agent ID")
    parser.add_argument("--to-number", required=True, help="Target phone number with country code")
    parser.add_argument("--from-number", required=True, help="Caller ID number with country code")
    parser.add_argument("--telephony-provider", default="twilio", help="Telephony provider")
    parser.add_argument("--context", help="JSON string with call context data")

    args = parser.parse_args()

    # Parse context if provided
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError as e:
            print(f"⚠ Warning: Invalid JSON for context: {e}", file=sys.stderr)
            print(f"  Using empty context", file=sys.stderr)

    result = make_call_safe(
        agent_id=args.agent_id,
        to_number=args.to_number,
        from_number=args.from_number,
        telephony_provider=args.telephony_provider,
        context=context
    )

    if result:
        print(f"\n📞 Call ID for tracking: {result.get('id')}")
        sys.exit(0)
    else:
        print(f"\n❌ Call failed - see errors above", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
