# Deploying FIRE Agent on Coolify

This guide outlines how to deploy the FIRE Agent using Coolify and connect it to your frontend.

## 1. Prepare the Repository

The FIRE Agent is part of your mono-repo at `/FIRE-Agent/`. Coolify will build from this subdirectory.

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
/FIRE-Agent
```

**Dockerfile Location:**
```
/FIRE-Agent/Dockerfile
```
*Note: Some Coolify versions auto-concatenate Base Dir + Dockerfile. If so, use `./Dockerfile` or `/Dockerfile` relative to base.*

**Port Exposes:**
```
8000
```

**Port Mappings:**
```
8000:8000
```

### 2.3. Environment Variables
Go to **Environment Variables** tab and add:

| Key | Value | Description |
|-----|-------|-------------|
| `GEMINI_API_KEY` | `your_actual_api_key` | Google Gemini API key |
| `PYTHONUNBUFFERED` | `1` | Prevents Python output buffering |

**Security Note:** Never commit API keys to Git. Use Coolify's environment variables.

### 2.4. Domain Configuration
**Domain Settings:**
- **Protocol:** `https` (Coolify auto-provisions SSL via Let's Encrypt)
- **Domain:** `fire.longtermtrends.com` (or your preferred subdomain)
- **Wildcard:** No

**DNS Setup (Required):**
Before deploying, add an A record in your DNS provider:
```
fire.longtermtrends.com → [Your Coolify Server IP]
```

### 2.5. Deploy
1. Click **Deploy**
2. Watch the build logs for errors
3. Wait for health check to pass (`/health` endpoint)

**Build Time:** ~2-3 minutes

---

## 3. Verification

### 3.1. Health Check
Once deployed, verify the API is running:

```bash
curl https://fire.longtermtrends.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "gemini_configured": true,
  "active_sessions": 0
}
```

### 3.2. API Documentation
Visit the auto-generated docs:
```
https://fire.longtermtrends.com/docs
```

You should see Swagger UI with available endpoints.

---

## 4. Frontend Integration

### 4.1. Update CORS Settings
The FIRE Agent already includes CORS middleware in `execution/api.py`:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://longtermtrends.net",
    "https://agent.longtermtrends.net"
]
```

**Action:** If your domain is different, add it to `ALLOWED_ORIGINS` before deploying.

### 4.2. Create Frontend Page
Create `fire-agent.html` in your Django templates:
```
longtermtrends/community/templates/community/fire-agent.html
```

### 4.3. Update Chatbox Configuration
In your `fire-agent.html`, configure the chatbox to point to the deployed API:

```javascript
<script>
  initFIREAgent({
    apiUrl: "https://fire.longtermtrends.com/chat",  // Your Coolify domain
    user_email: "{{ request.user.email|default:''|escapejs }}",
    user_name: "{{ request.user.first_name|default:request.user.username|escapejs }}",
    user_id: "{{ request.user.id|default:''|escapejs }}"
  });
</script>
```

---

## 5. Testing the Deployment

### 5.1. Test the API Directly
```bash
curl -X POST https://fire.longtermtrends.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "Hi, I want to retire early",
    "user_name": "Test User"
  }'
```

**Expected:** JSON response with agent's greeting.

### 5.2. Test from Frontend
1. Navigate to `https://longtermtrends.net/fire-agent`
2. Click "Start FIRE Agent"
3. Send a message
4. Verify response appears in chatbox

**Troubleshooting:**
- Open browser console (F12) and check for CORS errors
- Verify network tab shows requests to `fire.longtermtrends.com`
- Check Coolify logs if no response

---

## 6. Monitoring & Logs

### 6.1. View Logs in Coolify
1. Go to your FIRE Agent application
2. Click **Logs** tab
3. Monitor real-time output

**What to watch for:**
- Gemini API errors
- Session creation messages
- Tool execution logs

### 6.2. Persistent Volume for Logs (Required)

> [!CAUTION]
> Without a persistent volume, **all logs are lost** when the container restarts (on redeploy, crash, or server reboot).

