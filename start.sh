#!/bin/bash
# Production startup script for shot-diff server

cd "$(dirname "$0")"
source venv/bin/activate
exec gunicorn -w 2 -b 127.0.0.1:8000 server:app