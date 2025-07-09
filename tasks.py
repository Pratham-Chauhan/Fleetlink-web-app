# tasks.py
from celery import Celery
from atu_scraper import ATUScraper

celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # Update this in production
    backend='redis://localhost:6379/0'
)

@celery.task(bind=True)
def run_scraper(self, data, timestamp, browser_type):
    try:
        scraper = ATUScraper(data, timestamp, browser_type)
        scraper.run()
    except Exception as e:
        raise self.retry(exc=e, countdown=10, max_retries=3)
