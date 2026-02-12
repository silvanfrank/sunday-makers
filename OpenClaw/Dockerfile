# OpenClaw Gateway - Simplified Dockerfile
# Based on official: https://github.com/openclaw/openclaw/blob/main/Dockerfile
# Only differences: git clone instead of COPY, CMD starts gateway, entrypoint for trustedProxies

FROM node:22-bookworm

# Install Bun (required for build scripts)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN corepack enable

WORKDIR /app

# Clone OpenClaw source (since we're not in the openclaw repo)
RUN git clone --depth 1 https://github.com/openclaw/openclaw.git .

# Install dependencies (mirrors official Dockerfile)
RUN pnpm install --frozen-lockfile

# Build the application (mirrors official Dockerfile)
RUN OPENCLAW_A2UI_SKIP_MISSING=1 pnpm build
# Force pnpm for UI build (Bun may fail on ARM/Synology architectures)
ENV OPENCLAW_PREFER_PNPM=1
RUN pnpm ui:build

ENV NODE_ENV=production

# Expose Gateway port
EXPOSE 18789

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
  CMD curl -f http://localhost:18789/health || exit 1

# Copy and set up the entrypoint script (only sets trustedProxies)
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Start the Gateway via entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["node", "dist/index.js", "gateway", "--bind", "lan", "--allow-unconfigured"]
