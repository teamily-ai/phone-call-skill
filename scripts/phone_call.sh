#!/bin/bash
#
# Phone Call Skill - Unified Entry Point
#
# This script provides a simple interface for making phone calls with AI agents.
# It handles the complete workflow: create agent → make call → analyze results.
#
# Usage:
#   ./phone_call.sh --to "+1234567890" --purpose "Make a dinner reservation for 2 at 8pm"
#   ./phone_call.sh --agent-id "xxx" --to "+1234567890"
#   ./phone_call.sh --analyze "call-id-xxx"
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(cat "$PROJECT_DIR/.env" | grep -v '^#' | xargs)
fi

# Default values
FROM_NUMBER="${FLUENTS_FROM_NUMBER:-+15103982646}"
LANGUAGE="${FLUENTS_LANGUAGE:-en}"
ACTION=""
AGENT_ID=""
TO_NUMBER=""
PURPOSE=""
CALL_ID=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --to)
            TO_NUMBER="$2"
            shift 2
            ;;
        --from)
            FROM_NUMBER="$2"
            shift 2
            ;;
        --purpose)
            PURPOSE="$2"
            shift 2
            ;;
        --agent-id)
            AGENT_ID="$2"
            ACTION="call"
            shift 2
            ;;
        --analyze)
            CALL_ID="$2"
            ACTION="analyze"
            shift 2
            ;;
        --diagnose)
            ACTION="diagnose"
            shift
            ;;
        --help|-h)
            ACTION="help"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Help message
if [ "$ACTION" == "help" ] || [ -z "$ACTION" ]; then
    cat << 'EOF'
Phone Call Skill - AI-Powered Phone Calls

USAGE:
  # Make a call (creates agent automatically)
  ./phone_call.sh --to "+1234567890" --purpose "Your call objective"

  # Make a call with existing agent
  ./phone_call.sh --agent-id "agent-xxx" --to "+1234567890"

  # Analyze a completed call
  ./phone_call.sh --analyze "call-id-xxx"

  # Diagnose your setup
  ./phone_call.sh --diagnose

OPTIONS:
  --to NUMBER         Target phone number (with country code, e.g., +1234567890)
  --from NUMBER       Caller ID number (default: configured number)
  --purpose TEXT      Purpose of the call (used to create agent)
  --agent-id ID       Use existing agent instead of creating new one
  --analyze ID        Analyze results of a completed call
  --diagnose          Check system configuration
  --help, -h          Show this help message

EXAMPLES:
  # Restaurant reservation
  ./phone_call.sh \
    --to "+16576102352" \
    --purpose "Make a dinner reservation for 2 people tonight at 8 PM. Name: John Smith, Phone: 310-555-1234"

  # Use existing agent
  ./phone_call.sh \
    --agent-id "c7c4716a-7b7c-44c8-97a7-3872a34187fe" \
    --to "+16576102352"

  # Analyze call results
  ./phone_call.sh --analyze "call-abc123"