**Configure in Coolify:**
1. Go to your FIRE Agent application
2. Click **Storages** tab
3. Click **+ Add** to create a new volume
4. Configure:
   - **Name:** `fire-agent-logs`
   - **Source (Host Path):** `/var/lib/docker/volumes/fire-agent-logs/_data`
   - **Destination (Container Path):** `/app/logs`
5. Click **Save** and **Redeploy**

**Verify persistence:**
```bash
# After redeploy, check logs still exist
ssh -i ~/.ssh/id_rsa root@46.224.23.170
docker exec 7626aa44a8cc ls -la /app/logs/
```

### 6.3. Download Conversation Logs

**Method 1: Direct Download (Recommended - requires persistent volume)**

If you configured the persistent volume in section 6.2, logs are on the host filesystem and can be downloaded directly:

```bash
scp -i ~/.ssh/id_rsa root@46.224.23.170:/var/lib/docker/volumes/fire-agent-logs/_data/transcripts.jsonl ~/Downloads/transcripts.jsonl
```

**Method 2: Via Container (if persistent volume not configured)**

> [!NOTE]
> Coolify uses random container names (not "fire-agent"). Find the correct container by searching for the command it runs.

First, find the container ID:
```bash
# SSH into server and find FIRE Agent API container (look for "uvicorn execution")
ssh -i ~/.ssh/id_rsa root@46.224.23.170 'docker ps --format "table {{.ID}}\t{{.Command}}" | grep "uvicorn execution"'
```

**Example output:**
```
d01ea13fc62e   "uvicorn execution.a…"   # ← This is the FIRE Agent API container
```

Then download (replace `CONTAINER_ID` with the ID from above):
```bash
ssh -i ~/.ssh/id_rsa root@46.224.23.170 'docker cp CONTAINER_ID:/app/logs/transcripts.jsonl /tmp/transcripts.jsonl' && scp -i ~/.ssh/id_rsa root@46.224.23.170:/tmp/transcripts.jsonl ~/Downloads/transcripts.jsonl
```

> [!WARNING]
> If the log file doesn't exist in the container, it means no conversations have been logged yet, or the persistent volume wasn't configured before deployment.

---

## 7. Updating the Deployment

### 7.1. Push Changes to GitHub
```bash
cd /path/to/longtermtrends2/FIRE-Agent
# Make changes
git add .
git commit -m "Update FIRE Agent logic"
git push origin main
```

### 7.2. Trigger Redeploy in Coolify
1. Go to Coolify dashboard
2. Select FIRE Agent application
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
Consider moving to Redis or database-backed sessions.

### 8.2. Rate Limiting
Add rate limiting to prevent API abuse:

```python
# In execution/api.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def chat(request: Request, ...):
    ...
```

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
**Solution:** Check Base Directory path. Use `/FIRE-Agent` (absolute from repo root).

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

### Issue: Session Not Persisting
**Expected:** Sessions reset on container restart (by design).
**Solution:** For production, implement Redis-backed sessions.

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

- [ ] Test all test cases (see `test_cases.md`)
- [ ] Verify FIRE calculations are accurate
- [ ] Check legal disclaimer is displayed
- [ ] Monitor first 10 real conversations
- [ ] Set up error alerting (e.g., Slack/email for 500 errors)
- [ ] Document API endpoints for frontend team
- [ ] Run load test (simulate 100 concurrent users)

---

## Additional Resources

- **Coolify Docs:** https://coolify.io/docs
- **Gemini Pricing:** https://ai.google.dev/pricing
- **FIRE Agent README:** `/FIRE-Agent/README.md`
- **Test Cases:** `/docs/Longtermtrends-Content/Agents/FIRE-Agent/test_cases.md`

---

**Deployment Status Template:**

```
🚀 FIRE Agent Deployment
━━━━━━━━━━━━━━━━━━━━━━━━
✅ Build: Success
✅ Health Check: Passing
✅ Domain: fire.longtermtrends.com
✅ SSL: Active
✅ CORS: Configured
━━━━━━━━━━━━━━━━━━━━━━━━
Ready for Production: YES
```
