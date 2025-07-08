FROM python:3.9.23-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    unzip \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    libgbm1 \
    libgtk-3-0 \
    libx11-xcb1 \
    libasound2 curl \
    libgl1-mesa-glx \
    libx11-6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Opera Browser
RUN curl https://deb.opera.com/archive.key | apt-key add -
RUN echo deb https://deb.opera.com/opera-stable/ stable non-free | tee /etc/apt/sources.list.d/opera.list
RUN apt update
RUN apt install -y opera-stable


# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium firefox
RUN python -m camoufox fetch

# Copy your project files
COPY atu_scraper.py .
COPY fleetlink_id_mapping.xlsx .

# Command to run your script 
# CMD ["python", "atu_scraper.py"]

# Copy your Flask app and other project files
COPY app.py .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV DISPLAY=:0
ENV LIBGL_ALWAYS_SOFTWARE=1

# Expose port 5000 (Flask default)
# EXPOSE 5000

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Command to run your Flask app
# CMD ["flask", "run"]

# Command to run Gunicorn (with 2 workers, adjustable)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "2"]