#!/bin/bash
set -e

# OpenClaw Gateway Entrypoint for Coolify/Docker
# Configures gateway, agent API keys, default model, and channels from environment variables

CONFIG_DIR="${HOME:-/root}/.openclaw"
CONFIG_FILE="$CONFIG_DIR/openclaw.json"
AGENT_DIR="$CONFIG_DIR/agents/main/agent"
AUTH_FILE="$AGENT_DIR/auth-profiles.json"
CREDENTIALS_DIR="$CONFIG_DIR/credentials"

mkdir -p "$CONFIG_DIR"
mkdir -p "$AGENT_DIR"
mkdir -p "$CREDENTIALS_DIR"

# Parse comma-separated proxies into JSON array
if [ -n "$OPENCLAW_GATEWAY_TRUSTED_PROXIES" ]; then
  PROXIES_JSON=$(echo "$OPENCLAW_GATEWAY_TRUSTED_PROXIES" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')
else
  PROXIES_JSON='["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]'
fi

# Generate token if not provided
if [ -z "$OPENCLAW_GATEWAY_TOKEN" ]; then
  OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)
  echo "🔐 Generated auth token: $OPENCLAW_GATEWAY_TOKEN"
fi

# Determine default model based on available API keys
DEFAULT_MODEL="google/gemini-3-flash-preview"

if [ -n "$OPENCLAW_AGENT_MODEL" ]; then
  DEFAULT_MODEL="$OPENCLAW_AGENT_MODEL"
elif [ -n "$ANTHROPIC_API_KEY" ]; then
  DEFAULT_MODEL="anthropic/claude-sonnet-4-20250514"
elif [ -n "$OPENAI_API_KEY" ]; then
  DEFAULT_MODEL="openai/gpt-4o"
fi

echo "🦞 OpenClaw Configuration"
echo "--------------------------------"
echo "Trusted Proxies: $OPENCLAW_GATEWAY_TRUSTED_PROXIES"
echo "Auth Token: $OPENCLAW_GATEWAY_TOKEN"
echo "Default Model: $DEFAULT_MODEL"
echo "--------------------------------"

# Build channels config - OpenClaw uses tokenFile, not token directly
CHANNELS_JSON=""

if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
  # Write token to file (OpenClaw expects tokenFile reference)
  echo -n "$TELEGRAM_BOT_TOKEN" > "$CREDENTIALS_DIR/telegram-bot-token"
  CHANNELS_JSON="\"telegram\": { \"tokenFile\": \"$CREDENTIALS_DIR/telegram-bot-token\" }"
  echo "📱 Telegram channel configured"
fi

if [ -n "$DISCORD_BOT_TOKEN" ]; then
  echo -n "$DISCORD_BOT_TOKEN" > "$CREDENTIALS_DIR/discord-bot-token"
  if [ -n "$CHANNELS_JSON" ]; then CHANNELS_JSON="$CHANNELS_JSON,"; fi
  CHANNELS_JSON="$CHANNELS_JSON\"discord\": { \"tokenFile\": \"$CREDENTIALS_DIR/discord-bot-token\" }"
  echo "📱 Discord channel configured"
fi

if [ -n "$SLACK_BOT_TOKEN" ] && [ -n "$SLACK_APP_TOKEN" ]; then
  echo -n "$SLACK_BOT_TOKEN" > "$CREDENTIALS_DIR/slack-bot-token"
  echo -n "$SLACK_APP_TOKEN" > "$CREDENTIALS_DIR/slack-app-token"
  if [ -n "$CHANNELS_JSON" ]; then CHANNELS_JSON="$CHANNELS_JSON,"; fi
  CHANNELS_JSON="$CHANNELS_JSON\"slack\": { \"botTokenFile\": \"$CREDENTIALS_DIR/slack-bot-token\", \"appTokenFile\": \"$CREDENTIALS_DIR/slack-app-token\" }"
  echo "📱 Slack channel configured"
fi

# Create gateway config with agents list for TaskBoard integration
cat > "$CONFIG_FILE" << EOF
{
  "gateway": {
    "trustedProxies": $PROXIES_JSON,
    "auth": {
      "mode": "token",
      "token": "$OPENCLAW_GATEWAY_TOKEN"
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "$DEFAULT_MODEL"
      }
    },
    "list": [
      {
        "id": "main",
        "name": "OpenClaw",
        "subagents": {
          "allowAgents": ["architect", "security-auditor", "code-reviewer", "ux-manager"]
        }
      },
      {
        "id": "architect",
        "name": "Architect",
        "identity": { "name": "Architect", "emoji": "🏛️" },
        "tools": { "profile": "coding", "deny": ["browser", "message"] }
      },
      {
        "id": "security-auditor",
        "name": "Security Auditor",
        "identity": { "name": "Security Auditor", "emoji": "🔒" },
        "tools": { "profile": "coding", "deny": ["browser", "message"] }
      },
      {
        "id": "code-reviewer",
        "name": "Code Reviewer",
        "identity": { "name": "Code Reviewer", "emoji": "📝" },
        "tools": { "profile": "coding", "deny": ["browser", "message"] }
      },
      {
        "id": "ux-manager",
        "name": "UX Manager",
        "identity": { "name": "UX Manager", "emoji": "🎨" },
        "tools": { "profile": "coding", "deny": ["message"] }
      }
    ]
  }$(if [ -n "$CHANNELS_JSON" ]; then echo ",
  \"channels\": {
    $CHANNELS_JSON
  }"; fi)
}
EOF

echo "✅ Gateway config created at $CONFIG_FILE"

# Create agent auth-profiles.json with API keys from environment
echo "🔑 Configuring agent API keys..."

AUTH_JSON='{"profiles":{'

if [ -n "$ANTHROPIC_API_KEY" ]; then
  AUTH_JSON="${AUTH_JSON}\"anthropic\":{\"apiKey\":\"$ANTHROPIC_API_KEY\"},"
  echo "   ✓ Anthropic API key configured"
fi

if [ -n "$GEMINI_API_KEY" ]; then
  AUTH_JSON="${AUTH_JSON}\"google\":{\"apiKey\":\"$GEMINI_API_KEY\"},"
  echo "   ✓ Google/Gemini API key configured"
fi

if [ -n "$OPENAI_API_KEY" ]; then
  AUTH_JSON="${AUTH_JSON}\"openai\":{\"apiKey\":\"$OPENAI_API_KEY\"},"
  echo "   ✓ OpenAI API key configured"
fi

AUTH_JSON="${AUTH_JSON%,}}}"

echo "$AUTH_JSON" > "$AUTH_FILE"
echo "✅ Agent auth config created at $AUTH_FILE"

echo ""
echo "🔗 Access URL: https://YOUR_DOMAIN/?token=$OPENCLAW_GATEWAY_TOKEN"
echo ""

# Execute the CMD
exec "$@"
