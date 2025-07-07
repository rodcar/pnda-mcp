from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

app = Celery(
    'pnda-mcp-worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

app.conf.update(
    worker_concurrency=os.getenv('WORKER_CONCURRENCY', 4),
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_hostname='worker@%h',
)