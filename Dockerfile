FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Playwright and Chromium
# This includes all necessary libraries for running headless Chromium in containers
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Basic utilities
    curl \
    wget \
    gnupg \
    ca-certificates \
    # Timezone data
    tzdata \
    # Required libraries for Chromium
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    # Fonts
    fonts-liberation \
    fonts-noto-color-emoji \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set timezone
ENV TZ=Asia/Kuala_Lumpur
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel \
    && pip3 install --no-cache-dir -r requirements.txt

# Set Playwright environment variables BEFORE installing browsers
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0
ENV NODE_OPTIONS="--max-old-space-size=2048"
ENV PYTHONUNBUFFERED=1

# Install Playwright browsers with all system dependencies
# Using --with-deps ensures all necessary system libraries are installed
RUN playwright install --with-deps chromium

# Verify browser installation
RUN playwright install --help && \
    ls -la /ms-playwright/ || echo "Browser path not found" && \
    find /ms-playwright -name "chrome*" -o -name "chromium*" || echo "No browser executable found"

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x /app/start.sh

# Create non-root user for security (optional, but recommended)
# Comment out if you need to run as root in your environment
# RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /ms-playwright
# USER appuser

# Environment variables for Chromium in containerized environments
ENV PLAYWRIGHT_CHROMIUM_ARGS="--disable-dev-shm-usage --no-sandbox --disable-setuid-sandbox --disable-gpu"

# Expose API port
EXPOSE 8000

# Health check for container orchestration (K8s/Docker)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start both scraper and API server
CMD ["/app/start.sh"]
