# Deploying OpenClaw Workstation on Coolify (SECURE)

This guide outlines how to deploy the **OpenClaw Workstation** — a full Linux desktop with integrated OpenClaw AI — using Coolify.

## 1. Overview

**All-in-One Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│  Your Browser                                               │
│  https://workstation.your-domain.com                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Single Container                                [Port 3000]│
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Linux Desktop (Ubuntu XFCE)                        │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │  OpenClaw Gateway (background, port 18789)  │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                     │    │
│  │  Firefox → http://localhost:18789 (OpenClaw)        │    │
│  │  Firefox → http://localhost:3001  (Dev Server)      │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Why all-in-one?** When OpenClaw runs `npm start` on port 3001, it starts inside the same container. From the desktop's browser, you access it at `localhost:3001` — no network gymnastics needed.

---

## 2. Prerequisites

- **Coolify instance** running
- **LLM API Key** (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY`)
- **4GB+ RAM** on your VPS (recommended for smooth desktop experience)

---

## 3. Coolify Configuration

### 3.1. Create New Application
1. **Login** to your Coolify dashboard
2. **Create New Resource:** Application → **Private Repository (with App)**
3. **Repository Settings:**
   - **Source:** select your connected Git App
   - **Repository:** `silvanfrank/longtermtrends2`
   - **Branch:** `master`
   - **Build Pack:** **Dockerfile**  ← IMPORTANT!

### 3.2. Build Settings
Navigate to **General** tab:

| Setting | Value |
|---------|-------|
| **Base Directory** | `/docs/Longtermtrends-Content/Agents/OpenClaw-Workstation` |
| **Dockerfile Location** | `/Dockerfile` |

**Network Settings:**
| Setting | Value |
|---------|-------|
| **Ports Exposes** | `3000` |
| **Ports Mappings** | `3000:3000` |

**Custom Docker Options:**
(This is critical to prevent Plasma crashes)
```bash
--shm-size=2g
```
> [!IMPORTANT]
> **Don't skip this!** Browsers like Firefox/Chrome will crash or cause disconnects (Error 1006) if shared memory is too small (default is 64MB).

### 3.3. Environment Variables
Go to **Environment Variables** tab and add:

#### Required Secrets
| Key | Value | Description |
|-----|-------|-------------|
| `OPENCLAW_TOKEN` | (generate) | Auth token for OpenClaw dashboard |

> [!TIP]
> Generate a secure token with: `openssl rand -hex 32`

#### AI Configuration (At least one required)
| Key | Value | Description |
|-----|-------|-------------|
| `GEMINI_API_KEY` | `AIza...` | Google AI Key |
| `ANTHROPIC_API_KEY` | `sk-ant...` | Anthropic Key |
| `OPENAI_API_KEY` | `sk-...` | OpenAI Key |
| `BRAVE_API_KEY` | `BSA...` | Brave Search (for web search) |
| `TELEGRAM_BOT_TOKEN` | `859...` | Telegram Bot Token (Optional) |

#### Optional Settings
| Key | Value | Description |
|-----|-------|-------------|
| `TZ` | `Europe/Berlin` | Timezone for the desktop |
| `WORKSTATION_PASSWORD` | `yourpassword` | Password to access the desktop (REQUIRED) |
| `CUSTOM_USER` | `abc` | Username for the desktop (Default: `abc`) |
| `OPENCLAW_LOG_LEVEL` | `info` | File log level (`debug`, `info`, `warn`, `error`, `trace`) |
| `OPENCLAW_CONSOLE_LOG_LEVEL` | `info` | Console log level (`debug`, `info`, `warn`, `error`, `trace`) |

> [!CAUTION]
> Never commit API keys to Git. Use Coolify's environment variables exclusively.

### 3.4. Domain Configuration

You only need **one domain** for the workstation:

**Service: workstation**
- **Port:** `3000`
- **Domain:** `https://w04ko4scws0sosogooocs8s8.46.224.23.170.sslip.io`

> OpenClaw is accessed from *inside* the desktop at `localhost:18789`, not via a separate external domain.

### 3.5. Deploy
1. Click **Deploy**
2. Watch build logs. It will:
   - Build custom image (Webtop + Node.js + OpenClaw)
   - Start the container
3. Wait for health checks to pass

**Build Time:** ~5-8 minutes (first build installs Node.js and OpenClaw)

---

## 4. Post-Deployment Setup

### 4.1. Access the Desktop

1. **Navigate to your workstation domain:**
   ```
   https://w04ko4scws0sosogooocs8s8.46.224.23.170.sslip.io
   ```

2. **Login Information:**
   - **Username:** `abc` (Default for LinuxServer.io)
   - **Password:** [The value of `WORKSTATION_PASSWORD` you set in Coolify]

3. **You'll see a full Ubuntu KDE desktop** with:
   - Firefox browser
   - Terminal
   - File Manager
   - And more...

### 4.2. Access OpenClaw from Inside the Desktop

1. **Open Firefox** (inside the desktop)
2. **Navigate to:**
   ```
   http://localhost:18789/chat?session=main&token=YOUR_OPENCLAW_TOKEN
   ```
   > **Important:** The URL **must** include the token to authenticate the session.
3. **You're now in the OpenClaw dashboard!**

### 4.3. Access Dev Servers

When OpenClaw spins up a dev server (e.g., on port 3001):
1. From inside the desktop, open Firefox
2. Go to `http://localhost:3001`

**It just works** because everything runs in the same container.

### 4.4. Tips & Tricks

**Copy/Paste (Clipboard)**
- **Chrome/Edge**: Text usually syncs automatically.
- **Firefox/Safari**:
  1. Open the **Sidebar Menu** (click the arrow on the left edge or swipe right).
  2. Click the **Clipboard** icon.
  3. Paste your text into the text box there.
  4. Now you can paste (`Ctrl+V`) inside the Linux desktop.

---

## 5. Persistent Storage

Docker Compose automatically handles volumes:

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `workstation-data` | `/config` | Desktop settings, Firefox profile, OpenClaw data |

The OpenClaw config lives at `/config/.openclaw/` inside the container. Logs are stored at `/config/.openclaw/logs/` and are persistent.

### 5.2. Configuration Persistence
The workstation now uses **Smart Merging**. This means:
1.  Manual edits you make to `/config/.openclaw/openclaw.json` (like Telegram pairing) **persist** across restarts.
2.  Settings in Coolify's Environment Variables will update the config on boot without wiping your manual changes.


---

## 6. Security

> [!WARNING]
> **The desktop UI is accessible to anyone with the URL!**

### Recommended Security Measures:

1. **Set `WORKSTATION_PASSWORD`** in environment variables (REQUIRED)
2. **Use Coolify's Basic Auth** feature on the workstation domain
3. **Use Tailscale** for private access (most secure)

---

## 7. Troubleshooting

### Issue: Gateway Timeout (504)
**Cause:** Coolify can't reach port 3000

**Solution:**
1. Go to Coolify → your application → Domains
2. Ensure port `3000` is mapped to your domain
3. Redeploy

### Issue: Disconnected (Error 1006)
**Cause:** This usually means the WebSocket connection was closed by the reverse proxy (Traefik/Coolify) or the browser crashed due to low resources.

**Solutions:**
1. **Increase Shared Memory:** Ensure `--shm-size=2g` is set in **General -> Custom Docker Options**. 
3. **Increase Proxy Timeouts (Recommended):**
   Go to your application in Coolify → **Labels** and REPLACE everything with these labels (adjusting the domain/router names to match your specific instance):

   ```yaml
   traefik.enable=true
   traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https
   traefik.http.routers.http-0-YOURSERVICE.entryPoints=http
   traefik.http.routers.http-0-YOURSERVICE.middlewares=redirect-to-https
   traefik.http.routers.http-0-YOURSERVICE.rule=Host(`game.example.com`) && PathPrefix(`/`)
   traefik.http.routers.http-0-YOURSERVICE.service=http-0-YOURSERVICE
   traefik.http.routers.https-0-YOURSERVICE.entryPoints=https
   
   # --- PREVENT 1006 DISCONNECTS ---
   traefik.http.middlewares.vnc-buffering.buffering.maxRequestBodyBytes=0
   traefik.http.middlewares.vnc-buffering.buffering.maxResponseBodyBytes=0
   traefik.http.middlewares.vnc-buffering.buffering.memRequestBodyBytes=0
   traefik.http.middlewares.vnc-buffering.buffering.memResponseBodyBytes=0
   traefik.http.routers.https-0-YOURSERVICE.middlewares=vnc-buffering
   # --------------------------------
   
   traefik.http.routers.https-0-YOURSERVICE.rule=Host(`game.example.com`) && PathPrefix(`/`)
   traefik.http.routers.https-0-YOURSERVICE.service=https-0-YOURSERVICE
   traefik.http.routers.https-0-YOURSERVICE.tls.certresolver=letsencrypt
   traefik.http.routers.https-0-YOURSERVICE.tls=true
   traefik.http.services.http-0-YOURSERVICE.loadbalancer.server.port=3000
   traefik.http.services.https-0-YOURSERVICE.loadbalancer.server.port=3000
   ```
   *(Note: This disables gzip and buffering, which are the main causes of disconnects.)*
3. **Check RAM Usage:** If the VPS is hitting 100% RAM, the VNC server might be killed.
4. **Disable Browser Sleeping:** If you leave the tab inactive, some browsers (like Edge/Chrome) "sleep" the tab, killing the socket. Keep the tab active or use a "No Sleep" extension.

### Issue: OpenClaw not starting
**Check the log inside the desktop:**
Check the **deployment logs in Coolify** or run:
```bash
cat /config/.openclaw/logs/openclaw.log
```

**Or check if the process is running:**
```bash
ps aux | grep openclaw
```

### Issue: Desktop is slow or laggy
- Use Chrome or Edge instead of Firefox (better WebSocket support)
- Ensure VPS has 4GB+ RAM
- Check network latency to your VPS

### Issue: "HTTPS required" error
- The Webtop image requires HTTPS
- Ensure your domain uses `https://` not `http://`
- Wait for Coolify to provision the SSL certificate (can take 1-2 minutes)

---

## 8. Maintenance

### Check Disk Space
```bash
df -h
docker system df
```

### View OpenClaw Logs
From inside the desktop:
**Option 1: In Coolify** (Recommended)
Just click the **Logs** tab in your deployed service (this shows STDOUT/STDERR).

**Option 2: Persistent File Logs** (Recommended for history)
From inside the desktop:
```bash
cat /config/.openclaw/logs/openclaw.log
tail -f /config/.openclaw/logs/openclaw.log
```

### Restart OpenClaw Gateway
From inside the desktop:
```bash
pkill -f "openclaw gateway"
openclaw gateway --bind lan --allow-unconfigured &
```

---

## 9. Files

```
OpenClaw-Workstation/
├── Dockerfile             # Webtop + OpenClaw (all-in-one image)
├── docker-compose.yml     # Single service deployment
├── docker-entrypoint.sh   # OpenClaw startup script
├── .env.example           # Environment template
├── DEPLOY_COOLIFY.md      # This file
└── README.md              # Quick overview
```

---

## 10. Production Checklist

Before going live:

- [ ] `OPENCLAW_TOKEN` set (strong, random)
- [ ] `WORKSTATION_PASSWORD` set (CRITICAL)
- [ ] At least one AI key configured
- [ ] Domain configured with HTTPS
- [ ] Persistent storage verified
- [ ] Test OpenClaw access from inside desktop
- [ ] Test dev server access from inside desktop

---

## 11. Additional Resources

- **LinuxServer.io Webtop:** https://docs.linuxserver.io/images/docker-webtop
- **OpenClaw Docs:** https://docs.openclaw.ai
- **OpenClaw Discord:** https://discord.gg/clawd
