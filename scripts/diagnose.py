#!/usr/bin/env python3
"""
Diagnostic script to check fluents.ai setup and identify issues
"""

import os
import sys
import requests
from dotenv import load_dotenv
import json

load_dotenv()

FLUENTS_API_KEY = os.getenv("FLUENTS_API_KEY")
FLUENTS_API_URL = os.getenv("FLUENTS_API_URL", "https://api.fluents.ai")


def check_env():
    """Check environment configuration"""
    print("=" * 70)
    print("1. ENVIRONMENT CHECK")
    print("=" * 70)

    if not FLUENTS_API_KEY:
        print("✗ FLUENTS_API_KEY not set")
        return False

    print(f"✓ FLUENTS_API_KEY: {FLUENTS_API_KEY[:10]}...{FLUENTS_API_KEY[-4:]}")
    print(f"✓ FLUENTS_API_URL: {FLUENTS_API_URL}")
    return True


def check_api_connection():
    """Test API connectivity"""
    print("\n" + "=" * 70)
    print("2. API CONNECTION TEST")
    print("=" * 70)

    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{FLUENTS_API_URL}/v1/agents/list",
            params={"page": 1, "size": 1},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("✓ API connection successful")
            print(f"  Status: {response.status_code}")
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def check_agents():
    """Check available agents"""
    print("\n" + "=" * 70)
    print("3. AGENTS CHECK")
    print("=" * 70)

    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{FLUENTS_API_URL}/v1/agents/list",
            params={"page": 1, "size": 10},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        total = data.get('total', 0)
        items = data.get('items', [])

        print(f"✓ Total agents: {total}")
        if items:
            print(f"\nAvailable agents:")
            for i, agent in enumerate(items[:5], 1):
                print(f"  {i}. {agent.get('name')}")
                print(f"     ID: {agent.get('id')}")
                print(f"     Language: {agent.get('language')}")
        else:
            print("⚠ No agents found - you need to create one first")

        return len(items) > 0

    except Exception as e:
        print(f"✗ Failed to get agents: {e}")
        return False


def check_numbers():
    """Check phone numbers"""
    print("\n" + "=" * 70)
    print("4. PHONE NUMBERS CHECK")
    print("=" * 70)

    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{FLUENTS_API_URL}/v1/numbers/list",
            params={"page": 1, "size": 10},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        items = data.get('items', [])

        if items:
            print(f"✓ Found {len(items)} phone number(s):")
            for num in items:
                status = '✓ Active' if num.get('active') else '✗ Inactive'
                print(f"  {status}: {num.get('number')}")
                print(f"     Provider: {num.get('telephony_provider', 'Unknown')}")
        else:
            print("⚠ No phone numbers configured")
            print("  You need to add a phone number in fluents.ai dashboard")
            return False

        return True

    except Exception as e:
        print(f"✗ Failed to get numbers: {e}")
        return False


def check_recent_calls():
    """Check recent calls"""
    print("\n" + "=" * 70)
    print("5. RECENT CALLS")
    print("=" * 70)

    headers = {
        "Authorization": f"Bearer {FLUENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{FLUENTS_API_URL}/v1/calls/list",
            params={
                "page": 1,
                "size": 5,
                "sort_column": "start_time",
                "sort_desc": True,
                "filters": ""
            },
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        items = data.get('items', [])
        total = data.get('total', 0)

        print(f"✓ Total calls: {total}")
        if items:
            print(f"\nRecent calls:")
            for call in items[:3]:
                print(f"  • {call.get('to_number')} - {call.get('status')}")
                print(f"    ID: {call.get('id')}")
        else:
            print("  No calls yet")

        return True

    except Exception as e:
        print(f"✗ Failed to get calls: {e}")
        return False


def main():
    print("\n" + "=" * 70)
    print("FLUENTS.AI DIAGNOSTIC TOOL")
    print("=" * 70)

    results = []

    # Run all checks
    results.append(("Environment", check_env()))
    if not results[-1][1]:
        print("\n❌ Environment check failed - cannot continue")
        sys.exit(1)

    results.append(("API Connection", check_api_connection()))
    results.append(("Agents", check_agents()))
    results.append(("Phone Numbers", check_numbers()))
    results.append(("Recent Calls", check_recent_calls()))

    # Summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("\n✅ All checks passed! Your setup is ready.")
        sys.exit(0)
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
