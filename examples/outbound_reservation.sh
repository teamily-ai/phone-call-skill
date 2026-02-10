#!/bin/bash
# Example: Create an outbound call agent to make a restaurant reservation
# This uses the new best practices prompt builder

python3 scripts/create_agent.py \
  --name "Restaurant Reservation - Outbound" \
  --call-type outbound \
  --objective "make a dinner reservation at the restaurant" \
  --initial-message "Hi, I'd like to make a reservation for dinner tonight." \
  --key-info-dict '{
    "name": "Lee (spelled L-E-E)",
    "party_size": "2 people",
    "preferred_time": "7:00 PM tonight",
    "backup_times": "8:00 PM or 9:00 PM",
    "phone_for_callback": "310-555-1234"
  }' \
  --conversation-flow "Step 1: State you want a reservation
Step 2: If they ask for time, say 7 PM for 2 people
Step 3: If they ask for name, say Lee (L-E-E)
Step 4: If 7 PM unavailable, ask about 8 or 9 PM
Step 5: Confirm the final time and thank them" \
  --tone "friendly and casual" \
  --additional-instructions "If they are fully booked tonight, ask about tomorrow evening at the same times."

echo ""
echo "✅ Agent created with best practices for outbound calls!"
echo ""
echo "To test the agent, use:"
echo "  python3 scripts/make_call_simple.py --agent-id <AGENT_ID> --to-number +1234567890 --from-number +15103982646"
