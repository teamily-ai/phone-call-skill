---
name: phone-call
description: Use this skill when the user wants to make a phone call, initiate automated calls, or have AI agents call someone. Works with fluents.ai platform to create phone agents, execute calls, and understand conversation results.
---

# Phone Call Skill

An AI skill that enables automated phone calling functionality through the fluents.ai platform.

## When to Use This Skill

Use this skill when the user wants to:
- Make a phone call to someone
- Create an automated phone agent
- Conduct batch phone calls
- Have an AI agent communicate via phone
- Retrieve and analyze call transcripts

## Workflow

### 1. Identify Phone Call Intent

Trigger this skill when the user expresses intentions like:
- "Call [person/number]"
- "Make a phone call to..."
- "I need to contact [someone]"
- "Call the client to confirm..."

### 2. Gather Required Information

Before making the call, collect:
- **Phone number**: Target contact's phone number
- **Call purpose**: Why this call is being made
- **Expected content**: What to say/confirm during the call
- **Language**: Language to use (English, Chinese, etc.)
- **Voice style**: Optional - formal, friendly, professional, etc.

### 3. Create Fluents.ai Phone Agent

Use the fluents.ai API to create a dedicated phone agent:

```bash
# Call the agent creation script
python scripts/create_agent.py \
  --purpose "Call purpose" \
  --language "en-US" \
  --voice-style "professional"
```

Required API endpoint (reference):
- `POST /api/agents` - Create phone agent
- Parameters: conversation script, voice configuration, language settings, etc.

### 4. Execute Phone Call

Use the created agent to make the actual call:

```bash
# Call the dialing script
python scripts/make_call.py \
  --agent-id "agent_xxx" \
  --phone-number "+1234567890" \
  --callback-url "https://your-webhook.com/callback"
```

Required API endpoint (reference):
- `POST /api/calls` - Initiate call
- Parameters: agent ID, target number, callback URL, etc.

### 5. Understand Call Content

After the call completes, retrieve and analyze the call records:

```bash
# Get call results
python scripts/get_call_result.py \
  --call-id "call_xxx"
```

Required API endpoints (reference):
- `GET /api/calls/{call_id}` - Get call details
- `GET /api/calls/{call_id}/transcript` - Get call transcript
- `GET /api/calls/{call_id}/analysis` - Get AI analysis results

### 6. Report Results to User

Organize and report call results to the user:
- Whether the call was answered
- Call duration
- Conversation summary
- Key information extracted
- Suggested follow-up actions

## Environment Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file:

```env
FLUENTS_API_KEY=your_api_key_here
FLUENTS_API_URL=https://api.fluents.ai
WEBHOOK_URL=https://your-webhook.com/callback
```

### 3. Test Connection

```bash
python scripts/test_connection.py
```

## API Documentation

For detailed fluents.ai API documentation, see:
- `references/fluents_api.md` - Complete API documentation
- `references/examples.md` - Usage examples

## Security Considerations

1. **Privacy Protection**: Ensure you have permission to call the target number
2. **Compliance**: Follow local telemarketing and anti-harassment regulations
3. **Key Security**: Never commit API keys to version control
4. **Log Management**: Properly manage call records with attention to data security

## Usage Examples

### Example 1: Simple Call

User: "Call 13800138000 to confirm tomorrow's 3 PM meeting"

Claude will:
1. Identify the phone call intent
2. Extract information (number: 13800138000, purpose: confirm meeting)
3. Create agent and set conversation script
4. Make the call
5. Wait for call completion
6. Return result: "Called 13800138000, they confirmed attendance at tomorrow's 3 PM meeting"

### Example 2: Complex Conversation

User: "Call the customer to gather product feedback"

Claude will:
1. Ask for customer's phone number
2. Create agent with open-ended conversation capabilities
3. Set conversation guidelines (ask about product experience, collect feedback)
4. Make the call and conduct conversation
5. AI analyzes conversation content
6. Provide structured feedback report

## Troubleshooting

### Issue: Cannot connect to fluents.ai API
- Check if API key is correct
- Verify network connection
- Check API service status

### Issue: Call not answered
- Confirm phone number format is correct (including country code)
- Check if recipient is in service area
- Review call logs for details

### Issue: Speech recognition inaccurate
- Check if language settings are correct
- Adjust voice clarity parameters
- Consider environmental noise factors

## Technical Support

- fluents.ai website: https://fluents.ai
- API documentation: See `references/` directory
- Report issues: Submit a GitHub Issue

## License

MIT License - See LICENSE file for details
