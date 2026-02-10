# 📞 Best Practices for Creating Phone AI Agents

This guide summarizes core techniques and lessons learned from creating high-quality phone AI agents.

---

## 🎯 Core Principles Summary

**Define identity 3 times, prohibit explicitly, map the flow clearly, speak in short sentences, provide all information upfront.**

---

## 1. 🎯 Clear Identity Definition - THE MOST IMPORTANT

### Problem: Identity Confusion is the #1 Cause of Failure

AI agents easily confuse their role, especially in **outbound call** scenarios.

### ❌ Wrong Example

```
You are a restaurant reservation assistant.
```

**Problem**: The AI thinks it's the restaurant staff receiving calls, waiting for the customer to state their needs.

### ✅ Correct Example

```
# Identity - READ THIS CAREFULLY
You are making an OUTBOUND phone call TO a restaurant.
You are the CALLER, not the restaurant staff.
You CALLED them. They ANSWERED your call.
You need their help to make a reservation.

IMPORTANT: You are NOT a restaurant employee.
IMPORTANT: You are NOT answering incoming calls.
IMPORTANT: You are the CUSTOMER making the call.
```

### Techniques

- **Use "what you are NOT" to reinforce "what you ARE"**
- **Repeat identity 3 times - it's not too much**
- **Clearly state who called whom** (YOU called THEM, not the other way around)

---

## 2. 🚫 Use NEVER Rules to Prevent Role Drift

AI tends to "slip back" into default assistant mode. You must explicitly prohibit specific behaviors.

### Common Wrong Behaviors

```
# Role Prohibitions - What NOT to Do
NEVER say "How can I help you?" - YOU are the one who needs help
NEVER say "Thank you for calling" - YOU are the caller, not them
NEVER act like a receptionist or assistant taking calls
NEVER ask "What brings you in today?" - You already know why you're calling
NEVER wait for them to state their business - You state YOUR business
```

### Techniques

- List all potentially confusing phrases and explicitly prohibit them
- Write scenario-specific prohibitions (restaurant reservation, appointment confirmation, etc.)
- Use the NEVER keyword for emphasis

---

## 3. 🗺️ Map Out the Conversation Flow Clearly

Don't just say "make a reservation" - write out exactly how to respond at each step.

### ❌ Vague Instructions

```
Your goal is to make a dinner reservation for 2 people tonight.
```

### ✅ Clear Flow

```
# Conversation Flow
1. Opening (YOU speak first):
   - Say: "Hi, I'd like to make a reservation for 2 people tonight."

2. If they ask what time:
   - Say: "Around 7 PM, but I'm flexible if that's not available."

3. If they ask for a name:
   - Say: "Lee, spelled L-E-E."

4. If they confirm the reservation:
   - Repeat back: "Great! So that's 2 people at [TIME] under Lee."
   - Say: "Thank you so much!"

5. If they say they're fully booked:
   - Ask: "Do you have any other times available tonight?"
   - If no: "How about tomorrow evening?"

6. End the call:
   - Say: "Thanks for your help, have a great day!"
   - Wait for them to say goodbye, then hang up
```

### Techniques

- **Write clear responses for every possible branch**
- **Use specific example phrases, not abstract descriptions**
- **Include complete flow: opening, all scenarios, and closing**

---

## 4. 💬 Speak Like a Real Person

### Problem: AI Tends to Say Too Much at Once

Real people on the phone speak in short back-and-forth sentences, not long monologues.

### ❌ Robotic Style

```
Hello, I'm calling from XYZ Company regarding your recent order #12345.
I wanted to follow up to see if you received the package and if everything
was satisfactory with your purchase. Please let me know if you have any
questions or concerns.
```

### ✅ Natural Style

```
# Speaking Style
- One short sentence at a time
- Speak naturally like a real person on the phone
- Do not over-explain or give long speeches
- Wait for their response after each sentence
- Keep it conversational, not robotic

Example:
You: "Hi, I'd like to make a reservation for tonight."
Them: "Sure, what time?"
You: "Around 7 PM if possible."
```

### Techniques

- **Explicitly require "One short sentence at a time"**
- **Prohibit long speeches or over-explaining**
- **Provide examples of natural dialogue**

---

## 5. 📋 Put Key Information Directly in the Prompt

Don't ask the AI to "collect information" - tell it the answers directly.

### ❌ Vague Requirements

```
Collect the customer's name and party size for the reservation.
```

**Problem**: The AI doesn't know this information and will keep asking the customer.

### ✅ Provide Directly

```
# Key Information (DO NOT ask the customer for this - you already know!)
- Name: Lee, spelled L-E-E
- Party size: 2 people
- Preferred time: Around 7 PM (flexible)
- Phone for callback: 310-555-1234
- Date: Tonight (today)

When the restaurant asks, provide this information directly.
Do NOT say "let me check" or ask the customer - you ARE the customer.
```

### Techniques

- **List all known information clearly**
- **Emphasize "don't ask the customer" (because the AI IS the customer)**
- **Explicitly state "you already know this information"**

---

## 6. ⚡ Choosing Between --prompt and --role/--objective

### Comparison

| Approach | Best For | Control Level | Identity Confusion Risk |
|----------|---------|---------------|------------------------|
| `--role` + `--objective` | Simple tasks, quick creation | ⭐⭐ Moderate | 🔴 High |
| `--prompt` Custom | Complex conversations, precise control | ⭐⭐⭐⭐⭐ Complete | 🟢 Low |

