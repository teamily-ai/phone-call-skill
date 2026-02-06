# Phone Call Skill

🤖 An intelligent AI skill for Claude Code that manages the complete phone call lifecycle through the fluents.ai platform.

## Features

### Core Capabilities
- 🎯 **Automatic intent recognition** - Understands when users want to make calls
- 🤖 **Smart agent creation** - Creates purpose-optimized AI phone agents
- 📞 **Call execution & monitoring** - Initiates and tracks phone calls
- 🔍 **Intelligent conversation analysis** - Analyzes transcripts and extracts insights
- 📊 **Actionable reporting** - Provides clear success/failure summaries
- 🔄 **Continuous optimization** - Learns from failures and improves performance

### Advanced Features
- 🗣️ Multi-language support (11 languages)
- 📝 Call transcript retrieval and analysis
- 🎯 Task completion verification
- 🚨 Failure pattern detection
- 💡 Optimization recommendations
- 📈 Success confidence scoring

## Installation

```bash
npx skills add your-username/phone-call-skill
```

## Quick Start

1. Install the skill (see above)
2. Configure your fluents.ai API key (see Configuration)
3. Ask Claude to make a phone call:
   - "Call +1234567890 to confirm the meeting"
   - "I need to call a customer for feedback"
   - "Make a phone call to check on the order status"

## Configuration

Create a `.env` file in your project:

```env
FLUENTS_API_KEY=your_api_key_here
FLUENTS_API_URL=https://api.fluents.ai
WEBHOOK_URL=https://your-webhook.com/callback
```

See `.env.example` for a template.

## How It Works

1. **Intent Recognition**: Claude identifies when you want to make a phone call
2. **Information Gathering**: Collects phone number, purpose, and conversation requirements
3. **Agent Creation**: Creates a specialized phone agent via fluents.ai API
4. **Call Execution**: Initiates the phone call with the created agent
5. **Content Analysis**: Retrieves and understands the call transcript
6. **Result Reporting**: Provides you with a summary and key insights

## Requirements

- Python 3.8+
- fluents.ai API account
- Internet connection

## Documentation

- [SKILL.md](./SKILL.md) - Complete skill documentation
- [API Reference](./references/fluents_api.md) - fluents.ai API details
- [Examples](./references/examples.md) - Usage examples

## Security & Privacy

- ⚠️ Ensure you have permission to call the target number
- 🔒 Never commit your API keys to version control
- 📋 Follow local telemarketing regulations
- 🛡️ Handle call records securely

## License

MIT License - see [LICENSE](./LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

- Website: https://fluents.ai
- Issues: [GitHub Issues](https://github.com/your-username/phone-call-skill/issues)
