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


def build_outbound_prompt(
    objective: str,
    key_info: dict = None,
    conversation_flow: str = None,
    tone: str = "friendly and professional",
    additional_instructions: str = None
) -> str:
    """
    Build an outbound call prompt following best practices

    This generates prompts optimized for OUTBOUND calls where the AI is the CALLER.

    Args:
        objective: What you need to accomplish (e.g., "make a dinner reservation")
        key_info: Dict of known information (e.g., {"name": "Lee", "party_size": 2})
        conversation_flow: Optional detailed conversation flow steps
        tone: Communication style (default: "friendly and professional")
        additional_instructions: Any special instructions

    Returns:
        str: Complete structured prompt for outbound calls
    """
    prompt_parts = [
        "# IDENTITY - WHO YOU ARE",
        "You are making an OUTBOUND phone call.",
        "You are the CALLER, not someone answering the phone.",
        "YOU initiated this call. THEY answered YOUR call.",
        "",
        "CRITICAL: You are NOT a receptionist or assistant answering calls.",
        "CRITICAL: You are NOT waiting for the other person to state their business.",
        "CRITICAL: You need to clearly state YOUR purpose for calling.",
        "",
        "# ROLE PROHIBITIONS - NEVER DO THESE",
        'NEVER say "How can I help you?" - YOU are the one who needs help',
        'NEVER say "Thank you for calling" - YOU are calling them',
        "NEVER wait for them to explain what they want - YOU explain what you want",
        "NEVER act like you are receiving this call - YOU are making this call",
        "",
        f"# YOUR TASK",
        f"Your goal is to {objective}.",
        "",
    ]

    # Add key information if provided
    if key_info and len(key_info) > 0:
        prompt_parts.extend([
            "# KEY INFORMATION (You already know this - don't ask for it!)",
        ])
        for key, value in key_info.items():
            prompt_parts.append(f"- {key}: {value}")
        prompt_parts.extend([
            "",
            "When they ask for this information, provide it directly.",
            'Do NOT say "let me check" - you already know this information.',
            "",
        ])

    # Add conversation flow if provided
    if conversation_flow:
        prompt_parts.extend([
            "# CONVERSATION FLOW",
            conversation_flow,
            "",
        ])

    # Add speaking style guidelines
    prompt_parts.extend([
        "# SPEAKING STYLE",
        "- Speak one short sentence at a time",
        "- Sound natural like a real person on the phone",
        "- Do NOT give long explanations or speeches",
        f"- Maintain a {tone} tone",
        "- Wait for their response after each sentence",
        "- Keep it conversational, not robotic",
        "",
    ])

    if additional_instructions:
        prompt_parts.extend([
            "# SPECIAL INSTRUCTIONS",
            additional_instructions,
            "",
        ])

    return "\n".join(prompt_parts)


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

    NOTE: For outbound calls, consider using build_outbound_prompt() instead,
    as it follows best practices to avoid identity confusion.

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
    call_type: str = "outbound",  # "outbound" or "inbound"
    role: str = None,
    objective: str = None,
    scenario_context: str = None,
    key_info: list = None,
    key_info_dict: dict = None,
    conversation_flow: str = None,
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
        call_type: "outbound" (default) or "inbound" - affects prompt generation
        role: Who the agent is (for inbound calls, e.g., "customer service representative")
        objective: What the agent needs to accomplish (e.g., "make a dinner reservation")
        scenario_context: Optional scenario context (e.g., "calling existing customers")
        key_info: List of key information to collect (for inbound)
        key_info_dict: Dict of known information (for outbound, e.g., {"name": "Lee", "party_size": 2})
        conversation_flow: Detailed conversation flow steps (for outbound)
        tone: Communication style (e.g., "friendly and professional")
        additional_instructions: Extra instructions to add to the prompt

    Returns:
        dict: Agent creation response with agent id
    """

    # If using scenario builder, generate prompt based on call type
    if objective:
        if call_type == "outbound":
            # Use outbound-optimized prompt builder (best practices)
            generated_prompt = build_outbound_prompt(
                objective=objective,
                key_info=key_info_dict,
                conversation_flow=conversation_flow,
                tone=tone or "friendly and professional",
                additional_instructions=additional_instructions
            )
            builder_type = "outbound call (best practices)"
        else:
            # Use traditional scenario builder for inbound calls
            generated_prompt = build_scenario_prompt(
                role=role or "assistant",
                objective=objective,
                scenario_context=scenario_context,
                key_info=key_info,
                tone=tone,
                additional_instructions=additional_instructions
            )
            builder_type = "inbound call (traditional)"

        # Use generated prompt unless custom prompt is provided
        if not prompt_text:
            prompt_text = generated_prompt
            print(f"📋 Building {builder_type} prompt")
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

  # OUTBOUND call - Make a restaurant reservation (RECOMMENDED - uses best practices)
  python3 scripts/create_agent.py \\
    --name "Restaurant Reservation Agent" \\
    --call-type outbound \\
    --objective "make a dinner reservation at the restaurant" \\
    --initial-message "Hi, I'd like to make a reservation for dinner tonight." \\
    --key-info-dict '{"name": "Lee (L-E-E)", "party_size": "2 people", "preferred_time": "7 PM", "phone": "310-555-1234"}' \\
    --tone "friendly and casual"

  # OUTBOUND call - Appointment confirmation with conversation flow
  python3 scripts/create_agent.py \\
    --name "Appointment Reminder" \\
    --call-type outbound \\
    --objective "confirm the customer's appointment tomorrow at 3 PM" \\
    --initial-message "Hi, this is a reminder about your appointment tomorrow." \\
    --key-info-dict '{"appointment_time": "3 PM tomorrow", "customer_name": "John"}' \\
    --conversation-flow "1. Confirm they can still make it\\n2. If yes, thank them\\n3. If no, ask for alternative time"

  # INBOUND call - Customer service (traditional scenario builder)
  python3 scripts/create_agent.py \\
    --name "Support Agent" \\
    --call-type inbound \\
    --role "customer service representative" \\
    --objective "help customers with their questions" \\
    --initial-message "Hello, how can I help you today?" \\
    --key-info "customer name,order number,issue description"

  # Use fully custom prompt (maximum control)
  python3 scripts/create_agent.py \\
    --name "Custom Agent" \\
    --prompt "You are making an OUTBOUND call TO a restaurant..." \\
    --initial-message "Hi, I'd like to make a reservation."

  # See BEST_PRACTICES.md for detailed guidance on creating effective agents
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
    parser.add_argument("--call-type", default="outbound", choices=["outbound", "inbound"],
                       help="Type of call: 'outbound' (you call them) or 'inbound' (they call you). Default: outbound")
    parser.add_argument("--role",
                       help="Who the agent is (for inbound calls, e.g., 'customer service representative')")
    parser.add_argument("--objective", required=False,
                       help="What the agent needs to accomplish (e.g., 'make a dinner reservation')")
    parser.add_argument("--scenario-context",
                       help="Optional context (e.g., 'calling existing customers who made reservations online')")
    parser.add_argument("--key-info",
                       help="[Inbound] Comma-separated list of info to collect (e.g., 'date,time,number of guests')")
    parser.add_argument("--key-info-dict",
                       help="[Outbound] JSON dict of known info (e.g., '{\"name\": \"Lee\", \"party_size\": 2}')")
    parser.add_argument("--conversation-flow",
                       help="[Outbound] Detailed conversation flow steps")
    parser.add_argument("--tone",
                       help="Communication style (e.g., 'friendly and professional')")
    parser.add_argument("--additional-instructions",
                       help="Any special instructions for the agent")

    # Traditional parameter (backward compatible)
    parser.add_argument("--prompt",
                       help="Custom system prompt (alternative to using --role + --objective)")

    args = parser.parse_args()

    # Validate parameters
    if not args.prompt and not args.objective:
        parser.error("Must provide either --prompt OR --objective")

    # Parse key_info if provided (for inbound calls)
    key_info_list = None
    if args.key_info:
        key_info_list = [info.strip() for info in args.key_info.split(',')]

    # Parse key_info_dict if provided (for outbound calls)
    import json
    key_info_dict = None
    if args.key_info_dict:
        try:
            key_info_dict = json.loads(args.key_info_dict)
        except json.JSONDecodeError as e:
            parser.error(f"Invalid JSON in --key-info-dict: {e}")

    result = create_agent(
        name=args.name,
        prompt_text=args.prompt,
        language=args.language,
        voice_id=args.voice_id,
        initial_message=args.initial_message,
        call_type=args.call_type,
        role=args.role,
        objective=args.objective,
        scenario_context=args.scenario_context,
        key_info=key_info_list,
        key_info_dict=key_info_dict,
        conversation_flow=args.conversation_flow,
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