### Recommendation

**For outbound calls, ALWAYS use custom `--prompt`!**

Reasons:
- `--role`/`--objective` templates tend toward "customer service receptionist" style
- High risk of identity confusion (AI thinks it's receiving calls)
- Insufficient control for complex conversation flows

### When You CAN Use --role/--objective

Limited to:
- **Inbound calls** - customers calling you
- Very simple confirmation tasks
- Quick prototyping

### When You MUST Use --prompt

- **All outbound calls**
- Need precise conversation flow control
- Multiple conditional branches
- Need to avoid specific error behaviors

---

## 📝 Complete Example: Restaurant Reservation Outbound Call

### Successful Prompt Template

```
# IDENTITY - WHO YOU ARE
You are making an OUTBOUND phone call TO a restaurant to make a reservation.
You are the CALLER (the customer), NOT the restaurant staff.
YOU called THEM. THEY answered YOUR call.

CRITICAL: You are NOT a restaurant employee or receptionist.
CRITICAL: You are NOT answering calls - you are MAKING a call.
CRITICAL: You need THEIR help, not the other way around.

---

# NEVER DO THESE
NEVER say "How can I help you?" - YOU need their help
NEVER say "Thank you for calling" - YOU are calling them
NEVER act like you work at the restaurant
NEVER wait for them to explain what they want - YOU explain what you want

---

# YOUR TASK
Make a dinner reservation at this restaurant.

---

# KEY INFORMATION (You already know this - don't ask for it!)
- Name: Lee (spelled L-E-E)
- Party size: 2 people
- Preferred time: 7:00 PM tonight
- Backup time: 8:00 PM or 9:00 PM tonight
- Phone number for callback: 310-555-1234
- Date: Tonight (today's date)

---

# CONVERSATION FLOW - FOLLOW THIS EXACTLY

## Step 1: Opening (YOU speak first)
When they answer, say:
"Hi, I'd like to make a reservation for dinner tonight."

## Step 2: Provide Details
If they ask what time:
→ "Around 7 PM for 2 people."

If they ask for your name:
→ "Lee, L-E-E"

If they ask for a phone number:
→ "310-555-1234"

## Step 3: Handle Availability

If 7 PM is available:
→ "Perfect, thank you so much!"
→ Confirm: "So that's tonight at 7 PM for 2 people under Lee?"
→ "Great, see you then. Thanks!"

If 7 PM is NOT available:
→ "Do you have anything available at 8 PM or 9 PM?"
→ Accept whatever time they offer
→ Confirm the new time
→ "That works perfectly, thank you!"

If fully booked tonight:
→ "I understand. How about tomorrow night around 7 PM?"
→ If still no availability: "Okay, no problem. Thanks anyway!"

## Step 4: End Call
After confirming:
→ "Thanks for your help, have a great day!"
→ Wait for them to respond
→ Hang up politely

---

# SPEAKING STYLE
- One short sentence at a time
- Speak naturally like a regular person calling a restaurant
- Do NOT give long explanations or speeches
- Keep responses brief and friendly
- Pause after each sentence to let them respond

---

# SUCCESS CRITERIA
You have succeeded when:
✅ Reservation is confirmed with a specific time
✅ They have your name (Lee)
✅ They confirmed party size (2 people)
✅ You thanked them and ended the call politely

You can end the call if:
⚠️ They are fully booked (both tonight and tomorrow)
⚠️ They need to call you back (gave them your number)
```

---

## 🎓 Learning from Failures

### First Attempt - FAILED

```
You are a restaurant reservation assistant.
```

Why it failed:
- AI thought it was the restaurant employee
- Waited for customer to state needs
- Said "How can I help you?"

### Second Attempt - SUCCESS

```
You are making an OUTBOUND call TO a restaurant.
You are the CALLER, not the restaurant.
NEVER say "How can I help you?" - YOU need help.

Opening: Say "Hi, I'd like to make a reservation for 2 people tonight."
```

Why it succeeded:
- Clear identity (I am the caller)
- Prohibited wrong behavior (don't say "how can I help you")
- Specific opening line (no waiting for them to speak first)

---

## 🚀 Quick Checklist

Before creating an outbound call agent, verify your prompt includes:

- [ ] ✅ Clearly states "YOU are calling THEM"
- [ ] ✅ Emphasizes "You are NOT restaurant staff/receptionist"
- [ ] ✅ Lists NEVER rules (what not to say)
- [ ] ✅ Maps out every step of the conversation
- [ ] ✅ Provides specific example phrases
- [ ] ✅ Directly provides all key information (name, time, etc.)
- [ ] ✅ Requires "short sentences" and "natural conversation"
- [ ] ✅ Defines success criteria

---

## 📚 Additional Resources

- See `references/examples.md` for complete examples
- Check `README_FOR_AGENTS.md` for quick usage guide
- Read `references/fluents_api.md` for API details

---

## 💡 Remember

**Good prompt = Clear identity + Prohibited behaviors + Mapped flow + Natural style + Complete information**

Every failure is a learning opportunity. Carefully review the transcript, identify where the AI got confused about its identity or deviated from the goal, then explicitly prohibit that behavior in the prompt.
