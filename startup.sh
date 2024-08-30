#!/bin/bash
set -e
pwd

export PORT=${PORT:-8000}
gunicorn --bind=0.0.0.0:$PORT --timeout 600 -w 4 -k uvicorn.workers.UvicornWorker server:app --error-logfile /home/LogFiles/gunicorn_error.log --access-logfile /home/LogFiles/gunicorn_access.log
