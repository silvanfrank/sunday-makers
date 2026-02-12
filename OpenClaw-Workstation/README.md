# OpenClaw Workstation

A full Linux desktop with OpenClaw AI pre-installed, accessible from your browser.

## What You Get

```
┌─────────────────────────────────────────────────────────────┐
│  Your Browser                                               │
│  https://workstation.your-domain.com                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  All-in-One Container                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Linux Desktop (Ubuntu XFCE)                        │    │
│  │  - Firefox, Terminal, File Manager                  │    │
│  │  - OpenClaw Gateway (background service)            │    │
│  │                                                     │    │
│  │  Access from inside:                                │    │
│  │  → http://localhost:18789     (OpenClaw Dashboard)  │    │
│  │  → http://localhost:3001+     (Dev Servers)         │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Key benefit:** Since OpenClaw runs *inside* the same container, any dev server it spins up is accessible at `localhost:PORT` from the desktop browser.

## Quick Start (Coolify)

1. **Create New Resource** → **Private Repository (with App)**
2. **Build Pack:** `Dockerfile`
3. **Base Directory:** `/docs/Longtermtrends-Content/Agents/OpenClaw-Workstation`
4. **Dockerfile Location:** `/Dockerfile`
5. **Ports Exposes:** `3000`

## Environment Variables

Set these in Coolify's Environment Variables tab:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENCLAW_TOKEN` | ✅ | Auth token (generate: `openssl rand -hex 32`) |
| `GEMINI_API_KEY` | ✅* | Google AI key |
| `ANTHROPIC_API_KEY` | ✅* | Anthropic key |
| `OPENAI_API_KEY` | ✅* | OpenAI key |
| `TELEGRAM_BOT_TOKEN` | ❌ | Telegram Bot Token |
| `BRAVE_API_KEY` | ❌ | Brave Search key |
| `WORKSTATION_PASSWORD` | ✅ | Desktop password (CRITICAL FOR SECURITY) |
| `CUSTOM_USER` | ❌ | Username (default: `abc`) |
| `TZ` | ❌ | Timezone (default: `Europe/Berlin`) |
| `OPENCLAW_LOG_LEVEL` | ❌ | File log level (`info`, `debug`, etc.) |
| `OPENCLAW_CONSOLE_LOG_LEVEL` | ❌ | Console log level (`info`, `debug`, etc.) |

*At least one AI key required

## Domains

| Service | Port | Domain |
|---------|------|----------------|
| `workstation` | 3000 | `https://w04ko4scws0sosogooocs8s8.46.224.23.170.sslip.io` |

> OpenClaw is now accessed from *inside* the desktop at `localhost:18789`, not via a separate domain.

## Usage

1. **Access the Desktop:** Open [Workstation URL](https://w04ko4scws0sosogooocs8s8.46.224.23.170.sslip.io) in your browser.
   - **Username:** `abc`
   - **Password:** [Your `WORKSTATION_PASSWORD`]
2. **Open Firefox** (pre-installed in the desktop).
3. **Access OpenClaw:** Go to `http://localhost:18789/chat?session=main&token=YOUR_TOKEN`
   > **Note:** You MUST include the `token` parameter in the URL to authenticate.
4. **Dev Servers:** Any server OpenClaw starts is accessible at `http://localhost:PORT`

## Files

```
OpenClaw-Workstation/
├── Dockerfile             # Webtop + OpenClaw (all-in-one)
├── docker-compose.yml     # Single service deployment
├── docker-entrypoint.sh   # OpenClaw startup script
├── .env.example           # Environment template
├── DEPLOY_COOLIFY.md      # Detailed deployment guide
└── README.md              # This file
```

## How It Works

1. Container starts with LinuxServer.io's Webtop base image (Ubuntu KDE)
2. Our custom script (`openclaw-run`) runs via S6 overlay's `services.d` to keep OpenClaw running.
3. OpenClaw gateway starts in background on port 18789
4. You access the desktop via browser on port 3000
5. From inside the desktop, `localhost:18789` = OpenClaw, `localhost:3001+` = dev servers

## Technical Details

We use several configuration overrides to make OpenClaw work smoothly in this containerized "inception" environment:

- **Service Management**: OpenClaw is now fully integrated as an S6 service (`/etc/services.d/openclaw/run`). This replaces the previous `custom-cont-init.d` approach.
  - Usage of `exec` ensures simple process monitoring and signal propagation.
  - Automatic restart on failure.
- **Permissions**: We force ownership of the `/config` directory to user `911` (abc/ubuntu) and set `chmod 755` so the desktop user (and local apps) can read the auto-generated config/token.
- **Environment**: `HOME` is explicitly set to `/config` for the OpenClaw process to ensure persistent state handling matches the container's volume strategy.
- **Persistent Logs**: Logs are now moved from `/tmp` to `/config/.openclaw/logs/openclaw.log` to survive container restarts.
- **Safe Config Merging**: The startup script now respects existing tokens and settings in `openclaw.json` unless explicitly overridden by environment variables.
- **Cleanups**: `xfce4-power-manager` was removed from the Dockerfile to prevent "Permission denied" errors impacting the dbus/logging services in the unprivileged container environment.

### 4.1. Tips & Tricks

**Copy/Paste (Clipboard)**
- **Chrome/Edge**: Text usually syncs automatically.
- **Firefox/Safari**:
  1. Open the **Sidebar Menu** (click the arrow on the left edge or swipe right).
  2. Click the **Clipboard** icon.
  3. Paste your text into the text box there.
  4. Now you can paste (`Ctrl+V`) inside the Linux desktop.

### Configuration Notes (What We Tried)

Attempts to configure the following keys resulted in boot failures (Schema Validation Error: "Unrecognized key"):

- `gateway.allowedHosts` (intended to allow all host headers)
- `gateway.auth.dangerouslyDisableDeviceAuth` (intended to bypass device trust)

These keys appear to be unsupported in the current OpenClaw version installed by the container. We have reverted to standard token authentication.

## Security

> [!WARNING]
> The desktop is accessible to anyone with the URL. Set `WORKSTATION_PASSWORD` for protection, or use Coolify's Basic Auth feature.

## Troubleshooting

### OpenClaw not starting
Check the gateway log inside the desktop:
```bash
cat /config/.openclaw/logs/openclaw.log
```

### Desktop is slow
- Use Chrome or Edge (better than Firefox for streaming)
- Ensure VPS has 4GB+ RAM
- Check network latency to your VPS

### Can't find OpenClaw CLI
Open terminal in the desktop and run:
```bash
openclaw --version
openclaw doctor
```
