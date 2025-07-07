#!/bin/bash
source .venv/bin/activate
celery -A etl.tasks.app worker --loglevel=info 