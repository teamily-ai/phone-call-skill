# Phone Call Skill - Quick Guide for AI Agents

**You are an AI agent trying to make a phone call? This is for you!**

## ⚡ TL;DR - One Command

```bash
cd ~/.openclaw/workspace/skills/phone-call
./scripts/phone_call.sh \
  --to "+1234567890" \
  --purpose "What you want to accomplish on the call"
```

**That's it!** The script handles everything automatically.

---

## 📞 Common Use Cases

### 1. Restaurant Reservation

```bash
./scripts/phone_call.sh \
  --to "+16576102352" \
  --purpose "Make a dinner reservation for 2 people tonight at 8 PM. Name: John Smith, Phone: 310-555-1234"
```

### 2. Meeting Confirmation

```bash
./scripts/phone_call.sh \
  --to "+13105551234" \
  --purpose "Confirm tomorrow's meeting at 3 PM. If they can't make it, ask for alternative times."
```

### 3. Customer Follow-up

```bash
./scripts/phone_call.sh \
  --to "+14155551234" \
  --purpose "Follow up on order #12345. Ask if they received it and if they're satisfied."
```

### 4. Appointment Reminder

```bash
./scripts/phone_call.sh \
  --to "+12125551234" \
  --purpose "Remind about dentist appointment tomorrow at 2 PM. Confirm they can still make it."
```

---

## 🔍 What Happens

1. **Creates Agent** (2-5 seconds)
   - Optimized for your specific purpose
   - Uses best practices for conversation

2. **Makes Call** (instant)
   - Dials the number
   - AI agent starts conversation

3. **Waits** (30-120 seconds)
   - Monitors call progress
   - Updates you on status

4. **Analyzes** (1-2 seconds)
   - Extracts key information
   - Determines success/failure
   - Provides recommendations

5. **Reports** (instant)
   - Clear success/failure indicator
   - Conversation summary
   - Next steps if needed

---

## 📊 Understanding Output

### ✅ Success Example

```
✅ TASK SUCCESSFUL
Confidence: 85%

Reservation Details:
- Time: 10:00 PM (8 PM not available)
- Party: 2 people
- Name: John Smith

Call Duration: 1m 33s
```

### ❌ Failure Example

```
❌ TASK FAILED
Reason: Call too short (15 seconds)

What Happened:
- Restaurant hung up immediately

Recommended Actions:
1. Wait 30 minutes before retrying
2. Try a different time of day
3. Verify phone number is correct
```

---

## 🛠️ Troubleshooting

### "FLUENTS_API_KEY not found"

**Solution:** Make sure `.env` file exists:
```bash
cd ~/.openclaw/workspace/skills/phone-call
cat .env  # Should show FLUENTS_API_KEY=xxx
```

### "Failed to create agent"

**Solution:** Run diagnostics:
```bash
./scripts/phone_call.sh --diagnose
```

### Call failed or no response

**Possible reasons:**
- Wrong phone number format (needs `+1` for US)
- Number not in service
- Busy/voicemail
- Time zone (calling at night)

**What to do:**
- Verify number: `+1234567890` (country code + number)
- Try again in 30+ minutes
- Check if it's business hours

---

## 🎯 Pro Tips

### 1. Be Specific in Purpose

❌ Bad: "Call about reservation"
✅ Good: "Make dinner reservation for 2 people tonight at 8 PM. Name: John Smith, Phone: 310-555-1234"

### 2. Include All Details Upfront

The agent needs to know:
- Names
- Phone numbers for callback
- Specific times/dates
- Any special requests

### 3. Use Existing Agent for Similar Calls

If making multiple similar calls:
```bash
# First call - creates agent
./scripts/phone_call.sh --to "+1111" --purpose "Confirm meeting"
# Output: Agent ID: abc-123

# Subsequent calls - reuse agent
./scripts/phone_call.sh --agent-id "abc-123" --to "+2222"
./scripts/phone_call.sh --agent-id "abc-123" --to "+3333"
```

### 4. Wait Between Retries

Don't call the same number immediately:
- Wait at least 30 minutes
- Better yet, wait 2-4 hours
- Avoid looking like spam

---

## 📝 Advanced Options

### Analyze Past Calls

```bash
./scripts/phone_call.sh --analyze "call-id-xxx"
```

### Use Custom From Number

```bash
./scripts/phone_call.sh \
  --to "+1234567890" \
  --from "+9876543210" \
  --purpose "..."
```

### Check System Status

```bash
./scripts/phone_call.sh --diagnose
```

---

## ❓ FAQ

**Q: How long does a call take?**
A: Usually 30-120 seconds. Script waits automatically.

**Q: Can I make international calls?**
A: Yes, use proper country code (e.g., `+44` for UK).

**Q: What if the person doesn't answer?**
A: Script will report "no answer" and suggest retry timing.

**Q: Can I see the transcript?**
A: Yes, it's in the analysis output after the call.

**Q: Is this reliable?**
A: Yes, but success depends on:
- Phone number being valid
- Person answering
- Clear purpose/instructions
- Appropriate timing (not 2 AM)

**Q: What if it fails?**
A: Script provides specific failure reason and recommendations.

---

## 🆘 Need Help?

1. Check this guide first
2. Run `./scripts/phone_call.sh --diagnose`
3. Check `SKILL.md` for details
4. Check GitHub issues: https://github.com/teamily-ai/phone-call-skill/issues

---

## 🎓 Remember

**The script is designed to be foolproof:**
- It handles errors gracefully
- It provides clear output
- It tells you what to do if something fails
- You don't need to understand the internals

**Just use it and trust the output!** ✅
