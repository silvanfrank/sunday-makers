# Sunday Makers Repository

Welcome to the **Sunday Makers** repository. This collection houses advanced AI agents and tools designed for personal productivity, financial planning, and ecosystem automation.

## Projects

### 1. [Investment Co-Pilot](./Investment-Co-Pilot)
**An autonomous AI agent for evidence-based financial planning.**

The Investment Co-Pilot is designed to democratize high-quality financial education. It engages users in a conversation to understand their financial situation and goals, then generates a personalized **Investment Policy Statement (IPS)** based on academic principles and the "Simple. Cheap. Safe. Easy." philosophy.

*   **Core Logic:** Built on the DOE Framework (Directive, Orchestration, Execution).
*   **Features:** Lifecycle investing models, rule-based safety checks (debt, liquidity), and conflict-free portfolio generation.
*   **Tech Stack:** Python, FastAPI, Google Gemini.

### 2. [OpenClaw](./OpenClaw)
**A self-hosted, multi-channel personal AI assistant.**

OpenClaw connects your favorite messaging platforms (WhatsApp, Telegram, Discord, Slack, etc.) to a single, powerful AI assistant running on your own hardware. It acts as a unified "brain" for all your communications, ensuring privacy and control.

*   **Core Objective:** Provide a private, local-first assistant that lives where you chat.
*   **Features:** Multi-channel inbox, voice wake, skills platform, and browser control.
*   **Persistent Storage:** Data and sessions (e.g., WhatsApp login) are persisted across redeployments, ensuring no data loss.
*   **Tech Stack:** Node.js, TypeScript, Docker.

### 3. [OpenClaw Workstation](./OpenClaw-Workstation)
**A browser-accessible Linux desktop with OpenClaw pre-installed.**

This project provides a complete, containerized Linux desktop environment (Webtop) that includes OpenClaw. It allows for a consistent development and usage environment accessible directly from any web browser.

*   **Core Utility:** Access a full desktop via your browser with customizable development tools and OpenClaw ready to go.
*   **Features:** Ubuntu XFCE desktop, Firefox, Terminal, and automatic OpenClaw gateway startup.
*   **Persistent Storage:** Data and sessions (e.g., WhatsApp login) are persisted across redeployments, ensuring no data loss.
*   **Tech Stack:** Docker, KasmVNC/Webtop.

## Deployment

All projects in this repository are designed to be deployed using **Docker** and are optimized for **Coolify**. Detailed deployment instructions can be found in the `DEPLOY_COOLIFY.md` files within each project directory.
