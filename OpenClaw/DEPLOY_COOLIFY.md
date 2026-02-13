# Deploying OpenClaw on Coolify

This guide outlines how to deploy OpenClaw (a personal AI assistant) using Coolify and connect it to your messaging channels.

## 1. Overview

**OpenClaw** is a local-first, personal AI assistant that connects to messaging platforms (WhatsApp, Telegram, Slack, Discord, etc.) via a WebSocket Gateway. It's a Node.js application that can be self-hosted on Coolify.

**Architecture:**
```
WhatsApp / Telegram / Slack / Discord / ...
               │
               ▼
┌───────────────────────────────┐
│            Gateway            │
│       (control plane)         │
│     ws://127.0.0.1:18789      │
└───────────────────────────────┘
```

---

## 2. Prerequisites

- **Coolify instance** running at `coolify.longtermtrends.net`
- **Gemini API Key** (get at: https://aistudio.google.com/app/apikey)
- **Anthropic API Key** (optional, for Claude models)
  - Get at: https://www.anthropic.com/
- **OpenAI API Key** (optional, for fallback)
  - Get at: https://platform.openai.com/
- **Node.js ≥22** (handled by Docker)
- **Channel credentials** (WhatsApp, Telegram, Slack, Discord, etc.) as needed

---

## 3. Dockerfile

Use the provided [Dockerfile](./Dockerfile) in this directory. It handles:
- Node.js 22 (bookworm) base image
- pnpm installation and build (clones from official OpenClaw repo)
- Health check on `/health`
- Gateway startup on port 18789 (internal)

> [!NOTE]
> The Dockerfile exposes port 18789 internally. Coolify maps this to a different external port for security (see section 4.2).

---

## 4. Coolify Configuration

### 4.1. Create New Application
1. **Login** to [coolify.longtermtrends.net](https://coolify.longtermtrends.net)
2. **Create New Resource:** Application → **Private Repository (with App)**
3. **Repository Settings:**
   - **Source:** select `longtermtrends-coolify` (or your connected Git App)
   - **Repository:** `silvanfrank/longtermtrends2`
   - **Branch:** `master`
   - **Build Pack:** **Dockerfile**

> [!NOTE]
> We use a custom Dockerfile in this repo (not the official OpenClaw repo) because the official Dockerfile doesn't start the gateway daemon automatically.

### 4.2. Build Settings
Navigate to **General** tab:

**Base Directory:**
```
/docs/Longtermtrends-Content/Agents/OpenClaw
```

**Dockerfile Location:**
```
/Dockerfile
```

**Port Exposes:**
```
18789
```

**Port Mappings:**
```
44892:18789
```

> [!CAUTION]
> **Do NOT use the default port 18789!** Services like Shodan actively scan for OpenClaw instances on this port. Hundreds of unsecured instances have been compromised. Use a random port like `44892`, `37291`, or generate your own.

### 4.3. Environment Variables
Go to **Environment Variables** tab and add:

| Key | Value | Description |
|-----|-------|-------------|
| `OPENCLAW_GATEWAY_TOKEN` | (see below) | **Required.** Dashboard access token |
| `GEMINI_API_KEY` | `your_gemini_key` | Google Gemini API key |
| `ANTHROPIC_API_KEY` | `your_anthropic_key` | (Optional) Anthropic Claude key |
| `OPENAI_API_KEY` | `your_openai_key` | (Optional) OpenAI fallback key |
| `OPENCLAW_GATEWAY_BIND` | `lan` | **Required for Docker.** Bind to all interfaces |
| `OPENCLAW_GATEWAY_TRUSTED_PROXIES` | `10.0.0.0/8` | **Required.** Trust Coolify's internal proxy |

> [!TIP]
> Generate a secure token with: `openssl rand -hex 32`

**Channel-Specific Variables (add as needed):**

| Key | Value | Description |
|-----|-------|-------------|
| `TELEGRAM_BOT_TOKEN` | `123456:ABCDEF` | Telegram bot token |
| `DISCORD_BOT_TOKEN` | `your_discord_token` | Discord bot token |
| `SLACK_BOT_TOKEN` | `xoxb-...` | Slack bot token |
| `SLACK_APP_TOKEN` | `xapp-...` | Slack app token |

> [!CAUTION]
> Never commit API keys to Git. Use Coolify's environment variables exclusively.

### 4.4. Domain Configuration
**Domain Settings:**
- **Protocol:** `https` (Coolify auto-provisions SSL via Let's Encrypt)
- **Domain:** `f4gog4oo80kwg0ggwg008gs4.xx.xxx.xx.xxx.sslip.io` (current)
- **Wildcard:** No

**DNS Setup (For Future Custom Domain):**
If you later switch to a custom domain (e.g., `openclaw.longtermtrends.com`), add an A record:
```
openclaw.longtermtrends.com → [Your Coolify Server IP]
```

### 4.5. Deploy
1. Click **Deploy**
2. Watch the build logs for errors
3. Look for `🦞 OPENCLAW READY` in the logs — this confirms successful startup
4. Wait for health check to pass (`/health` endpoint)

**Build Time:** ~5-7 minutes (includes pnpm install + build)

---

## 5. Configuration (Environment Variables)

OpenClaw reads configuration directly from environment variables. **No config file is required for basic setups.**

**Key Environment Variables:**
| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | **Required.** Your Google Gemini API key |
| `OPENCLAW_GATEWAY_TRUSTED_PROXIES` | **Required for Coolify.** Set to `10.0.0.0/8` |
| `OPENCLAW_GATEWAY_TOKEN` | (Optional) Auth token for dashboard access |

> [!NOTE]
> The `--bind lan` flag in the Dockerfile ensures OpenClaw binds to `0.0.0.0` (all interfaces), which is required for Docker networking.

**To verify the gateway is running:**
```bash
docker exec -it <container-id> curl http://localhost:18789/health
```

---

## 6. Post-Deployment Setup

### 6.1. Access the Dashboard

1. **Wait for the container to start** (check health status in Coolify)
2. **Navigate to your domain**: `https://f4gog4oo80kwg0ggwg008gs4.xx.xxx.xx.xxx.sslip.io/`
3. If you set `OPENCLAW_GATEWAY_TOKEN`, append it: `https://f4gog4oo80kwg0ggwg008gs4.xx.xxx.xx.xxx.sslip.io/?token=<YOUR_TOKEN>`

> [!TIP]
> If you didn't set a token, you may need to run `openclaw doctor` in the container to set up authentication.

### 6.2. Run the Onboarding Wizard

To configure your agent's personality and skills:

1. Open the **Service Terminal** in Coolify
2. Run:
   ```bash
   docker exec -it <container-id> node dist/index.js onboard
   ```
3. Follow the interactive wizard

### 6.3. Verify Health

```bash
curl https://f4gog4oo80kwg0ggwg008gs4.xx.xxx.xx.xxx.sslip.io/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "gateway": "running"
}
```

---

## 7. Persistent Storage

For **sessions, history, and channel credentials** to survive container restarts, configure persistent storage.

> [!WARNING]
> **First deployment:** Do NOT configure persistent storage on your first deploy. Get the dashboard working first, then add storage and redeploy. Old config files in storage can cause startup errors.

### 7.1. What Persistent Storage Preserves

| Data | Path | Why It Matters |
|------|------|----------------|
| WhatsApp session | `credentials/whatsapp/` | Avoids re-scanning QR code on restart |
| Chat history | `agents/<id>/sessions/*.jsonl` | Preserves conversation transcripts |
| Channel credentials | `credentials/` | Telegram/Discord/Slack session tokens |
| Paired devices | `nodes/paired.json` | Approved devices (if device auth is enabled) |
| Configuration | `openclaw.json` | ⚠️ **Regenerated on every start by entrypoint** |

### 7.2. Configure Volume in Coolify

**After your dashboard is working:**

1. Go to your OpenClaw application
2. Click **Storages** tab
3. Click **+ Add** to create a new volume
4. Configure:
   - **Name:** `openclaw-data`
   - **Source (Host Path):** `/var/lib/docker/volumes/openclaw-data/_data`
   - **Destination (Container Path):** `/root/.openclaw`
5. Click **Save** and **Redeploy**

> [!NOTE]
> The `docker-entrypoint.sh` script **overwrites** `openclaw.json` on every container start from your environment variables. So even with persistent storage, your config stays in sync with Coolify's env vars.

---

## 8. Channel Setup

### 8.1. WhatsApp (via Dashboard)

WhatsApp requires scanning a QR code:

1. **Go to your OpenClaw Dashboard** (from the logs URL with token)
2. Navigate to **Channels → WhatsApp**
3. Open **WhatsApp on your phone** → Linked Devices → Link a Device
4. **Scan the QR code** shown on the dashboard
5. Done! You can now chat with OpenClaw via WhatsApp

**Configure allowlist** (recommended):
```json5
{
  "channels": {
    "whatsapp": {
      "allowFrom": ["+1234567890", "+0987654321"]
    }
  }
}
```

> [!TIP]
> The dashboard method is simpler than scanning from terminal logs.

### 8.2. Telegram
1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get the bot token
3. Add `TELEGRAM_BOT_TOKEN` to Coolify environment variables
4. Redeploy

### 8.3. Discord
1. Create app at https://discord.com/developers/applications
2. Create a bot and get the token
3. Add `DISCORD_BOT_TOKEN` to Coolify environment variables
4. Invite bot to your server with appropriate permissions
5. Redeploy

### 8.4. Slack
1. Create app at https://api.slack.com/apps
2. Enable Socket Mode
3. Get Bot Token (`xoxb-...`) and App Token (`xapp-...`)
4. Add both to Coolify environment variables
5. Install app to your workspace
6. Redeploy

---

## 9. Security Configuration

### 9.1. DM Policy (Important)
By default, OpenClaw uses **pairing mode** for unknown senders:

| Policy | Description |
|--------|-------------|
| `pairing` | Unknown senders receive a pairing code (default, recommended) |
| `open` | Accept messages from anyone (use with caution) |

**Approve a paired user via Dashboard:**
1. Go to OpenClaw Dashboard → **Pairing**
2. Find the pending request with the pairing code
3. Click **Approve**

**Or via CLI:**
```bash
docker exec CONTAINER_ID openclaw pairing approve telegram ABC123
```

> [!WARNING]
> **Never use `openclaw-approve`** (the break-glass utility) for routine approvals — it accepts ALL pending requests. Use the dashboard or specific CLI command instead.

### 9.2. Trusted Proxies (Critical for Nginx/Caddy)

If you're running behind a reverse proxy (nginx, Caddy, Traefik), you **must** configure trusted proxies:

```json5
{
  "gateway": {
    "trustedProxies": ["127.0.0.1", "::1"]
  }
}
```

> [!CAUTION]
> **Without this setting, anyone accessing your URL will be treated as `localhost`**, bypassing all authentication. This is the #1 vulnerability being exploited in the wild.

### 9.3. Security Checklist
- [x] API Keys in environment variables (not in code)
- [x] HTTPS enforced via Coolify/Traefik
- [x] DM pairing enabled (default)
- [x] Dashboard token-protected
- [x] **Non-default port** (not 18789, 443, 80, 8080, 3000)
- [x] **Trusted proxies configured** (if using reverse proxy)
- [ ] Channel allowlists configured
- [ ] Rate limiting enabled
- [ ] Tailscale/VPN for extra protection (optional)

---

## 10. If You've Been Exposed

> [!WARNING]
> If you deployed OpenClaw on port 18789 without authentication, assume your API keys are compromised.

**Immediate Actions:**
1. **Rotate ALL API keys** (Gemini, Anthropic, OpenAI, Telegram, Discord, Slack, etc.)
2. **Check your logs** for unauthorized access
3. **Update OpenClaw** to the latest version (patches nginx bypass)
4. **Change to a non-default port**
5. **Configure trusted proxies** if using nginx/Caddy

---

## 10. Monitoring & Logs

### 10.1. View Logs in Coolify
1. Go to your OpenClaw application
2. Click **Logs** tab
3. Monitor real-time output

**What to watch for:**
- Channel connection status
- API errors
- Session creation messages

### 10.2. Download Logs
```bash
# With persistent volume configured
scp -i ~/.ssh/id_rsa root@xx.xxx.xx.xxx:/var/lib/docker/volumes/openclaw-data/_data/logs/*.log ~/Downloads/
```

### 10.3. Run Doctor
Check for configuration issues:
```bash
docker exec CONTAINER_ID openclaw doctor
```

---

## 11. Updating

### 11.1. Auto-Deploy (Disabled)

> [!IMPORTANT]
> **Keep Automatic Deployment OFF.** OpenClaw is a standalone external project — you don't want it to rebuild every time you push changes to your main repository.

To disable auto-deploy in Coolify:
1. Go to your OpenClaw application
2. Navigate to **General** tab
3. Ensure **Automatic Deployment** is **OFF**

### 11.2. Manual Update (Recommended)
1. Go to Coolify dashboard
2. Select OpenClaw application
3. Click **Deploy** when you want to update

### 11.3. Version Channels
OpenClaw has three release channels:

| Channel | Description | npm tag |
|---------|-------------|---------|
| `stable` | Tagged releases (`vYYYY.M.D`) | `latest` |
| `beta` | Prerelease versions | `beta` |
| `dev` | Bleeding edge | `dev` |

---

## 12. Common Issues

### Issue: Build Fails - "pnpm not found"
**Solution:** Ensure Dockerfile installs pnpm globally before running install.

### Issue: Gateway Not Starting
**Solution:** 
1. Check `GATEWAY_BIND` is set to `0.0.0.0` (not `127.0.0.1`)
2. Verify port 18789 is exposed

### Issue: WhatsApp "Session Expired"
**Solution:**
1. Delete the session data in `/home/node/.openclaw/credentials/whatsapp`
2. Restart container
3. Scan new QR code

### Issue: WebSocket Connection Refused
**Solution:**
1. Verify Coolify domain is pointing to correct IP
2. Check SSL certificate is valid
3. Ensure container health check is passing

### Issue: "Model not configured"
**Solution:** Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in environment variables.

### Issue: "disconnected (1008): pairing required"

> [!IMPORTANT]
> This is the most common error when deploying OpenClaw behind a reverse proxy like Coolify.

**What's Happening:**
OpenClaw requires "device pairing" for new WebSocket connections. By default, pairing is auto-approved for local/loopback connections, but remote connections through a reverse proxy are treated as **new devices requiring manual approval**. Your browser connecting through Coolify's Traefik proxy is seen as an unknown device.

**Solution (Automated - Recommended):**
The provided `docker-entrypoint.sh` script includes this fix automatically:
```json
{
  "gateway": {
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true
    }
  }
}
```

This disables the device authentication requirement for the Control UI, allowing browser access via the token alone.

**Alternative Solution (Manual Pairing):**
If you prefer not to disable device auth, you can manually approve your device:

1. **Access the Coolify Terminal:**
   - Go to your OpenClaw application → **Servers** → **Terminal**
   
2. **List pending pairing requests:**
   ```bash
   node dist/index.js nodes pending
   ```
   
3. **Approve your device:**
   ```bash
   node dist/index.js nodes approve <requestId>
   ```
   
4. **Refresh** your browser (you may need to clear cache)

**If Terminal is Disabled:**
If Coolify's terminal isn't available, you can SSH into your server and run:
```bash
docker exec -it <container-id> node dist/index.js nodes pending
docker exec -it <container-id> node dist/index.js nodes approve <requestId>
```

> [!NOTE]
> Once pairing is approved, your device is remembered. You won't need to repeat this process unless you clear the persistent storage or access from a new device.

---

## 13. Maintenance

To prevent the server from filling up, regularly check your disk usage and clean up Docker artifacts.

### SSH into Coolify server (OpenClaw/Agents)
ssh -i ~/.ssh/id_rsa root@xx.xxx.xx.xxx

### 13.1. Check Disk Space
Run this command to see how much space is left:
```bash
df -h
```
*(Look at the Usage % for `/`)*

### 13.2. Clean Up (Prune)
Run this command to remove unused images and build cache:
```bash
docker system prune -a -f
```
*(This removes unused images and stopped containers. It does NOT delete your volumes/database data.)*

**Automate (Optional Cron Job):**
To run this automatically every night at 4 AM:
1.  Run `crontab -e`
2.  Add: `0 4 * * * docker system prune -a -f > /dev/null 2>&1`

---

## 14. Troubleshooting

If a deployment breaks:

1. **Coolify UI:**
   - Go to **Deployments** tab
   - Click on a previous working deployment
   - Click **Redeploy**

2. **Switch to Stable Channel:**
   Update Dockerfile to pin a specific version:
   ```dockerfile
   RUN npm install -g openclaw@stable
   ```

---

## 14. Production Checklist

Before going live:

- [ ] Configure all desired channels
- [ ] Set up DM allowlists
- [ ] Configure persistent volume
- [ ] Test each channel connectivity
- [ ] Run `openclaw doctor` to verify config
- [ ] Set up monitoring/alerting
- [ ] Document channel-specific credentials

---

## 15. Additional Resources

- **OpenClaw Docs:** https://docs.openclaw.ai
- **Getting Started:** https://docs.openclaw.ai/start/getting-started
- **Configuration Reference:** https://docs.openclaw.ai/gateway/configuration
- **Security Guide:** https://docs.openclaw.ai/gateway/security
- **Discord Community:** https://discord.gg/clawd
- **GitHub:** https://github.com/openclaw/openclaw

---

**Deployment Status Template:**

```
🦞 OpenClaw Deployment
━━━━━━━━━━━━━━━━━━━━━━━━
✅ Build: Success
✅ Health Check: Passing
✅ Domain: f4gog4oo80kwg0ggwg008gs4.xx.xxx.xx.xxx.sslip.io
✅ SSL: Active
✅ Gateway: Running
✅ Channels: [telegram, discord]
━━━━━━━━━━━━━━━━━━━━━━━━
Ready for Production: YES
```