ENVIRONMENT:
  Set these in .env file:
  - FLUENTS_API_KEY       (required)
  - FLUENTS_FROM_NUMBER   (your phone number)
  - FLUENTS_API_URL       (default: https://api.fluents.ai)

MORE INFO:
  See SKILL.md for detailed documentation
  GitHub: https://github.com/teamily-ai/phone-call-skill
EOF
    exit 0
fi

# Diagnose
if [ "$ACTION" == "diagnose" ]; then
    echo "Running diagnostics..."
    python3 "$SCRIPT_DIR/diagnose.py"
    exit $?
fi

# Analyze
if [ "$ACTION" == "analyze" ]; then
    if [ -z "$CALL_ID" ]; then
        echo "Error: --analyze requires a call ID"
        exit 1
    fi
    echo "Analyzing call: $CALL_ID"
    python3 "$SCRIPT_DIR/analyze_call.py" --call-id "$CALL_ID"
    exit $?
fi

# Make a call
if [ -z "$TO_NUMBER" ]; then
    echo "Error: --to is required"
    echo "Use --help for usage information"
    exit 1
fi

# Create agent if needed
if [ -z "$AGENT_ID" ]; then
    if [ -z "$PURPOSE" ]; then
        echo "Error: --purpose is required when creating a new agent"
        echo "Use --help for usage information"
        exit 1
    fi

    echo "=================================="
    echo "STEP 1: Creating Agent"
    echo "=================================="
    echo "Purpose: $PURPOSE"
    echo ""

    # Create agent and capture output
    AGENT_OUTPUT=$(python3 "$SCRIPT_DIR/create_agent.py" \
        --name "Auto-generated: $(date +%Y%m%d-%H%M%S)" \
        --prompt "$PURPOSE" \
        --language "$LANGUAGE" 2>&1)

    echo "$AGENT_OUTPUT"

    # Extract agent ID from output
    AGENT_ID=$(echo "$AGENT_OUTPUT" | grep "Agent ID:" | tail -1 | awk '{print $3}')

    if [ -z "$AGENT_ID" ]; then
        echo ""
        echo "Error: Failed to create agent"
        exit 1
    fi

    echo ""
    echo "✓ Agent created: $AGENT_ID"
    echo ""
fi

# Make the call
echo "=================================="
echo "STEP 2: Making Call"
echo "=================================="
echo "From: $FROM_NUMBER"
echo "To: $TO_NUMBER"
echo "Agent: $AGENT_ID"
echo ""

CALL_OUTPUT=$(python3 "$SCRIPT_DIR/make_call_simple.py" \
    --agent-id "$AGENT_ID" \
    --to-number "$TO_NUMBER" \
    --from-number "$FROM_NUMBER" 2>&1)

echo "$CALL_OUTPUT"

# Extract call ID
CALL_ID=$(echo "$CALL_OUTPUT" | grep "Call ID:" | grep -v "for tracking" | tail -1 | awk '{print $3}')

if [ -z "$CALL_ID" ]; then
    echo ""
    echo "Error: Failed to initiate call"
    exit 1
fi

echo ""
echo "✓ Call initiated: $CALL_ID"
echo ""

# Wait for call to complete
echo "=================================="
echo "STEP 3: Waiting for Call"
echo "=================================="
echo "Waiting for call to complete..."
echo "(This usually takes 30-120 seconds)"
echo ""

MAX_WAIT=300  # 5 minutes max
WAIT_TIME=0
INTERVAL=15

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    sleep $INTERVAL
    WAIT_TIME=$((WAIT_TIME + INTERVAL))

    # Check call status
    STATUS=$(python3 -c "
import requests, os, sys
headers = {'Authorization': f'Bearer {os.getenv(\"FLUENTS_API_KEY\")}'}
try:
    r = requests.get('$FLUENTS_API_URL/v1/calls', params={'id': '$CALL_ID'}, headers=headers, timeout=10)
    data = r.json()
    print(data.get('status', 'unknown'))
except:
    print('error')
" 2>/dev/null)

    echo "  Status: $STATUS (waited ${WAIT_TIME}s)"

    if [ "$STATUS" == "ended" ]; then
        echo ""
        echo "✓ Call completed!"
        break
    elif [ "$STATUS" == "error" ]; then
        echo ""
        echo "✗ Call failed"
        break
    fi
done

echo ""

# Analyze results
echo "=================================="
echo "STEP 4: Analyzing Results"
echo "=================================="
echo ""

python3 "$SCRIPT_DIR/analyze_call.py" --call-id "$CALL_ID"

echo ""
echo "=================================="
echo "COMPLETE"
echo "=================================="
echo "Call ID: $CALL_ID"
echo "Agent ID: $AGENT_ID"
echo ""
echo "To re-analyze this call later:"
echo "  ./phone_call.sh --analyze \"$CALL_ID\""
echo ""
