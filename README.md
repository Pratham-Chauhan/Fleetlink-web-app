
# 🕸️  ATU Booking System Scraper (Playwright) 

This project is a robust scraper system built with:

- 🧠 **Flask** for handling HTTP API requests  
- 🧵 **Celery** for background job processing  
- 📬 **Redis** as the Celery message broker  
- 🧭 **Playwright** for browser automation  
- 📦 **Supervisor** to run everything in a single container  

It is designed to be deployed easily on platforms like **Railway**, using a single `Dockerfile` and `supervisord`.



## 🚀 Features

- Accepts `POST` requests via Flask  
- Dispatches scraping jobs to Celery workers  
- Uses Redis as internal queue  
- All three services run inside **one Docker container**



## 🧪 Local Development (Without Docker)

You can run all services manually on your system for development.

### 🔧 Prerequisites
Before proceeding, make sure you have the following installed on your system:

 - Python 3.9+
 - Redis server
 - Opera browser
 - Playwright and Chromium driver (playwright install chromium)
 - [Optional] Camuofox (https://github.com/daijro/camoufox)


**Create and activate virtual environment**

Install Python dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
### 1. Start Redis server

Make sure Redis is installed and run:

```bash
redis-server
```

### 2. Start Flask app (via Gunicorn)
```bash
gunicorn app:app --bind 0.0.0.0:8000 --workers=4
```
### 3. Start Celery worker

```bash
celery -A tasks worker --loglevel=info --concurrency=2 --pool=prefork
```

### 🐳 Run with Docker (All-in-One Container)
---
Everything — Flask + Celery + Redis — runs in one container using Supervisor.

1. Build Docker image


```bash
docker build -t scraper-app .
```
2. Run the container

```bash
docker run -p 8000:8000 scraper-app
```


## 🌐 API Usage


Send a POST request to the API:

```bash
curl -X POST http://localhost:8000/run-scraper \
  -H "Content-Type: application/json" \
  -d '{
        "pin_code": "64347",
        "id_target": [26],
        "target_service_group": [],
        "service_name": [],
        "target_manufacturer": "FORD",
        "target_model": "KA",
        "target_year": "2011",
        "quantity_amount": "1",
        "target_date": "12.06.2025",
        "engine": "electric",
        "your_data": {
            "firstName": "",
            "lastName": "",
            "email": "",
            "mobile": "",
            "Erreichbarkeit": "",
            "licensePlate": "",
            "HSN": "",
            "TSN": "",
            "mileage": "",
            "Radeinlagerungsnummer": "",
            "Firmenname": "",
            "Kundennummer": "",
            "Anmerkung": ""
        }
      }'

```

### 🚀 Deploying on Railway
-  Push your project to GitHub
- Create a new service on Railway
- Choose "Deploy from GitHub" and select your repo
- Railway will detect the Dockerfile and run everything
- You do NOT need to provision Redis separately — it's included in the container.

