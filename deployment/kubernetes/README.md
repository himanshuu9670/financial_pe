# Kubernetes (Phase 10 skeleton)

Deploy using the production images from `deployment/docker/`.

Suggested manifests (create per environment):

- `Deployment` — backend (2+ replicas), frontend, celery worker
- `StatefulSet` or managed RDS — PostgreSQL
- `Deployment` — Redis
- `Ingress` — TLS + `/api` → backend, `/` → frontend
- `PersistentVolumeClaim` — `pdf_storage` or use S3 (`STORAGE_BACKEND=s3`)
- `ServiceMonitor` — scrape `/api/v1/metrics` for Prometheus Operator

Helm chart can wrap `deployment/docker/docker-compose.prod.yml` services as a starting point.
