# Fluents.ai API Reference

This document provides a reference for the fluents.ai API endpoints used in this skill.

## Base URL

```
https://api.fluents.ai
```

## Authentication

All API requests require Bearer token authentication.

```bash
Authorization: Bearer YOUR_API_KEY
```

Get your API key from: https://app.fluents.ai/settings/api-keys

---

## Agents API

### Create Agent

Create a new phone agent with specified configuration.

**Endpoint:** `POST /v1/agents/create`

**Request Body:**
```json
{
  "name": "string",
  "language": "en",
  "initial_message": "Hello, how can I help you today?",
  "prompt": {
    "text": "You are a helpful phone assistant..."
  },
  "actions": [],
  "voice": {
    "provider": "elevenlabs",
    "voice_id": "optional_voice_id"
  },
  "enable_recording": true,
  "interrupt_sensitivity": "high",
  "endpointing_sensitivity": "auto"
}
```

**Required Fields:**
- `prompt` (PromptDto): System prompt for agent behavior
- `actions` (array): Array of actions the agent can perform
- `voice` (object): Voice configuration

**Optional Fields:**
- `name`: Agent name
- `language`: Language code (en, es, de, hi, pt, fr, nl, id, it, ja, ko)
- `initial_message`: Greeting message
- `initial_message_delay`: Delay in milliseconds
- `conversation_speed`: Speed multiplier
- `interrupt_sensitivity`: "low" or "high"
- `endpointing_sensitivity`: "auto", "relaxed", or "sensitive"
- `enable_recording`: Boolean to enable call recording
- `noise_suppression`: Boolean to enable noise suppression
- `idle_time_seconds`: Timeout setting
- `call_duration_sec`: Maximum call length
- `webhook`: Webhook configuration for events

**Response (201 Created):**
```json
{
  "id": "agent_uuid",
  "user_id": "user_uuid",
  "name": "Agent Name",
  "language": "en",
  "prompt": {...},
  "actions": [...],
  "voice": {...}
}
```

### Get Agent

Retrieve agent details by ID.

**Endpoint:** `GET /v1/agents?id={agent_id}`

**Response (200 OK):**
Returns complete agent configuration.

---

## Calls API

### Create Call

Initiate an outbound phone call.

**Endpoint:** `POST /v1/calls/create`

**Request Body:**
```json
{
  "to_number": "+1234567890",
  "from_number": "+0987654321",
  "agent_phone_number": "+0987654321",
  "agent": {
    "id": "agent_uuid",
    ...
  },
  "telephony_provider": {
    "name": "twilio"
  },
  "context": {},
  "telephony_params": {},
  "is_outgoing": true,
  "run_do_not_call_detection": false
}
```

**Required Fields:**
- `to_number`: Destination phone number with country code
- `from_number`: Caller ID number with country code
- `agent_phone_number`: Agent's phone number
- `agent`: Complete agent object
- `telephony_provider`: Provider configuration
- `context`: Call context data
- `telephony_params`: Telephony-specific parameters

**Optional Fields:**
- `human_detection_result`: "human" or "no_human"
- `do_not_call_result`: Boolean
- `telephony_id`: Unique identifier from provider
- `hipaa_compliant`: Boolean
- `on_no_human_answer`: "continue" or "hangup"
- `run_do_not_call_detection`: Boolean
- `is_outgoing`: Boolean

**Response (201 Created):**
```json
{
  "id": "call_uuid",
  "user_id": "user_uuid",
  "status": "not_started",
  "to_number": "+1234567890",
  "from_number": "+0987654321",
  "start_time": "2026-01-01T00:00:00Z",
  "recording_available": false
}
```

### Get Call

Retrieve call details and transcript.

**Endpoint:** `GET /v1/calls?id={call_id}`

**Response (200 OK):**
```json
{
  "id": "call_uuid",
  "user_id": "user_uuid",
  "status": "ended",
  "stage": "picked_up",
  "stage_outcome": "human_disconnected",
  "to_number": "+1234567890",
  "from_number": "+0987654321",
  "start_time": "2026-01-01T00:00:00Z",
  "end_time": "2026-01-01T00:05:00Z",
  "recording_available": true,
  "transcript": "Full conversation transcript...",
  "human_detection_result": "human",
  "do_not_call_result": false,
  "error_message": null,
  "errors": []
}
```

**Status Values:**
- `not_started`: Call has not begun
- `in_progress`: Call is ongoing
- `error`: Call encountered an error
- `ended`: Call has completed

**Stage Values:**
- `created`: Call has been created
- `picked_up`: Call was answered
- `transfer_started`: Transfer initiated
- `transfer_successful`: Transfer completed

**Stage Outcome Values:**
- `human_unanswered`: No one picked up
- `call_did_not_connect`: Connection failed
- `human_disconnected`: Human hung up
- `bot_disconnected`: Bot ended the call
- `transfer_unanswered`: Transfer not answered
- `transfer_disconnected`: Transfer ended

### Get Recording

Download call recording as MP3.

**Endpoint:** `GET /v1/calls/recording?id={call_id}`

**Response (200 OK):**
Returns MP3 audio file as binary data.

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "message": "Error description",
  "error": "BadRequest",
  "statusCode": 400
}
```

**404 Not Found:**
```json
{
  "message": "Resource not found",
  "error": "NotFound",
  "statusCode": 404
}
```

---

## Rate Limits

Check the Fluents.ai documentation for current rate limits.

## Support

For API support, contact: support@fluents.ai

## Additional Resources

- Official Documentation: https://docs.fluents.ai
- API Reference: https://docs.fluents.ai/api-reference
- Dashboard: https://app.fluents.ai
