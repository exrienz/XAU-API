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
EXPOSE 8000
CMD ["/app/start.sh"]
