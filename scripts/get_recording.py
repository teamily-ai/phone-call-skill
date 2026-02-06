#!/usr/bin/env python3
"""
Download call recording from fluents.ai
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

FLUENTS_API_KEY = os.getenv("FLUENTS_API_KEY")
FLUENTS_API_URL = os.getenv("FLUENTS_API_URL", "https://api.fluents.ai")


def get_recording(call_id: str, output_file: str = None):
    """
    Download call recording

    Args:
        call_id: The call ID
        output_file: Path to save the recording (default: recording_{call_id}.mp3)

    Returns:
        str: Path to the saved recording file
    """

    if not FLUENTS_API_KEY:
        raise ValueError("FLUENTS_API_KEY not found in environment variables")

    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}"
    }

    # Default output filename
    if not output_file:
        output_file = f"recording_{call_id}.mp3"

    try:
        print(f"Downloading recording for call: {call_id}")

        response = requests.get(
            f"{FLUENTS_API_URL}/v1/calls/recording",
            params={"id": call_id},
            headers=headers,
            timeout=60,
            stream=True
        )
        response.raise_for_status()

        # Save the recording
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = os.path.getsize(output_file)
        print(f"✓ Recording downloaded successfully")
        print(f"  File: {output_file}")
        print(f"  Size: {file_size / 1024:.2f} KB")

        return output_file

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to download recording: {e}", file=sys.stderr)
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Download call recording from fluents.ai")
    parser.add_argument("--call-id", required=True, help="Call ID")
    parser.add_argument("--output", "-o", help="Output file path (default: recording_{call_id}.mp3)")

    args = parser.parse_args()

    recording_path = get_recording(
        call_id=args.call_id,
        output_file=args.output
    )

    print(f"\nRecording saved to: {recording_path}")


if __name__ == "__main__":
    main()
