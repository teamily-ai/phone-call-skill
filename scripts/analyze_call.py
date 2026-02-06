#!/usr/bin/env python3
"""
Intelligently analyze phone call results and provide actionable insights
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv
import json
import re

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
        return None


def calculate_duration(call_data):
    """Calculate call duration in seconds"""
    start = float(call_data.get('start_time', 0))
    end = float(call_data.get('end_time', 0))
    return int(end - start) if end > 0 else 0


def analyze_transcript(transcript):
    """Analyze transcript to extract insights"""
    if not transcript or transcript.strip() == "":
        return {
            "turns": 0,
            "bot_turns": 0,
            "human_turns": 0,
            "keywords": [],
            "has_confirmation": False,
            "is_one_sided": True
        }

    # Parse transcript lines
    lines = transcript.strip().split('\n')
    bot_turns = 0
    human_turns = 0
    keywords = []
    has_confirmation = False

    for line in lines:
        if '[' in line and ']' in line:
            if 'BOT:' in line:
                bot_turns += 1
                # Check for confirmation keywords
                if re.search(r'\b(confirm|confirmed|reservation|booked|set|scheduled)\b', line, re.I):
                    has_confirmation = True
                    keywords.append('confirmation')
            elif 'HUMAN:' in line:
                human_turns += 1

    return {
        "turns": len(lines),
        "bot_turns": bot_turns,
        "human_turns": human_turns,
        "keywords": keywords,
        "has_confirmation": has_confirmation,
        "is_one_sided": human_turns == 0 or bot_turns == 0
    }


def determine_success(call_data, transcript_analysis, duration):
    """
    Determine if the call successfully completed its objective
    Returns: (is_success, confidence, reason)
    """
    status = call_data.get('status')
    stage_outcome = call_data.get('stage_outcome')

    # Obvious failures
    if duration < 20:
        return False, 0.95, "Call too short (< 20 seconds) - likely immediate hangup"

    if status != 'ended':
        return False, 0.9, f"Call status: {status} (not properly ended)"

    if transcript_analysis['is_one_sided']:
        if transcript_analysis['bot_turns'] > 0 and transcript_analysis['human_turns'] == 0:
            return False, 0.85, "No human responses detected - one-sided conversation"
        elif transcript_analysis['human_turns'] > 0 and transcript_analysis['bot_turns'] <= 1:
            return False, 0.85, "Bot only said greeting - conversation not completed"

    # Check for confirmation
    if transcript_analysis['has_confirmation']:
        return True, 0.8, "Confirmation keywords detected in conversation"

    # Check conversation length and turns
    if duration > 60 and transcript_analysis['human_turns'] >= 2:
        return True, 0.7, "Meaningful conversation detected (60+ seconds, multiple exchanges)"

    # Uncertain cases
    if duration >= 30 and transcript_analysis['human_turns'] >= 1:
        return None, 0.5, "Unclear - short conversation with minimal exchange"

    return False, 0.6, "No clear success indicators"


def identify_failure_cause(call_data, transcript_analysis, duration):
    """Identify the specific cause of failure"""
    stage_outcome = call_data.get('stage_outcome')

    if duration < 15:
        return "immediate_hangup", "Recipient hung up immediately (possibly recognized as robocall)"

    if transcript_analysis['bot_turns'] <= 1 and duration < 30:
        return "bot_stalled", "Bot only spoke once and call ended - likely a response/recognition issue"

    if transcript_analysis['human_turns'] == 0:
        return "no_human_response", "No human responses detected - recognition failure or silent line"

    if stage_outcome == "human_disconnected" and not transcript_analysis['has_confirmation']:
        return "task_incomplete", "Human hung up before task completion"

    return "unknown", "Failure cause unclear from available data"


def suggest_optimizations(failure_cause, call_data, duration):
    """Suggest specific optimizations based on failure analysis"""
    suggestions = []

    agent = call_data.get('agent', {})

    if failure_cause == "immediate_hangup":
        suggestions.extend([
            "⏰ Wait 30+ minutes before retrying (avoid spam detection)",
            "🎤 Consider using a different voice (currently: {})".format(
                agent.get('voice', {}).get('label', 'Unknown')
            ),
            "💬 Make opening message more human-like and natural",
            "📞 Verify number is correct and not on DNC list"
        ])

    elif failure_cause == "bot_stalled":
        suggestions.extend([
            "⏱️ Increase idle_time_seconds (current: {})".format(
                agent.get('idle_time_seconds', 'Not set')
            ),
            "🎯 Set endpointing_sensitivity to 'relaxed'",
            "✅ Enable ask_if_human_present_on_idle",
            "🔊 Enable noise_suppression"
        ])

    elif failure_cause == "no_human_response":
        suggestions.extend([
            "🎙️ Check if noise_suppression is enabled",
            "📡 Consider using better transcriber (Deepgram, AssemblyAI)",
            "⏰ Add initial_message_delay: 2000 (wait 2s before speaking)",
            "🔊 Adjust conversation_speed (try 0.9 or 1.1)"
        ])

    elif failure_cause == "task_incomplete":
        suggestions.extend([
            "📝 Improve prompt with explicit completion criteria",
            "⚠️ Add 'DO NOT HANG UP until [specific condition]' to prompt",
            "✅ List all required steps in prompt",
            "🔄 Add confirmation step at the end"
        ])

    # General suggestions
    if agent.get('llm_temperature', 0) > 0.7:
        suggestions.append("🎲 Lower llm_temperature to 0.5 for more consistent behavior")

    if not agent.get('noise_suppression'):
        suggestions.append("🔇 Enable noise_suppression: true")

    return suggestions


def generate_report(call_data, format='text'):
    """Generate comprehensive analysis report"""
    duration = calculate_duration(call_data)
    transcript = call_data.get('transcript', '')
    transcript_analysis = analyze_transcript(transcript)

    is_success, confidence, reason = determine_success(call_data, transcript_analysis, duration)

    report = {
        "call_id": call_data.get('id'),
        "duration_seconds": duration,
        "status": call_data.get('status'),
        "stage": call_data.get('stage'),
        "stage_outcome": call_data.get('stage_outcome'),
        "transcript_analysis": transcript_analysis,
        "success": is_success,
        "confidence": confidence,
        "reason": reason,
        "transcript": transcript
    }

    if is_success is False:
        failure_cause, cause_detail = identify_failure_cause(call_data, transcript_analysis, duration)
        report['failure_cause'] = failure_cause
        report['failure_detail'] = cause_detail
        report['optimizations'] = suggest_optimizations(failure_cause, call_data, duration)

    if format == 'json':
        return json.dumps(report, indent=2)

    # Text format
    output = []
    output.append("=" * 70)
    output.append("INTELLIGENT CALL ANALYSIS")
    output.append("=" * 70)
    output.append(f"Call ID: {report['call_id']}")
    output.append(f"Duration: {duration} seconds")
    output.append(f"Status: {report['status']}")
    output.append(f"Outcome: {report['stage_outcome']}")
    output.append("")

    # Success/Failure
    output.append("=" * 70)
    if is_success:
        output.append("✅ TASK SUCCESSFUL")
        output.append(f"Confidence: {int(confidence * 100)}%")
        output.append(f"Reason: {reason}")
    elif is_success is False:
        output.append("❌ TASK FAILED")
        output.append(f"Confidence: {int(confidence * 100)}%")
        output.append(f"Reason: {reason}")
        output.append("")
        output.append(f"Failure Type: {report['failure_cause']}")
        output.append(f"Details: {report['failure_detail']}")
    else:
        output.append("❓ UNCLEAR RESULT")
        output.append(f"Confidence: {int(confidence * 100)}%")
        output.append(f"Reason: {reason}")

    output.append("")

    # Transcript Analysis
    output.append("=" * 70)
    output.append("CONVERSATION ANALYSIS")
    output.append("=" * 70)
    output.append(f"Total exchanges: {transcript_analysis['turns']}")
    output.append(f"Bot spoke: {transcript_analysis['bot_turns']} times")
    output.append(f"Human responded: {transcript_analysis['human_turns']} times")
    output.append(f"Confirmation detected: {'Yes' if transcript_analysis['has_confirmation'] else 'No'}")
    output.append(f"One-sided: {'Yes' if transcript_analysis['is_one_sided'] else 'No'}")
    output.append("")

    # Transcript
    output.append("=" * 70)
    output.append("TRANSCRIPT")
    output.append("=" * 70)
    if transcript:
        output.append(transcript)
    else:
        output.append("(No transcript available)")
    output.append("")

    # Optimizations
    if 'optimizations' in report:
        output.append("=" * 70)
        output.append("RECOMMENDED OPTIMIZATIONS")
        output.append("=" * 70)
        for opt in report['optimizations']:
            output.append(f"  {opt}")
        output.append("")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description="Intelligently analyze phone call results")
    parser.add_argument("--call-id", required=True, help="Call ID to analyze")
    parser.add_argument("--format", choices=['text', 'json'], default='text',
                       help="Output format (default: text)")

    args = parser.parse_args()

    call_data = get_call_details(args.call_id)
    if not call_data:
        sys.exit(1)

    report = generate_report(call_data, format=args.format)
    print(report)


if __name__ == "__main__":
    main()
