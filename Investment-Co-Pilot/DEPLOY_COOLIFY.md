# Deploying Investment Co-Pilot on Coolify

This guide outlines how to deploy the Investment Co-Pilot agent using Coolify and connect it to your frontend.

## 1. Prepare the Repository
Ensure your project (Github Repo) is structured so Coolify can build it. The `Dockerfile` is already in the `Investment Co-Pilot` folder, but Coolify usually expects the Dockerfile at the root *or* you must specify the build context.

**Recommended:** Since this Agent is part of a mono-repo, you will configure Coolify to build from a subdirectory.

## 2. Coolify Configuration
1.  **Login** to [coolify.longtermtrends.net](https://coolify.longtermtrends.net).
2.  **Create New Resource:** Select **Application** -> **Public Repository** (or Private if you linked GitHub).
3.  **Repository URL:** `https://github.com/silvanfrank/longtermtrends2` (or your actual repo URL).
4.  **Branch:** `main` (or your working branch).
5.  **Build Pack:** Select **Dockerfile**.

### 2.1. Build Settings
In the Application settings page:
*   **Base Directory:** `/docs/Longtermtrends-Content/Agents/Investment Co-Pilot`
*   **Dockerfile Location:** `/docs/Longtermtrends-Content/Agents/Investment Co-Pilot/Dockerfile`
    *   *Note: Coolify concatenates Base Dir + Dockerfile Location automatically in some versions. If so, just use `/Dockerfile` relative to Base Directory.*
*   **Port:** `8000` (This matches our Dockerfile `EXPOSE` and `uvicorn` port).

### 2.2. Environment Variables (.env)
Go to the **Environment Variables** tab and add:
*   `GEMINI_API_KEY`: `[Your Actual Google Gemini API Key]`
*   `PYTHONUNBUFFERED`: `1`

### 2.3. Domain Configuration
*   **Protocol:** `https`
*   **Domain:** `agent.longtermtrends.com` (or `.com`)
*   *Coolify will automatically provision an SSL certificate for this subdomain.*

### 2.4. Deploy
Click **Deploy**. Watch the logs to ensure the build succeeds and the health check (`/health`) passes.

---

## 3. Frontend Integration
Once the agent is live at `https://agent.longtermtrends.com`, you need to update the frontend code to talk to this new endpoint.

### 3.1. Update `base.html`
Edit `longtermtrends/my_app/templates/my_app/bootstrap/base.html`:

```javascript
    <script>
      window.N8NbrandableChatbox.init({
        // UPDATE: Point to your new Coolify URL + /chat endpoint
        webhookUrl: "https://agent.longtermtrends.com/chat", 
        
        botName: "Investment Co-Pilot",
        // ... rest of config ...
      });
    </script>
```

### 3.2. CORS (Cross-Origin Resource Sharing)
**Crucial:** Your frontend is on `longtermtrends.net`, but your API is on `agent.longtermtrends.com`. The browser will block requests unless the API allows it.

**Action Required:**
You must update `execution/api.py` to allow CORS from your main domain.

**Update `execution/api.py`:**
```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(...)

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.longtermtrends.net", "https://longtermtrends.net", "http://localhost:8000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
*(I will apply this fix to the code for you in the next step).*

---

## 5. Monitoring & Logs

### 5.1. View Logs in Coolify
1. Go to your Investment Co-Pilot application
2. Click **Logs** tab
3. Monitor real-time output

**What to watch for:**
- Gemini API errors
- Session creation messages
- Tool execution logs

### 5.2. Persistent Volume for Logs (Required)

> [!CAUTION]
> Without a persistent volume, **all logs are lost** when the container restarts (on redeploy, crash, or server reboot).

**Configure in Coolify:**
1. Go to your Investment Co-Pilot application
2. Click **Storages** tab
3. Click **+ Add** to create a new volume
4. Configure:
   - **Name:** `investment-copilot-logs`
   - **Source (Host Path):** `/var/lib/docker/volumes/investment-copilot-logs/_data`
   - **Destination (Container Path):** `/app/logs`
5. Click **Save** and **Redeploy**

**Verify persistence:**
```bash
# After redeploy, check logs still exist
ssh -i ~/.ssh/id_rsa root@46.224.23.170
docker exec CONTAINER_ID ls -la /app/logs/
```

### 5.3. Download Conversation Logs

**Method 1: Direct Download (Recommended - requires persistent volume)**

If you configured the persistent volume in section 5.2, logs are on the host filesystem and can be downloaded directly:

```bash
scp -i ~/.ssh/id_rsa root@46.224.23.170:/var/lib/docker/volumes/investment-copilot-logs/_data/transcripts.jsonl ~/Downloads/transcripts.jsonl
```

**Method 2: Via Container (if persistent volume not configured)**

> [!NOTE]
> Coolify uses random container names. Find the correct container by searching for the command it runs.

First, find the container ID:
```bash
# SSH into server and find Investment Co-Pilot API container (look for "uvicorn execution")
ssh -i ~/.ssh/id_rsa root@46.224.23.170 'docker ps --format "table {{.ID}}\t{{.Command}}" | grep "uvicorn execution"'
```

Then download (replace `CONTAINER_ID` with the ID from above):
```bash
ssh -i ~/.ssh/id_rsa root@46.224.23.170 'docker cp CONTAINER_ID:/app/logs/transcripts.jsonl /tmp/transcripts.jsonl' && scp -i ~/.ssh/id_rsa root@46.224.23.170:/tmp/transcripts.jsonl ~/Downloads/transcripts.jsonl
```

> [!WARNING]
> If the log file doesn't exist in the container, it means no conversations have been logged yet, or the persistent volume wasn't configured before deployment.

---

## 6. Verification
1.  Go to `https://agent.longtermtrends.com/health`. You should see `{"status":"ok"}`.
2.  Open your website.
3.  Open the Chatbox and say "Hi".
4.  The request should go to the agent, the Agent should use Gemini to generate a response, and the reply should appear in the chatbox.
