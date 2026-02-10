# Bad vs Good: Creating Outbound Call Agents

This document shows side-by-side comparisons of problematic approaches vs. best practices.

---

## Example 1: Restaurant Reservation

### ❌ BAD APPROACH - Identity Confusion

```bash
python3 scripts/create_agent.py \
  --name "Reservation Agent" \
  --call-type inbound \
  --role "restaurant reservation assistant" \
  --objective "confirm dinner reservation" \
  --initial-message "Hello, thank you for calling." \
  --key-info "customer name,party size,reservation time"
```

**Problems:**
- Using `inbound` for a call YOU are making
- Role says "assistant" (sounds like restaurant staff)
- Initial message says "thank you for calling" (YOU called them!)
- Asks to "collect" information (YOU should already have it)

**What happens:**
- AI thinks it's the restaurant answering the phone
- Waits for customer to state needs
- Says "How can I help you today?"
- Gets confused about who needs what

---

### ✅ GOOD APPROACH - Clear Identity

```bash
python3 scripts/create_agent.py \
  --name "Reservation Agent" \
  --call-type outbound \
  --objective "make a dinner reservation at the restaurant" \
  --initial-message "Hi, I'd like to make a reservation for dinner tonight." \
  --key-info-dict '{
    "name": "Lee (spelled L-E-E)",
    "party_size": "2 people",
    "preferred_time": "7 PM"
  }'
```

**Why it works:**
- `outbound` correctly identifies YOU are calling
- Objective says "make a reservation" (not "confirm")
- Initial message states YOUR purpose immediately
- Information is provided (not collected)
- No ambiguity about who is calling whom

---

## Example 2: Appointment Confirmation

### ❌ BAD APPROACH - Vague Instructions

```bash
python3 scripts/create_agent.py \
  --name "Appointment Agent" \
  --role "appointment coordinator" \
  --objective "verify the appointment" \
  --initial-message "Hello, I'm calling about an appointment."
```

**Problems:**
- No clear conversation flow
- Doesn't specify WHAT to verify
- No information provided about the appointment
- Opening is vague ("about an appointment")

**What happens:**
- AI doesn't know what to say after opening
- Might ask customer "Do you have an appointment?"
- Confused about what details to confirm
- Conversation goes in circles

---

### ✅ GOOD APPROACH - Detailed Flow

```bash
python3 scripts/create_agent.py \
  --name "Appointment Agent" \
  --call-type outbound \
  --objective "confirm the customer can still attend their appointment tomorrow at 3 PM" \
  --initial-message "Hi, I'm calling to confirm your appointment tomorrow at 3 PM." \
  --key-info-dict '{
    "appointment_time": "3 PM tomorrow",
    "appointment_type": "dental cleaning",
    "customer_name": "John"
  }' \
  --conversation-flow "1. State the appointment time (3 PM tomorrow)
2. Ask: Can you still make it?
3. If YES: Say thanks and confirm
4. If NO: Ask what time works better
5. End: Thank them and say goodbye"
```

**Why it works:**
- Specific appointment details in opening
- Clear question: "Can you still make it?"
- Handles both yes/no responses
- All information provided upfront
- Step-by-step conversation flow

---

## Example 3: Customer Follow-up

### ❌ BAD APPROACH - Robotic Speech

```bash
python3 scripts/create_agent.py \
  --name "Follow-up Agent" \
  --objective "follow up on order" \
  --initial-message "Hello, I am calling from XYZ Company regarding your recent order number 12345 that was delivered on January 15th. I would like to inquire whether you received the package in satisfactory condition and if you have any questions or concerns about the product."
```

**Problems:**
- Initial message is WAY too long
- Sounds like a robot reading a script
- Overwhelming with details all at once
- No natural conversation flow

**What happens:**
- Customer gets confused by information overload
- Sounds unnatural and spam-like
- Customer might hang up
- No room for natural back-and-forth

---

### ✅ GOOD APPROACH - Natural Conversation

```bash
python3 scripts/create_agent.py \
  --name "Follow-up Agent" \
  --call-type outbound \
  --objective "check if customer received their order and if they're satisfied" \
  --initial-message "Hi, I'm calling from XYZ Company about your recent order." \
  --key-info-dict '{
    "order_number": "12345",
    "delivery_date": "January 15th",
    "product": "Widget Pro"
  }' \
  --conversation-flow "1. Introduce yourself (from XYZ Company)
2. Ask: Did you receive your order?
3. If YES: Ask: Is everything okay with it?
4. If issue: Ask: What's wrong?
5. Thank them for their time" \
  --tone "friendly and conversational" \
  --additional-instructions "Speak one sentence at a time. Keep it brief and natural."
```

**Why it works:**
- Short, natural opening
- One question at a time
- Leaves room for responses
- Sounds like a real person
- Clear flow but conversational

---

## Example 4: Using Custom Prompt (Maximum Control)

For complex scenarios, you can write a fully custom prompt:

```bash
python3 scripts/create_agent.py \
  --name "Complex Outbound Agent" \
  --initial-message "Hi, I'd like to make a reservation for tonight." \
  --prompt "# IDENTITY
You are making an OUTBOUND phone call TO a restaurant.
You are the CALLER (customer), NOT the restaurant staff.
YOU called THEM. THEY answered.

# NEVER SAY
NEVER say \"How can I help you?\" - YOU need their help
NEVER say \"Thank you for calling\" - YOU are calling them
NEVER wait for them to speak first - YOU explain why you called

# YOUR TASK
Make a dinner reservation for 2 people tonight at 7 PM.

# INFORMATION YOU ALREADY KNOW
- Name: Lee (L-E-E)
- Party size: 2 people
- Time: 7 PM (flexible: 8 or 9 PM also OK)
- Phone: 310-555-1234

# CONVERSATION FLOW
1. Opening: \"Hi, I'd like to make a reservation for 2 people tonight.\"
2. If they ask time: \"Around 7 PM.\"
3. If they ask name: \"Lee, L-E-E\"
4. If unavailable: \"Do you have 8 or 9 PM available?\"
5. Confirm and thank them

# SPEAKING STYLE
- One short sentence at a time
- Natural, friendly tone
- Don't over-explain"
```

---

## Quick Decision Guide

**When to use each approach:**

| Your Scenario | Use This | Why |
|--------------|----------|-----|
| Outbound call, simple task | `--call-type outbound` + `--objective` | Best practices built-in |
| Outbound call, complex flow | `--prompt` (custom) | Maximum control |
| Inbound call, simple | `--call-type inbound` + `--role`/`--objective` | Works fine for receiving calls |
| Testing/prototype | Any approach | Just test with your own number first |

---

## Remember

**The #1 mistake: Identity confusion**

Always ask yourself:
- **Who is calling whom?** (YOU call THEM, or THEY call YOU?)
- **What should they say first?** (State YOUR purpose, not wait for theirs)
- **What information do they already have?** (Provide it, don't collect it)

**When in doubt, use `--call-type outbound` with the new builder - it handles these issues for you!**
