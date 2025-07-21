FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Kuala_Lumpur
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/start.sh
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["/app/start.sh"]
