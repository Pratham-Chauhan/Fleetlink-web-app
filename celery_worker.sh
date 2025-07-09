#!/bin/bash
# celery_worker.sh

echo "Starting Celery worker..."
celery -A tasks worker --loglevel=info
