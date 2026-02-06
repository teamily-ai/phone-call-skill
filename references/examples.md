# Usage Examples

This document provides practical examples of using the phone call skill.

## Example 1: Simple Confirmation Call

Make a quick call to confirm an appointment.

### Step 1: Create the Agent

```bash
python scripts/create_agent.py \
  --name "Appointment Confirmation Agent" \
  --prompt "You are calling to confirm an appointment. Ask if the person can still make their appointment tomorrow at 3 PM. Be polite and brief." \
  --language "en" \
  --initial-message "Hello, I'm calling to confirm your appointment tomorrow."
```

**Output:**
```
✓ Agent created successfully
  Agent ID: abc123-def456-ghi789
  Name: Appointment Confirmation Agent
  Language: en

Agent ID: abc123-def456-ghi789
```

### Step 2: Make the Call

```bash
python scripts/make_call.py \
  --agent-id "abc123-def456-ghi789" \
  --to-number "+13105551234" \
  --from-number "+13105559999"
```

**Output:**
```
Fetching agent details for: abc123-def456-ghi789
✓ Call initiated successfully
  Call ID: call-xyz789
  Status: not_started
  From: +13105559999
  To: +13105551234

Call ID: call-xyz789
```

### Step 3: Get the Results

```bash
# Wait a few minutes for the call to complete, then:
python scripts/get_call_result.py --call-id "call-xyz789"
```

**Output:**
```
Retrieving results for call: call-xyz789

============================================================
CALL DETAILS
============================================================
Call ID: call-xyz789
Status: ended
Stage: picked_up
Stage Outcome: human_disconnected
From: +13105559999
To: +13105551234
Outgoing: Yes
Started: 2026-02-06T10:30:00Z
Ended: 2026-02-06T10:32:15Z
Human Detected: human
Recording Available: Yes

============================================================
TRANSCRIPT
============================================================
Agent: Hello, I'm calling to confirm your appointment tomorrow.
Human: Yes, who is this?
Agent: This is a reminder call about your appointment tomorrow at 3 PM. Can you still make it?
Human: Oh yes, I'll be there. Thanks!
Agent: Great! We'll see you tomorrow at 3 PM. Have a nice day!
Human: You too, bye.
```

### Step 4: Download the Recording (Optional)

```bash
python scripts/get_recording.py \
  --call-id "call-xyz789" \
  --output "confirmation_call.mp3"
```

---

## Example 2: Customer Feedback Call

Conduct a more open-ended conversation to gather feedback.

### Step 1: Create a Conversational Agent

```bash
python scripts/create_agent.py \
  --name "Customer Feedback Agent" \
  --prompt "You are conducting a customer satisfaction survey. Ask the customer about their recent purchase experience. Be friendly, listen actively, and ask follow-up questions. Keep the conversation under 5 minutes." \
  --language "en" \
  --initial-message "Hi! I'm calling from our customer service team to hear about your recent experience with us."
```

### Step 2: Make the Call with Context

```bash
python scripts/make_call.py \
  --agent-id "feedback-agent-id" \
  --to-number "+14155551234" \
  --from-number "+14155559999" \
  --context '{"customer_name": "John", "order_id": "ORD-12345", "product": "Widget Pro"}'
```

### Step 3: Retrieve Detailed Results

```bash
python scripts/get_call_result.py \
  --call-id "call-feedback-123" \
  --verbose
```

---

## Example 3: Batch Calls

Make multiple calls in sequence.

### Create the Agent Once

```bash
python scripts/create_agent.py \
  --name "Reminder Agent" \
  --prompt "You are calling to remind people about an event tomorrow. Keep it brief." \
  --initial-message "Hello, this is a reminder about tomorrow's event." \
  > agent_output.txt

# Extract agent ID
AGENT_ID=$(grep "Agent ID:" agent_output.txt | tail -1 | awk '{print $3}')
```

### Loop Through Contact List

