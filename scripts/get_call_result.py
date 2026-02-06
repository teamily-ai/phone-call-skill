#!/usr/bin/env python3
"""
Retrieve and analyze phone call results from fluents.ai
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


def get_call_details(call_id: str):
    """Get complete call details"""

    if not FLUENTS_API_KEY:
        raise ValueError("FLUENTS_API_KEY not found in environment variables")

    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{FLUENTS_API_URL}/v1/calls",
            params={"id": call_id},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get call details: {e}", file=sys.stderr)
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text}", file=sys.stderr)
        return None


def display_results(call_id: str, verbose: bool = False):
    """
    Retrieve and display call results

    Args:
        call_id: The call ID to retrieve
        verbose: Show all details
    """

    print(f"Retrieving results for call: {call_id}\n")

    call_data = get_call_details(call_id)
    if not call_data:
        return

    # Basic call information
    print("=" * 60)
    print("CALL DETAILS")
    print("=" * 60)
    print(f"Call ID: {call_data.get('id')}")
    print(f"Status: {call_data.get('status')}")
    print(f"Stage: {call_data.get('stage')}")
    print(f"Stage Outcome: {call_data.get('stage_outcome')}")
    print(f"From: {call_data.get('from_number')}")
    print(f"To: {call_data.get('to_number')}")
    print(f"Outgoing: {'Yes' if call_data.get('is_outgoing') else 'No'}")
    print(f"Started: {call_data.get('start_time')}")
    print(f"Ended: {call_data.get('end_time')}")

    # Human detection
    human_result = call_data.get('human_detection_result')
    if human_result:
        print(f"Human Detected: {human_result}")

    # Recording
    recording_available = call_data.get('recording_available')
    print(f"Recording Available: {'Yes' if recording_available else 'No'}")

    # Do not call detection
    dnc_result = call_data.get('do_not_call_result')
    if dnc_result is not None:
        print(f"Do Not Call: {dnc_result}")

    print()

    # Transcript
    transcript = call_data.get('transcript')
    if transcript:
        print("=" * 60)
        print("TRANSCRIPT")
        print("=" * 60)
        print(transcript)
        print()

    # Errors
    errors = call_data.get('errors', [])
    error_message = call_data.get('error_message')
    if errors or error_message:
        print("=" * 60)
        print("ERRORS")
        print("=" * 60)
        if error_message:
            print(f"Error Message: {error_message}")
        if errors:
            for error in errors:
                print(f"  • {error}")
        print()

    # Action history
    action_history = call_data.get('action_history', [])
    if action_history and verbose:
        print("=" * 60)
        print("ACTION HISTORY")
        print("=" * 60)
        for action in action_history:
            print(f"  • {action}")
        print()

    # Full data in verbose mode
    if verbose:
        print("=" * 60)
        print("FULL CALL DATA")
        print("=" * 60)
        print(json.dumps(call_data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Get phone call results from fluents.ai")
    parser.add_argument("--call-id", required=True, help="Call ID to retrieve")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all details")

    args = parser.parse_args()

    if args.json:
        # Output everything as JSON
        result = get_call_details(args.call_id)
        if result:
            print(json.dumps(result, indent=2))
    else:
        # Display formatted results
        display_results(
            call_id=args.call_id,
            verbose=args.verbose
        )


if __name__ == "__main__":
    main()
