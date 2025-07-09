FROM python:3.9.23-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    unzip \
    supervisor \
    redis-server \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    libgbm1 \
    libgl1-mesa-glx \
    libx11-6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Opera
RUN curl https://deb.opera.com/archive.key | apt-key add -
RUN echo deb https://deb.opera.com/opera-stable/ stable non-free | tee /etc/apt/sources.list.d/opera.list
RUN apt update && apt install -y opera-stable

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright and camoufox
RUN playwright install chromium
# RUN playwright install chromium firefox
# RUN python -m camoufox fetch

# Copy your project files
COPY . .

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV DISPLAY=:0
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV CELERY_BROKER_URL=redis://localhost:6379/0

EXPOSE 8000

# Start all processes via Supervisor
CMD ["supervisord", "-n"]
