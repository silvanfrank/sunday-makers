# Deploying Car Agent on Coolify

This guide outlines how to deploy the Car Affordability Agent using Coolify and connect it to your frontend.

## 1. Prepare the Repository

The Car Agent is part of your mono-repo at `/Car-Agent/`. Coolify will build from this subdirectory.

**Prerequisites:**
- Gemini API Key (get at: https://aistudio.google.com/app/apikey)
- GitHub repository pushed to `main` branch
- Coolify instance running at `coolify.longtermtrends.net`

---

## 2. Coolify Configuration

### 2.1. Create New Application
1. **Login** to [coolify.longtermtrends.net](https://coolify.longtermtrends.net)
2. **Create New Resource:** Application → **Public Repository**
3. **Repository Settings:**
   - **URL:** `https://github.com/silvanfrank/longtermtrends2`
   - **Branch:** `main`
   - **Build Pack:** **Dockerfile**

### 2.2. Build Settings
Navigate to **General** tab:

**Base Directory:**
```
/Car-Agent
```

**Dockerfile Location:**
```
/Car-Agent/Dockerfile
```

**Port Exposes:**
```
8000
```

**Port Mappings:**
```
8010:8000
```
*(Note: Port 8010 is suggested to avoid conflict if running locally, but internally Coolify manages routing via Traefik so the exposed port is handled by the domain)*

### 2.3. Environment Variables
Go to **Environment Variables** tab and add:

| Key | Value | Description |
|-----|-------|-------------|
| `GEMINI_API_KEY` | `your_actual_api_key` | Google Gemini API key |
| `PYTHONUNBUFFERED` | `1` | Prevents Python output buffering |

### 2.4. Domain Configuration
**Domain Settings:**
- **Protocol:** `https`
- **Domain:** `car.longtermtrends.com`
- **Wildcard:** No

**DNS Setup (Required):**
Add an A record in your DNS provider:
```
car.longtermtrends.com → [Your Coolify Server IP]
```

> [!NOTE]
> **Default Domain Behavior:**
> If you do not configure a custom domain (or DNS hasn't propagated), Coolify serves the app via a default `sslip.io` domain (e.g., `http://x848cw...xx.xxx.xx.xxx.sslip.io`).
>
> **Impact:** If you use this default domain, you **MUST** update the `apiUrl` in `car-agent.html` to match it, otherwise the frontend widget will fail to connect.


### 2.5. Deploy
1. Click **Deploy**
2. Watch the build logs for errors
3. Wait for health check to pass (`/health` endpoint)

---

## 3. Verification

### 3.1. Health Check
```bash
curl https://car.longtermtrends.com/health
```

### 3.2. API Documentation
```
https://car.longtermtrends.com/docs
```

---

## 4. Frontend Integration

### 4.1. Update CORS Settings
Ensure `execution/api.py` includes `https://longtermtrends.net` in `ALLOWED_ORIGINS`.

### 4.2. Verify Chatbox Configuration
In `longtermtrends/community/templates/community/car-agent.html`, ensure the API URL matches your deployment:

```javascript
const apiUrl = "https://car.longtermtrends.com/chat";
```

---

## 5. Testing the Deployment

### 5.1. Test the API Directly
```bash
curl -X POST https://car.longtermtrends.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "Hi, I am looking for a car",
    "user_name": "Test User"
  }'
```

**Expected:** JSON response with agent's greeting.

### 5.2. Test from Frontend
1. Navigate to `https://longtermtrends.net/car-agent-affordability`
2. Click "Check My Affordability" or open chat
3. Send a message
4. Verify response appears in chatbox

**Troubleshooting:**
- Open browser console (F12) and check for CORS errors
- Verify network tab shows requests to `car.longtermtrends.com`
- Check Coolify logs if no order

---

## 6. Monitoring & Logs

### 6.1. Persistent Volume for Logs
To keep conversation logs across restarts:

1. Go to **Storages** tab in Coolify.
2. Add Volume:
   - **Name:** `car-agent-logs`
   - **Source:** `/var/lib/docker/volumes/car-agent-logs/_data`
   - **Destination:** `/app/logs`
3. **Redeploy**.

### 6.2. Download Logs
```bash
scp -i ~/.ssh/id_rsa root@46.224.23.170:/var/lib/docker/volumes/car-agent-logs/_data/transcripts.jsonl ~/Downloads/car_transcripts.jsonl
```

---

## 7. Updating the Deployment

### 7.1. Push Changes to GitHub
```bash
cd /path/to/longtermtrends2/Car-Agent
# Make changes
git add .
git commit -m "Update Car Agent logic"
git push origin main
```

### 7.2. Trigger Redeploy in Coolify
1. Go to Coolify dashboard
2. Select Car Agent application
3. Click **Deploy** button (or enable auto-deploy on push)

**Auto-Deploy (Optional):**
- Enable **Automatic Deployment** in Coolify settings
- Every push to `main` will trigger a rebuild

---

## 8. Scaling & Performance

### 8.1. Session Management
Current implementation uses **in-memory sessions**:
- Sessions reset on container restart
- Not suitable for horizontal scaling

**For Production:**
Consider moving to Redis or database-backed sessions if scaling horrizontally.

### 8.2. Rate Limiting
Rate limiting can be added to `execution/api.py` if needed. Currently rely on Traefik/Coolify settings.

---

## 9. Security Checklist

- [x] API Key in environment variables (not in code)
- [x] CORS restricted to longtermtrends.net
- [x] HTTPS enforced via Coolify/Traefik
- [ ] Rate limiting enabled (optional)
- [ ] Logging excludes sensitive user data
- [x] Health check doesn't expose secrets

---

## 10. Common Issues

### Issue: Build Fails - "Dockerfile not found"
**Solution:** Check Base Directory path. Use `/Car-Agent` (absolute from repo root).

### Issue: Health Check Fails
**Solution:** Verify port 8000 is exposed in Dockerfile and mapped in Coolify.

### Issue: CORS Error in Browser
**Solution:** 
1. Check `ALLOWED_ORIGINS` in `execution/api.py`
2. Ensure frontend domain is whitelisted
3. Verify HTTPS (mixed content blocks requests)

### Issue: Gemini API Error
**Solution:**
1. Verify `GEMINI_API_KEY` is set in Coolify environment
2. Check API key has GenAI access enabled
3. Check Gemini quota/billing

---

## 11. Rollback Procedure

If a deployment breaks:

1. **Coolify UI:**
   - Go to **Deployments** tab
   - Click on a previous working deployment
   - Click **Redeploy**

2. **Git:**
   ```bash
   git revert HEAD
   git push origin main
   ```

---

## 12. Production Checklist

Before going live:

- [ ] Run unit tests (`python -m pytest tests/`)
- [ ] Verify 10% Rule calculations match expected values
- [ ] Check TCO tables for accuracy
- [ ] Monitor first 10 real conversations
- [ ] Set up error alerting (e.g., Slack/email for 500 errors)
- [ ] Document API endpoints for frontend team

---

## Additional Resources

- **Coolify Docs:** https://coolify.io/docs
- **Gemini Pricing:** https://ai.google.dev/pricing
- **Car Agent README:** `/Car-Agent/README.md`

---

## Deployment Status Template

```
🚗 Car Agent Deployment
━━━━━━━━━━━━━━━━━━━━━━━━
✅ Build: Success
✅ Health Check: Passing
✅ Domain: car.longtermtrends.com
✅ SSL: Active
✅ CORS: Configured
━━━━━━━━━━━━━━━━━━━━━━━━
Ready for Production: YES
```
