# 🦞 OpenClaw — Personal AI Assistant

A self-hosted, personal AI assistant that connects to your messaging channels (WhatsApp, Telegram, Slack, Discord, and more) via a local Gateway.

**EXFOLIATE! EXFOLIATE!**

---

## Core Objective

OpenClaw is a **local-first, single-user assistant** that:
- Runs on your own devices
- Connects to channels you already use (WhatsApp, Telegram, Slack, Discord, etc.)
- Provides a unified AI assistant experience across all platforms
- Keeps your data private and under your control

---

## Architecture

```
WhatsApp / Telegram / Slack / Discord / Signal / iMessage / ...
               │
               ▼
┌───────────────────────────────┐
│            Gateway            │
│       (control plane)         │
│     ws://127.0.0.1:18789      │
└──────────────┬────────────────┘
               │
               ├─ Pi agent (RPC)
               ├─ CLI (openclaw …)
               ├─ WebChat UI
               ├─ macOS app
               └─ iOS / Android nodes
```

---

## Quick Start

### Prerequisites
- **Node.js ≥22**
- **pnpm** (recommended) or npm/bun
- **Gemini API Key** (get at: https://aistudio.google.com/app/apikey)

### 1. Install OpenClaw

```bash
npm install -g openclaw@latest
# or: pnpm add -g openclaw@latest

openclaw onboard --install-daemon
```

### 2. Run the Gateway

```bash
openclaw gateway --port 18789 --verbose
```

### 3. Send a Test Message

```bash
openclaw agent --message "Hello, world!" --thinking high
```

---

## Project Structure

```text
OpenClaw/
├── Dockerfile              # Container build instructions
├── DEPLOY_COOLIFY.md       # Coolify deployment guide
├── README.md               # This file
└── openclaw.json           # Configuration (created on setup)
```

**When cloned from source:**
```text
openclaw/
├── src/                    # TypeScript source
├── dist/                   # Built JavaScript
├── packages/
│   ├── gateway/            # WebSocket control plane
│   ├── cli/                # Command-line interface
│   └── ui/                 # Control UI + WebChat
├── docs/                   # Documentation
├── package.json
├── pnpm-lock.yaml
└── tsconfig.json
```

---

## Supported Channels

| Channel | Status | Auth Method |
|---------|--------|-------------|
| **WhatsApp** | ✅ | QR Code (Baileys) |
| **Telegram** | ✅ | Bot Token |
| **Discord** | ✅ | Bot Token |
| **Slack** | ✅ | Bot + App Token |
| **Signal** | ✅ | signal-cli |
| **iMessage** | ✅ | macOS only |
| **Microsoft Teams** | ✅ | Bot Framework |
| **Google Chat** | ✅ | Chat API |
| **Matrix** | ✅ | Extension |
| **WebChat** | ✅ | Built-in Gateway UI |

---

## Configuration

### Environment Variables (Recommended for Docker)

OpenClaw reads configuration from environment variables. For Docker deployments, set these in your container:

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (recommended) |
| `ANTHROPIC_API_KEY` | Anthropic Claude key (optional) |
| `OPENAI_API_KEY` | OpenAI API key (optional fallback) |
| `OPENCLAW_GATEWAY_TRUSTED_PROXIES` | Trust proxy IPs (e.g., `10.0.0.0/8` for Docker) |
| `OPENCLAW_GATEWAY_TOKEN` | Auth token for dashboard access |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `DISCORD_BOT_TOKEN` | Discord bot token |

### Config File (`~/.openclaw/openclaw.json`)

For advanced setups, you can use a config file:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "google/gemini-3-flash-preview"
      }
    }
  }
}
```

> [!TIP]
> See full configuration reference: https://docs.openclaw.ai/gateway/configuration

---

## Key Features

### 1. Multi-Channel Inbox
Connect once, respond everywhere. Messages from all channels flow through a single Gateway.

### 2. Voice Wake + Talk Mode
Always-on speech recognition for macOS/iOS/Android with ElevenLabs TTS.

### 3. Live Canvas
Agent-driven visual workspace with A2UI (Agent-to-UI) rendering.

### 4. Skills Platform
Bundled, managed, and workspace skills that extend the agent's capabilities.

### 5. Browser Control
Dedicated Chrome/Chromium instance with CDP control for web automation.

### 6. Session Management
- `/status` — Session status
- `/new` or `/reset` — Reset session
- `/compact` — Compact context
- `/think <level>` — Set thinking level

---

## Security

### DM Pairing (Default)
Unknown senders receive a pairing code. Approve with:
```bash
openclaw pairing approve telegram ABC123
```

### Allowlists
Configure per-channel allowlists in `openclaw.json`:
```json5
{
  "channels": {
    "whatsapp": {
      "allowFrom": ["+1234567890", "+0987654321"]
    }
  }
}
```

### Security Checklist
- [x] DM pairing enabled by default
- [x] API keys in environment variables
- [x] HTTPS for remote access
- [ ] Channel allowlists configured
- [ ] Sandbox mode for non-main sessions

---

## Deployment

### Docker

```bash
# Build image
docker build -t openclaw .

