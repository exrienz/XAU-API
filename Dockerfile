FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    tzdata \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
ENV TZ=Asia/Kuala_Lumpur
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

# Install Playwright browsers and dependencies
RUN playwright install --with-deps chromium

COPY . .
RUN chmod +x /app/start.sh

ENV PYTHONUNBUFFERED=1

# K8s compatibility: Chromium shared memory settings
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV NODE_OPTIONS="--max-old-space-size=2048"

# Chromium flags for containerized environments
ENV PLAYWRIGHT_CHROMIUM_ARGS="--disable-dev-shm-usage --no-sandbox --disable-setuid-sandbox --disable-gpu"

EXPOSE 8000

# Health check for K8s liveness/readiness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["/app/start.sh"]
