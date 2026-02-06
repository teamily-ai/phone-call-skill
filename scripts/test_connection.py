#!/usr/bin/env python3
"""
Test connection to fluents.ai API
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

FLUENTS_API_KEY = os.getenv("FLUENTS_API_KEY")
FLUENTS_API_URL = os.getenv("FLUENTS_API_URL", "https://api.fluents.ai")


def test_connection():
    """Test API connection and authentication"""

    print("Testing connection to fluents.ai API...\n")

    # Check if API key is set
    if not FLUENTS_API_KEY:
        print("✗ FLUENTS_API_KEY not found in environment variables")
        print("  Please set FLUENTS_API_KEY in your .env file")
        sys.exit(1)

    print(f"✓ API Key found")
    print(f"  API URL: {FLUENTS_API_URL}")

    # Test API connection
    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Try to list agents as a connectivity test
        response = requests.get(
            f"{FLUENTS_API_URL}/v1/agents/list",
            params={"page": 1, "size": 1},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print(f"✓ API connection successful")
            print(f"  Status: {response.status_code}")
            print(f"  API is accessible and authenticated")
            return True
        elif response.status_code == 401 or response.status_code == 403:
            print(f"✗ Authentication failed")
            print(f"  Status: {response.status_code}")
            print(f"  Please check your API key")
            return False
        else:
            print(f"⚠ Unexpected response: {response.status_code}")
            print(f"  Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"✗ Connection failed")
        print(f"  Cannot reach {FLUENTS_API_URL}")
        print(f"  Please check your internet connection")
        return False

    except requests.exceptions.Timeout:
        print(f"✗ Connection timeout")
        print(f"  The API server is not responding")
        return False

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    success = test_connection()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