# Run container (use a random external port, not 18789!)
docker run -p 44892:18789 \
  -e GEMINI_API_KEY=your_key \
  -e OPENCLAW_GATEWAY_TOKEN=your_token \
  -e OPENCLAW_GATEWAY_BIND=lan \
  -e OPENCLAW_GATEWAY_TRUSTED_PROXIES="10.0.0.0/8" \
  -v ~/.openclaw:/home/node/.openclaw \
  openclaw
```

> [!CAUTION]
> **Do NOT expose port 18789 publicly.** Use a random port (e.g., `44892:18789`) to avoid Shodan scans. See [DEPLOY_COOLIFY.md](./DEPLOY_COOLIFY.md) for security details.

### Coolify

See [DEPLOY_COOLIFY.md](./DEPLOY_COOLIFY.md) for detailed instructions.

---

## CLI Reference

```bash
# Gateway control
openclaw gateway --port 18789
openclaw gateway:watch  # Dev mode with auto-reload

# Agent interaction
openclaw agent --message "Hello"
openclaw agent --message "Complex task" --thinking high

# Channel management
openclaw channels login       # Link WhatsApp
openclaw channels list        # Show connected channels

# Pairing
openclaw pairing list
openclaw pairing approve <channel> <code>

# Diagnostics
openclaw doctor              # Check configuration
openclaw --version          # Show version
```

---

## Troubleshooting

### Gateway Not Starting
```bash
# Check for port conflicts
lsof -i :18789

# Run with verbose logging
openclaw gateway --verbose
```

### WhatsApp Session Expired
```bash
# Clear credentials and re-link
rm -rf ~/.openclaw/credentials/whatsapp
openclaw channels login
```

> [!TIP]
> **Docker users:** To avoid re-scanning the QR code after every restart, configure persistent storage for `~/.openclaw/`. See [DEPLOY_COOLIFY.md](./DEPLOY_COOLIFY.md#7-persistent-storage) for details.

### Model Not Responding
```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Run doctor
openclaw doctor
```

---

## Resources

- **Website:** https://openclaw.ai
- **Docs:** https://docs.openclaw.ai
- **GitHub:** https://github.com/openclaw/openclaw
- **Discord:** https://discord.gg/clawd
- **DeepWiki:** https://deepwiki.com/openclaw/openclaw

---

## Model Recommendations

| Model | Best For |
|-------|----------|
| **Google Gemini 3 Pro** | Long-context, cost-effective (recommended) |
| **Anthropic Claude Opus** | Prompt-injection resistance |
| **Anthropic Claude Sonnet** | Balanced speed/quality |
| **OpenAI GPT-4o** | Vision and multimodal |

---

## Credits

- **Peter Steinberger** and the OpenClaw community
- Built for **Molty**, a space lobster AI assistant 🦞
- Powered by **Google Gemini**, **Anthropic Claude**, and **OpenAI**

---

## License

MIT License — See [LICENSE](https://github.com/openclaw/openclaw/blob/main/LICENSE)
