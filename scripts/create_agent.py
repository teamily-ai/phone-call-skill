#!/usr/bin/env python3
"""
Create a phone agent using the fluents.ai API with scenario-based prompts
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

FLUENTS_API_KEY = os.getenv("FLUENTS_API_KEY")
FLUENTS_API_URL = os.getenv("FLUENTS_API_URL", "https://api.fluents.ai")


def build_scenario_prompt(
    role: str,
    objective: str,
    scenario_context: str = None,
    key_info: list = None,
    tone: str = None,
    additional_instructions: str = None
) -> str:
    """
    Build a structured prompt based on caller-defined parameters

    Args:
        role: Who you are (e.g., "restaurant reservation assistant")
        objective: What you need to accomplish (e.g., "confirm dinner reservation")
        scenario_context: Optional context about the scenario (e.g., "calling existing customers")
        key_info: List of key information to collect (e.g., ["date", "time", "number of guests"])
        tone: Communication style (e.g., "friendly and professional")
        additional_instructions: Any special instructions

    Returns:
        str: Complete structured prompt
    """
    # Build structured prompt
    prompt_parts = [
        f"# Role Definition",
        f"You are a {role}.",
        "",
    ]

    if scenario_context:
        prompt_parts.extend([
            f"# Scenario",
            f"{scenario_context}",
            "",
        ])

    prompt_parts.extend([
        f"# Objective",
        f"Your goal is to {objective}.",
        "",
    ])

    if tone:
        prompt_parts.extend([
            f"# Communication Style",
            f"Maintain a {tone} communication style.",
            "",
        ])

    if key_info and len(key_info) > 0:
        prompt_parts.extend([
            f"# Key Information",
            f"During the conversation, you need to collect or confirm the following information:",
        ])
        for info in key_info:
            prompt_parts.append(f"- {info}")
        prompt_parts.append("")

    prompt_parts.extend([
        f"# Conversation Guidelines",
        f"1. Keep it concise and clear - ask only one question at a time",
        f"2. If the customer doesn't understand, patiently repeat",
        f"3. When confirming important information, repeat it back to ensure accuracy",
        f"4. If unable to complete the task, politely explain why and offer alternatives",
        f"5. Thank the customer for their time at the end of the conversation",
    ])

    if additional_instructions:
        prompt_parts.extend([
            "",
            f"# Special Instructions",
            additional_instructions
        ])

    return "\n".join(prompt_parts)


def create_agent(
    name: str,
    prompt_text: str = None,
    language: str = "en",
    voice_provider: str = "elevenlabs",
    voice_id: str = None,
    initial_message: str = None,
    # Scenario builder parameters
    role: str = None,
    objective: str = None,
    scenario_context: str = None,
    key_info: list = None,
    tone: str = None,
    additional_instructions: str = None
):
    """
    Create a phone agent with specified configuration

    Args:
        name: Name of the agent
        prompt_text: The system prompt (if not using scenario builder)
        language: Language code (en, es, de, hi, pt, fr, nl, id, it, ja, ko)
        voice_provider: Voice provider (elevenlabs, openai, etc.)
        voice_id: Specific voice ID to use
        initial_message: Greeting message (required for outbound calls)

        # Scenario builder parameters (alternative to prompt_text):
        role: Who the agent is (e.g., "restaurant reservation assistant")
        objective: What the agent needs to accomplish (e.g., "confirm dinner reservation")
        scenario_context: Optional scenario context (e.g., "calling existing customers")
        key_info: List of key information to collect
        tone: Communication style (e.g., "friendly and professional")
        additional_instructions: Extra instructions to add to the prompt

    Returns:
        dict: Agent creation response with agent id
    """

    # If using scenario builder, generate prompt
    if role and objective:
        generated_prompt = build_scenario_prompt(
            role=role,
            objective=objective,
            scenario_context=scenario_context,
            key_info=key_info,
            tone=tone,
            additional_instructions=additional_instructions
        )
        # Use generated prompt unless custom prompt is provided
        if not prompt_text:
            prompt_text = generated_prompt
            print(f"📋 Building scenario-based prompt")
            print(f"   Role: {role}")
            print(f"   Objective: {objective}")
            print(f"\n✨ Generated Prompt:")
            print("─" * 60)
            print(prompt_text)
            print("─" * 60)

    # Error if neither scenario builder nor prompt is provided
    if not prompt_text:
        raise ValueError("Must provide either --prompt or (--role + --objective) parameters")

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

    # Validate initial_message is provided
    if not initial_message:
        raise ValueError("--initial-message is required. Please specify what the agent should say when the call connects.")

    # Construct the payload according to fluents.ai API spec
    # IMPORTANT: Based on successful curl tests, the format must be:
    # - prompt.content (not prompt.text)
    # - voice as UUID string (not object)
    # - enable_dynamic_turns: true (CRITICAL for outbound!)
    # - initial_message_delay: 0 (speak immediately!)
    payload = {
        "name": name,
        "language": language,
        "initial_message": initial_message,
        "prompt": {
            "content": prompt_text  # ✅ FIXED: use "content" not "text"
        },
        "actions": [],
        "voice": voice_id,  # ✅ FIXED: direct UUID string, not object

        # ⚡ CRITICAL FOR OUTBOUND CALLS - Based on working Agent 1 config
        "wait_for_greeting": False,  # Agent speaks first (don't wait!)
        "enable_dynamic_turns": True,  # 🔥 CRITICAL: Enables proactive speaking!
        "initial_message_delay": 0,  # 🔥 Speak IMMEDIATELY when call connects

        # Conversation settings - Proven working config from Agent 1
        "endpointing_sensitivity": "auto",  # Auto detection (not too sensitive)
        "idle_time_seconds": 7,  # Give enough time for responses
        "conversation_speed": 1.0,  # Normal speech speed
        "interrupt_sensitivity": "low",  # Less sensitive to interruptions

        # Quality settings
        "provider": "openai",
        "llm_temperature": 0,  # Deterministic responses
        "noise_suppression": False,  # Match working config
        "ask_if_human_present_on_idle": True,  # Ask if still there
        "call_duration_sec": 600,  # 10 minutes max
        "max_idle_check_count": 3  # Check 3 times before giving up
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
    parser = argparse.ArgumentParser(
        description="Create scenario-based fluents.ai phone agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:

  # Define agent by role and objective (recommended)
  python3 scripts/create_agent.py \\
    --name "Restaurant Reservation Agent" \\
    --role "restaurant reservation assistant from The Italian Kitchen" \\
    --objective "confirm the customer's dinner reservation for tonight" \\
    --initial-message "Hello, I'm calling from The Italian Kitchen to confirm your reservation." \\
    --tone "friendly and professional" \\
    --key-info "reservation time,number of guests,any dietary requirements"

  # Delivery notification example
  python3 scripts/create_agent.py \\
    --name "Delivery Agent" \\
    --role "delivery coordinator from Amazon" \\
    --objective "notify the customer that their package will arrive today" \\
    --initial-message "Hello, this is Amazon. Your package is out for delivery." \\
    --key-info "delivery time window,delivery address confirmation"

  # Use fully custom prompt (traditional way)
  python3 scripts/create_agent.py \\
    --name "My Agent" \\
    --prompt "You are a helpful assistant..." \\
    --initial-message "Hello, how can I help you?"
        """
    )

    # Basic parameters
    parser.add_argument("--name", required=True,
                       help="Agent name")
    parser.add_argument("--initial-message", required=True,
                       help="Opening message when the call connects (what the agent says first)")
    parser.add_argument("--language", default="en",
                       help="Language code (default: en)")
    parser.add_argument("--voice-id",
                       help="Specific voice ID (uses default if not specified)")

    # Scenario builder parameters (recommended way)
    parser.add_argument("--role",
                       help="Who the agent is (e.g., 'restaurant reservation assistant from Joe's Pizza')")
    parser.add_argument("--objective",
                       help="What the agent needs to accomplish (e.g., 'confirm dinner reservation')")
    parser.add_argument("--scenario-context",
                       help="Optional context (e.g., 'calling existing customers who made reservations online')")
    parser.add_argument("--key-info",
                       help="Comma-separated list of info to collect (e.g., 'date,time,number of guests')")
    parser.add_argument("--tone",
                       help="Communication style (e.g., 'friendly and professional')")
    parser.add_argument("--additional-instructions",
                       help="Any special instructions for the agent")

    # Traditional parameter (backward compatible)
    parser.add_argument("--prompt",
                       help="Custom system prompt (alternative to using --role + --objective)")

    args = parser.parse_args()

    # Validate parameters
    if not args.prompt and not (args.role and args.objective):
        parser.error("Must provide either --prompt OR (--role + --objective)")

    # Parse key_info if provided
    key_info_list = None
    if args.key_info:
        key_info_list = [info.strip() for info in args.key_info.split(',')]

    result = create_agent(
        name=args.name,
        prompt_text=args.prompt,
        language=args.language,
        voice_id=args.voice_id,
        initial_message=args.initial_message,
        role=args.role,
        objective=args.objective,
        scenario_context=args.scenario_context,
        key_info=key_info_list,
        tone=args.tone,
        additional_instructions=args.additional_instructions
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
