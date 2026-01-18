# Workers

This directory contains **background worker jobs** that run outside the
FastAPI request–response cycle.

Purpose of workers:
- Execute long-running or non-critical tasks
- Prevent blocking API requests
- Enable scalability and async processing

These workers are NOT invoked directly by HTTP requests.
They are intended to be triggered by:
- Schedulers (cron)
- Task queues (Celery / RQ)
- Periodic background jobs

Ownership is defined per worker file to allow
parallel backend and AI development.
