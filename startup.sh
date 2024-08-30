#!/bin/bash
cd /home/site/wwwroot
gunicorn --bind=0.0.0.0 -w 4 -k uvicorn.workers.UvicornWorker server:app