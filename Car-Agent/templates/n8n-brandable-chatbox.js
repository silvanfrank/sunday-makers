(() => {
  const N8NbrandableChatbox = (() => {
    const defaultOptions = {
      webhookUrl: "",
      method: "POST",
      headers: {},
      brandColor: "#2563eb",
      accentColor: "#0ea5e9",
      botName: "Chatbox",
      botAvatarUrl: "",
      userAvatarUrl: "",
      welcomeMessage: "Hi! How can I help you?",
      launcherText: "",
      launcherVariant: "icon", // 'icon' | 'text' | 'icon-text'
      position: "right", // 'right' | 'left'
      zIndex: 999999,
      openByDefault: false,
      placeholder: "Type your message...",
      storageKey: "n8n-brandable-chatbox",
      typingIndicatorText: "Typing...",
      darkMode: false,
      allowHTMLInResponses: false,
      extraContext: {},
      onEvent: null, // (eventName, data) => void
      transformRequest: null, // (text, ctx) => payload
      transformResponse: null, // (data) => string | { text, html }
      maxMessages: 200,
      sessionTtlMinutes: 0, // 0 disables inactivity expiration
      feedbackUrl: ""
    };

    function generateSessionId() {
      return "bc_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
    }

    function sanitizeHtml(unsafeHtml) {
      const temp = document.createElement("div");
      temp.innerHTML = unsafeHtml;
      const scripts = temp.querySelectorAll("script, style, iframe, object, embed");
      scripts.forEach((el) => el.remove());
      const treeWalker = document.createTreeWalker(temp, NodeFilter.SHOW_ELEMENT, null);
      while (treeWalker.nextNode()) {
        const el = treeWalker.currentNode;
        [...el.attributes].forEach((attr) => {
          if (/^on/i.test(attr.name)) el.removeAttribute(attr.name);
        });
      }
      return temp.innerHTML;
    }

    function createShadowRoot(zIndex) {
      const host = document.createElement("div");
      host.setAttribute("data-bc-root", "true");
      host.style.all = "initial";
      host.style.position = "fixed";
      host.style.zIndex = String(zIndex);
      document.body.appendChild(host);
      return host.attachShadow({ mode: "open" });
    }

    function createStyles(options) {
      const css = `
      :host { all: initial; }
      *, *::before, *::after { box-sizing: border-box; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }
      
      /* Container - ensure it's always positioned relative to viewport */
      .bc-container { 
        position: fixed !important; 
        ${options.position === "left" ? "left" : "right"}: max(20px, env(safe-area-inset-${options.position === "left" ? "left" : "right"}, 20px)); 
        bottom: max(20px, env(safe-area-inset-bottom, 20px)) !important; 
        z-index: ${options.zIndex};
        pointer-events: none;
      }
      
      /* Ensure launcher and panel have pointer events */
      .bc-launcher, .bc-panel { pointer-events: auto; }

      /* Launcher */
      .bc-launcher {
        display: inline-flex; align-items: center; justify-content: center;
        width: 56px; height: 56px; border-radius: 9999px; border: none; cursor: pointer;
        background: linear-gradient(135deg, ${options.brandColor} 0%, ${options.accentColor} 100%);
        color: #fff; box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
        will-change: transform;
        position: relative;
        z-index: 1;
      }
      .bc-launcher:hover { transform: translateY(-2px); box-shadow: 0 16px 36px rgba(0,0,0,0.28); filter: brightness(1.03); }
      .bc-launcher:active { transform: translateY(0); box-shadow: 0 8px 20px rgba(0,0,0,0.22); }
      .bc-launcher:focus-visible { outline: 3px solid ${options.accentColor}; outline-offset: 2px; }
      .bc-launcher svg { width: 26px; height: 26px; }
      .bc-launcher.bc-launcher--text { width: auto; height: 44px; padding: 0 14px; font-weight: 600; font-size: 14px; border-radius: 9999px; }
      .bc-launcher.bc-launcher--icon-text { width: auto; height: 44px; padding: 0 12px; gap: 8px; border-radius: 9999px; }
      .bc-launcher span { line-height: 1; }

      /* Panel - ensure it's positioned correctly relative to launcher */
      .bc-panel {
        position: absolute !important; 
        ${options.position === "left" ? "left" : "right"}: 0; 
        bottom: 72px;
        width: min(600px, calc(100vw - 40px));
        min-height: 340px;
        max-height: min(85vh, 1200px);
        border-radius: 16px; overflow: hidden; box-shadow: 0 24px 64px rgba(0,0,0,0.30);
        background: ${options.darkMode ? "rgba(11,18,32,0.88)" : "rgba(255,255,255,0.92)"};
        -webkit-backdrop-filter: saturate(160%) blur(16px);
        backdrop-filter: saturate(160%) blur(16px);
        color: ${options.darkMode ? "#f5f7fb" : "#0b1220"};
        display: flex; flex-direction: column; border: 1px solid ${options.darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.07)"};
        opacity: 1; transform: translateY(0); transition: opacity 220ms ease, transform 220ms ease;
        z-index: 2;
      }
      .bc-panel.hidden { opacity: 0; transform: translateY(8px); pointer-events: none; }

      /* Header */
      .bc-header {
        display: flex; align-items: center; gap: 10px; padding: 12px 14px;
        background: ${options.darkMode ? "linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0))" : "linear-gradient(180deg, rgba(0,0,0,0.03), rgba(0,0,0,0))"};
        border-bottom: 1px solid ${options.darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)"};
      }
      .bc-title { font-weight: 700; font-size: 14px; line-height: 1.2; letter-spacing: 0.2px; }
      .bc-sub { font-size: 12px; opacity: 0.75; position: relative; padding-left: 14px; }
      .bc-sub::before { content: ""; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 8px; height: 8px; border-radius: 9999px; background: #22c55e; box-shadow: 0 0 0 4px rgba(34,197,94,0.15); }
      .bc-header .bc-avatar {
        width: 28px; height: 28px; border-radius: 9999px; overflow: hidden; background: ${options.brandColor}; display: inline-flex; align-items: center; justify-content: center; color: #fff; font-weight: 700;
      }
      .bc-close { margin-left: auto; background: transparent; border: none; color: inherit; cursor: pointer; opacity: 0.7; transition: opacity 150ms ease, transform 150ms ease; }
      .bc-close:hover { opacity: 1; transform: scale(1.05); }

      /* Messages */
      .bc-messages { padding: 14px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; flex: 1 1 auto; }
      .bc-msg { display: flex; align-items: flex-start; gap: 8px; max-width: 90%; animation: bc-fade-in 180ms ease; }
      .bc-msg-user { align-self: flex-end; flex-direction: row-reverse; }
      .bc-bubble img { max-width: 100%; height: auto; border-radius: 8px; margin-top: 8px; }
      .bc-bubble { padding: 12px 14px; border-radius: 14px; line-height: 1.5; font-size: 14px; white-space: pre-wrap; overflow-wrap: break-word; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
      .bc-bubble-user { background: linear-gradient(135deg, ${options.brandColor} 0%, ${options.accentColor} 100%); color: #fff; border-bottom-right-radius: 4px; }
      .bc-bubble-bot { background: ${options.darkMode ? "rgba(255,255,255,0.06)" : "#f4f6fb"}; color: inherit; border-bottom-left-radius: 4px; border: 1px solid ${options.darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.04)"}; white-space: normal; }
      .bc-msg .bc-mini-avatar { width: 22px; height: 22px; min-width: 22px; min-height: 22px; flex: 0 0 22px; border-radius: 9999px; overflow: hidden; background: ${options.darkMode ? "#1f2937" : "#e5e7eb"}; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; color: ${options.darkMode ? "#e5e7eb" : "#111827"}; box-shadow: inset 0 0 0 1px ${options.darkMode ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)"}; }
      .bc-msg .bc-mini-avatar img { width: 100%; height: 100%; object-fit: cover; display: block; }
      .bc-typing { font-size: 12px; opacity: 0.75; animation: bc-pulse 1.2s ease-in-out infinite; }
      
      /* Markdown element spacing overrides */
      .bc-bubble p { margin: 0 0 8px 0; }
      .bc-bubble p:last-child { margin-bottom: 0; }
      .bc-bubble ul, .bc-bubble ol { margin: 0 0 8px 0; padding-left: 20px; }
      .bc-bubble li { margin: 4px 0; }
      
      /* Markdown Enhancements */
      .bc-bubble strong, .bc-bubble b { font-weight: 600; }
      .bc-bubble em, .bc-bubble i { font-style: italic; }
      .bc-bubble h1, .bc-bubble h2, .bc-bubble h3, .bc-bubble h4 { margin: 12px 0 8px; font-weight: 700; line-height: 1.3; }
      .bc-bubble h1 { font-size: 1.25em; }
      .bc-bubble h2 { font-size: 1.1em; }
      .bc-bubble h3 { font-size: 1em; }
      
      .bc-bubble a { color: ${options.accentColor}; text-decoration: underline; }
      .bc-bubble a:hover { opacity: 0.8; }
      
      .bc-bubble blockquote { border-left: 3px solid ${options.accentColor}; margin: 8px 0; padding-left: 12px; opacity: 0.8; }
      
      .bc-bubble pre { background: ${options.darkMode ? "rgba(0,0,0,0.3)" : "rgba(0,0,0,0.05)"}; padding: 10px; border-radius: 6px; overflow-x: auto; font-family: monospace; font-size: 0.9em; margin: 8px 0; }
      .bc-bubble code { font-family: monospace; background: ${options.darkMode ? "rgba(0,0,0,0.3)" : "rgba(0,0,0,0.05)"}; padding: 2px 4px; border-radius: 4px; font-size: 0.9em; }
      
      /* Tables */
      .bc-bubble table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 0.9em; display: block; overflow-x: auto; }
      .bc-bubble th, .bc-bubble td { padding: 6px 10px; border: 1px solid ${options.darkMode ? "rgba(255,255,255,0.15)" : "rgba(0,0,0,0.1)"}; text-align: left; }
      .bc-bubble th { background: ${options.darkMode ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.03)"}; font-weight: 600; }

      /* Input */
      .bc-input { border-top: 1px solid ${options.darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)"}; padding: 10px; display: flex; gap: 8px; align-items: center; background: ${options.darkMode ? "rgba(255,255,255,0.02)" : "rgba(255,255,255,0.7)"}; }
      .bc-input input[type="text"] { flex: 1 1 auto; border-radius: 12px; border: 1px solid ${options.darkMode ? "rgba(255,255,255,0.12)" : "rgba(0,0,0,0.12)"}; padding: 10px 12px; font-size: 16px; background: ${options.darkMode ? "rgba(255,255,255,0.03)" : "#ffffff"}; color: inherit; outline: none; transition: border-color 150ms ease, box-shadow 150ms ease; }
      .bc-input input[type="text"]:focus { border-color: ${options.accentColor}; box-shadow: 0 0 0 3px rgba(14,165,233,0.25); }
      .bc-input button { border: none; background: ${options.accentColor}; color: #fff; padding: 10px 12px; border-radius: 12px; cursor: pointer; font-weight: 600; transition: transform 120ms ease, box-shadow 120ms ease, filter 120ms ease; box-shadow: 0 6px 18px rgba(14,165,233,0.35); }
      .bc-input button:hover { transform: translateY(-1px); filter: brightness(1.03); }
      .bc-input button:active { transform: translateY(0); box-shadow: 0 4px 12px rgba(14,165,233,0.28); }

      /* Footer */
      .bc-badge { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; opacity: 0.7; }
      .bc-powered { padding: 8px 12px; text-align: center; font-size: 11px; opacity: 0.8; border-top: 1px solid ${options.darkMode ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)"}; background: ${options.darkMode ? "rgba(255,255,255,0.02)" : "rgba(255,255,255,0.7)"}; }
      .bc-powered a { color: ${options.accentColor}; text-decoration: none; }
      .bc-powered a:hover { text-decoration: underline; }

      /* Scrollbar */
      .bc-messages::-webkit-scrollbar { width: 10px; }
      .bc-messages::-webkit-scrollbar-track { background: transparent; }
      .bc-messages::-webkit-scrollbar-thumb { background: ${options.darkMode ? "rgba(255,255,255,0.15)" : "rgba(0,0,0,0.12)"}; border-radius: 9999px; }
      .bc-messages::-webkit-scrollbar-thumb:hover { background: ${options.darkMode ? "rgba(255,255,255,0.25)" : "rgba(0,0,0,0.22)"}; }

      /* Animations */
      @keyframes bc-fade-in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes bc-pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

      /* Mobile-specific improvements */
      @media (max-width: 768px) {
        .bc-container {
          ${options.position === "left" ? "left" : "right"}: max(16px, env(safe-area-inset-${options.position === "left" ? "left" : "right"}, 16px)) !important;
          bottom: max(16px, env(safe-area-inset-bottom, 16px)) !important;
        }
        .bc-panel {
          width: calc(100vw - 32px);
          max-height: 70vh;
          bottom: 68px;
        }
        .bc-launcher {
          width: 52px;
          height: 52px;
        }
        .bc-launcher svg {
          width: 24px;
          height: 24px;
        }
      }

      /* Ensure safe area support for mobile devices */
      @supports (padding: max(0px)) {
        .bc-container {
          ${options.position === "left" ? "left" : "right"}: max(20px, env(safe-area-inset-${options.position === "left" ? "left" : "right"}));
          bottom: max(20px, env(safe-area-inset-bottom));
        }
      }
      `;
      const style = document.createElement("style");
      style.textContent = css;
      return style;
    }

    function createUI(options, shadowRoot) {
      const container = document.createElement("div");
      container.className = "bc-container";

      const launcher = document.createElement("button");
      launcher.className = "bc-launcher";
      launcher.setAttribute("aria-label", options.launcherText || `Open ${options.botName}`);
      const iconSvg = `
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 3C7.03 3 3 6.58 3 11c0 2.43 1.23 4.61 3.19 6.11-.09.76-.39 2.02-1.31 3.16 0 0 2.06-.21 3.76-1.45.73.2 1.5.31 2.36.31 4.97 0 9-3.58 9-8s-4.03-8-9-8z" fill="currentColor"/>
        </svg>`;
      const launchText = options.launcherText || `Chat`;
      if (options.launcherVariant === 'text') {
        launcher.classList.add('bc-launcher--text');
        launcher.innerHTML = `<span>${launchText}</span>`;
      } else if (options.launcherVariant === 'icon-text') {
        launcher.classList.add('bc-launcher--icon-text');
        launcher.innerHTML = iconSvg + `<span>${launchText}</span>`;
      } else {
        launcher.innerHTML = iconSvg;
      }

      const panel = document.createElement("div");
      panel.className = "bc-panel hidden";

      const header = document.createElement("div");
      header.className = "bc-header";
      header.innerHTML = `
        <div class="bc-avatar">${options.botAvatarUrl ? `<img src="${options.botAvatarUrl}" alt="${options.botName}" style="width:100%;height:100%;object-fit:cover" />` : options.botName.slice(0,1).toUpperCase()}</div>
        <div>
          <div class="bc-title">${options.botName}</div>
          <div class="bc-sub">Online</div>
        </div>
        <button class="bc-close" aria-label="Close">&times;</button>
      `;

      const messages = document.createElement("div");
      messages.className = "bc-messages";

      const inputBar = document.createElement("form");
      inputBar.className = "bc-input";
      inputBar.innerHTML = `
        <input type="text" aria-label="Message input" placeholder="${options.placeholder}">
        <button type="submit">Send</button>
      `;

      panel.appendChild(header);
      panel.appendChild(messages);
      panel.appendChild(inputBar);

      if (options.feedbackUrl) {
        const powered = document.createElement("div");
        powered.className = "bc-powered";
        powered.innerHTML = `<a href="${options.feedbackUrl}" target="_blank" rel="noopener noreferrer">Report Issue / Feedback</a>`;
        panel.appendChild(powered);
      }
      container.appendChild(panel);
      container.appendChild(launcher);

      shadowRoot.appendChild(container);

      return { container, launcher, panel, header, messages, inputBar };
    }

    function scrollToBottom(el) {
      el.scrollTop = el.scrollHeight;
    }

    function createMessageElement({ role, text, html, botAvatarUrl, userAvatarUrl, allowHTMLInResponses }) {
      const row = document.createElement("div");
      row.className = `bc-msg ${role === "user" ? "bc-msg-user" : "bc-msg-bot"}`;

      const avatar = document.createElement("div");
      avatar.className = "bc-mini-avatar";
      if (role === "bot") {
        avatar.innerHTML = botAvatarUrl ? `<img src="${botAvatarUrl}" alt="bot" style="width:100%;height:100%;object-fit:cover" />` : "🤖";
      } else {
        avatar.innerHTML = userAvatarUrl ? `<img src="${userAvatarUrl}" alt="you" style="width:100%;height:100%;object-fit:cover" />` : "🧑";
      }

      const bubble = document.createElement("div");
      bubble.className = `bc-bubble ${role === "user" ? "bc-bubble-user" : "bc-bubble-bot"}`;

      if (html && allowHTMLInResponses) {
        bubble.innerHTML = sanitizeHtml(html);
      } else {
        bubble.textContent = text || "";
      }

      row.appendChild(avatar);
      row.appendChild(bubble);
      return row;
    }

    function loadState(storageKey) {
      try {
        const raw = localStorage.getItem(storageKey);
        if (!raw) return null;
        return JSON.parse(raw);
      } catch {
        return null;
      }
    }

    function saveState(storageKey, state) {
      try {
        localStorage.setItem(storageKey, JSON.stringify(state));
      } catch {
        // ignore
      }
    }

    function computeLastTimestampsFromHistory(history) {
      let lastBotAt = 0;
      let lastUserAt = 0;
      const now = Date.now();
      for (const msg of history || []) {
        // If older history doesn't carry timestamps, approximate with now
        if (msg.role === "bot") lastBotAt = msg.timestamp || now;
        if (msg.role === "user") lastUserAt = msg.timestamp || now;
      }
      return { lastBotAt, lastUserAt };
    }

    function init(userOptions) {
      const options = { ...defaultOptions, ...userOptions };
      if (!options.webhookUrl) {
        console.error("[N8NbrandableChatbox] Missing required option: webhookUrl");
        return;
      }

      const stored = loadState(options.storageKey) || {};
      let sessionId = stored.sessionId || generateSessionId();
      let history = Array.isArray(stored.history) ? stored.history.slice(-options.maxMessages) : [];
      // Inactivity TTL check
      if (options.sessionTtlMinutes && options.sessionTtlMinutes > 0) {
        const now = Date.now();
        const ttlMs = options.sessionTtlMinutes * 60 * 1000;
        const lastUserAt = stored.lastUserAt || 0;
        const lastBotAt = stored.lastBotAt || 0;
        const baseTime = lastUserAt || lastBotAt || 0;
        if (baseTime && now - baseTime > ttlMs) {
          // Expire session due to inactivity
          sessionId = generateSessionId();
          history = [];
        }
      }

      const shadowRoot = createShadowRoot(options.zIndex);
      const styleEl = createStyles(options);
      shadowRoot.appendChild(styleEl);
      const ui = createUI(options, shadowRoot);

      function persist() {
        const { lastBotAt, lastUserAt } = computeLastTimestampsFromHistory(history);
        saveState(options.storageKey, { sessionId, history, lastBotAt, lastUserAt });
      }

      function addMessage(role, content) {
        const entry = typeof content === "string" ? { role, text: content } : { role, ...content };
        entry.timestamp = Date.now();
        history.push(entry);
        while (history.length > options.maxMessages) history.shift();

        const node = createMessageElement({
          role,
          text: entry.text,
          html: entry.html,
          botAvatarUrl: options.botAvatarUrl,
          userAvatarUrl: options.userAvatarUrl,
          allowHTMLInResponses: options.allowHTMLInResponses
        });
        ui.messages.appendChild(node);
        scrollToBottom(ui.messages);
        persist();
        if (typeof options.onEvent === "function") options.onEvent("message", { role, entry });
      }

      function setTyping(isTyping) {
        const existing = ui.messages.querySelector('[data-typing="true"]');
        if (existing) existing.remove();
        if (isTyping) {
          const typing = document.createElement("div");
          typing.className = "bc-msg";
          typing.setAttribute("data-typing", "true");
          typing.innerHTML = `<div class="bc-mini-avatar">🤖</div><div class="bc-bubble bc-bubble-bot"><span class="bc-typing">${options.typingIndicatorText}</span></div>`;
          ui.messages.appendChild(typing);
          scrollToBottom(ui.messages);
        }
      }

      function reopenFromOption() {
        if (options.openByDefault) ui.panel.classList.remove("hidden");
      }

      // Restore history
      history.forEach((msg) => {
        const node = createMessageElement({
          role: msg.role,
          text: msg.text,
          html: msg.html,
          botAvatarUrl: options.botAvatarUrl,
          userAvatarUrl: options.userAvatarUrl,
          allowHTMLInResponses: options.allowHTMLInResponses
        });
        ui.messages.appendChild(node);
      });

      // Welcome
      if (!history.length && options.welcomeMessage) {
        if (options.allowHTMLInResponses && /<[a-z][\s\S]*>/i.test(options.welcomeMessage)) {
          addMessage("bot", { html: options.welcomeMessage });
        } else {
          addMessage("bot", { text: options.welcomeMessage });
        }
      }

      function buildPayload(userText) {
        const context = { sessionId, history: history.slice(-20), metadata: options.extraContext };
        if (typeof options.transformRequest === "function") {
          return options.transformRequest(userText, context);
        }
        return { message: userText, sessionId, metadata: options.extraContext };
      }

      async function sendToWebhook(userText) {
        setTyping(true);
        try {
          const payload = buildPayload(userText);
          const resp = await fetch(options.webhookUrl, {
            method: options.method,
            headers: { "Content-Type": "application/json", ...options.headers },
            body: options.method.toUpperCase() === "GET" ? undefined : JSON.stringify(payload),
            credentials: "omit",
            mode: "cors"
          });
          let data;
          const contentType = resp.headers.get("content-type") || "";
          if (contentType.includes("application/json")) {
            data = await resp.json();
          } else {
            data = { reply: await resp.text() };
          }

          let out = null;
          if (typeof options.transformResponse === "function") {
            out = options.transformResponse(data);
          } else {
            const text = data?.reply ?? data?.message ?? data?.text ?? data?.output ?? "";
            if (options.allowHTMLInResponses && typeof text === "string" && /<[^>]+>/.test(text)) {
              out = { html: text };
            } else {
              out = { text };
            }
          }

          setTyping(false);

          if (typeof out === "string") {
            if (options.allowHTMLInResponses && /<[^>]+>/.test(out)) {
              addMessage("bot", { html: out });
            } else {
              addMessage("bot", { text: out });
            }
          } else if (out && typeof out === "object") {
            const { text, html } = out;
            if (options.allowHTMLInResponses && html) {
              addMessage("bot", { html });
            } else {
              addMessage("bot", { text: text ?? "" });
            }
          } else {
            addMessage("bot", { text: "Received empty response." });
          }
        } catch (err) {
          setTyping(false);
          addMessage("bot", { text: "Sorry, I couldn’t reach the server. Please try again." });
          if (typeof options.onEvent === "function") options.onEvent("error", { error: err });
        }
      }

      // Events
      ui.launcher.addEventListener("click", () => {
        ui.panel.classList.toggle("hidden");
        if (typeof options.onEvent === "function") options.onEvent("toggle", { open: !ui.panel.classList.contains("hidden") });
      });
      ui.header.querySelector(".bc-close").addEventListener("click", () => {
        ui.panel.classList.add("hidden");
        if (typeof options.onEvent === "function") options.onEvent("toggle", { open: false });
      });

      ui.inputBar.addEventListener("submit", (e) => {
        e.preventDefault();
        const input = ui.inputBar.querySelector('input[type="text"]');
        const value = (input.value || "").trim();
        if (!value) return;
        addMessage("user", { text: value });
        input.value = "";
        sendToWebhook(value);
      });

      // Close on click outside
      let lastOpenedAt = 0;
      document.addEventListener("click", (e) => {
        // If panel is hidden, nothing to do
        if (ui.panel.classList.contains("hidden")) return;
        
        // Debounce: Don't close if panel was just opened (prevents CTA button race condition)
        if (Date.now() - lastOpenedAt < 100) return;
        
        // Check if the click path includes the shadow host (click is inside or on the chatbox)
        const path = e.composedPath();
        if (path.includes(shadowRoot.host)) return;

        // Otherwise, close it
        ui.panel.classList.add("hidden");
        if (typeof options.onEvent === "function") options.onEvent("toggle", { open: false });
      });

      // Close on Escape key
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !ui.panel.classList.contains("hidden")) {
          ui.panel.classList.add("hidden");
          if (typeof options.onEvent === "function") options.onEvent("toggle", { open: false });
        }
      });

      // Inactivity/session TTL: when exceeded while panel is open, reset and inform user
      function expireSessionDueToInactivity() {
        setTyping(false);
        sessionId = generateSessionId();
        history = [];
        ui.messages.innerHTML = "";
        persist();
        if (!ui.panel.classList.contains("hidden")) {
          addMessage("bot", { text: "Session expired due to inactivity. Starting a new session." });
        }
        if (typeof options.onEvent === "function") options.onEvent("sessionExpired", { sessionId });
      }

      if (options.sessionTtlMinutes && options.sessionTtlMinutes > 0) {
        const ttlMs = options.sessionTtlMinutes * 60 * 1000;
        const intervalMs = Math.min(Math.max(15000, Math.floor(ttlMs / 3)), 60000);
        setInterval(() => {
          const { lastBotAt, lastUserAt } = computeLastTimestampsFromHistory(history);
          const baseTime = Math.max(lastUserAt || 0, lastBotAt || 0);
          if (baseTime && Date.now() - baseTime > ttlMs) {
            expireSessionDueToInactivity();
          }
        }, intervalMs);
      }

      reopenFromOption();

      const api = {
        open: () => {
          lastOpenedAt = Date.now();
          ui.panel.classList.remove("hidden");
        },
        close: () => ui.panel.classList.add("hidden"),
        toggle: () => ui.panel.classList.toggle("hidden"),
        send: (text) => {
          addMessage("user", { text });
          sendToWebhook(text);
        },
        clear: () => {
          history.splice(0, history.length);
          ui.messages.innerHTML = "";
          persist();
        },
        getSessionId: () => sessionId
      };

      if (typeof options.onEvent === "function") options.onEvent("ready", { sessionId });

      try { if (window && window.N8NbrandableChatbox) { window.N8NbrandableChatbox.api = api; } } catch (e) {}

      return api;
    }

    return { init };
  })();

  window.N8NbrandableChatbox = N8NbrandableChatbox;
})();