```bash
#!/bin/bash

# List of phone numbers to call
numbers=(
  "+13105551111"
  "+13105552222"
  "+13105553333"
)

for number in "${numbers[@]}"; do
  echo "Calling $number..."
  python scripts/make_call.py \
    --agent-id "$AGENT_ID" \
    --to-number "$number" \
    --from-number "+13105559999"

  # Wait a bit between calls
  sleep 60
done
```

---

## Example 4: Using Python Directly

Instead of command-line scripts, you can import and use the functions directly:

```python
#!/usr/bin/env python3
import sys
import os

# Add scripts directory to path
sys.path.append('scripts')

from create_agent import create_agent
from make_call import make_call
from get_call_result import get_call_details

# Create agent
agent = create_agent(
    name="My Agent",
    prompt_text="You are a helpful assistant.",
    language="en"
)

agent_id = agent['id']
print(f"Created agent: {agent_id}")

# Make call
call = make_call(
    agent_id=agent_id,
    to_number="+13105551234",
    from_number="+13105559999"
)

call_id = call['id']
print(f"Initiated call: {call_id}")

# Wait for call to complete (in real usage, use webhooks or polling)
import time
time.sleep(300)  # 5 minutes

# Get results
result = get_call_details(call_id)
print(f"Call status: {result['status']}")
print(f"Transcript: {result.get('transcript', 'N/A')}")
```

---

## Example 5: Multi-Language Support

Create agents for different languages:

### Spanish Agent

```bash
python scripts/create_agent.py \
  --name "Agente Español" \
  --prompt "Eres un asistente telefónico amable. Ayuda al cliente con sus preguntas." \
  --language "es" \
  --initial-message "Hola, ¿cómo puedo ayudarte hoy?"
```

### Chinese Agent

```bash
python scripts/create_agent.py \
  --name "中文客服" \
  --prompt "你是一个友好的电话助理。帮助客户解答问题。" \
  --language "zh" \
  --initial-message "你好，我能帮你什么？"
```

---

## Error Handling

### Check Call Status

```python
import time
from scripts.get_call_result import get_call_details

def wait_for_call_completion(call_id, max_wait=600, poll_interval=30):
    """Wait for call to complete"""
    elapsed = 0

    while elapsed < max_wait:
        call = get_call_details(call_id)
        status = call.get('status')

        if status == 'ended':
            return call
        elif status == 'error':
            print(f"Call failed: {call.get('error_message')}")
            return call

        time.sleep(poll_interval)
        elapsed += poll_interval

    print("Timeout waiting for call to complete")
    return None

# Usage
call_result = wait_for_call_completion("call-xyz789")
if call_result and call_result['status'] == 'ended':
    print("Call completed successfully!")
```

---

## Best Practices

1. **Test with Your Own Number First**: Before calling customers, test the agent by calling yourself.

2. **Use Webhooks**: For production use, set up webhooks instead of polling for results.

3. **Handle Time Zones**: Make sure to call during appropriate hours for the recipient's time zone.

4. **Provide Context**: Use the `context` parameter to give the agent relevant information about the call.

5. **Keep Prompts Clear**: Write clear, concise prompts that tell the agent exactly what to do.

6. **Monitor Recordings**: Regularly review call recordings to improve agent prompts.

7. **Respect Do Not Call Lists**: Enable `run_do_not_call_detection` for compliance.

---

## Troubleshooting

### Call Not Connecting

If calls aren't connecting:
- Verify phone numbers include country code (e.g., +1 for US)
- Check that your Fluents.ai account has a valid telephony provider configured
- Ensure the `from_number` is a number you own or have access to

### Poor Conversation Quality

If the agent doesn't respond well:
- Refine the prompt to be more specific
- Adjust `interrupt_sensitivity` if the agent interrupts too much or too little
- Try different `endpointing_sensitivity` settings

### Recording Not Available

If recording is not available:
- Check that `enable_recording` was set to `true` when creating the agent
- Wait longer - recordings may take a few minutes to process
- Verify the call actually completed successfully

---

For more examples and updates, check the [GitHub repository](https://github.com/your-username/phone-call-skill).
