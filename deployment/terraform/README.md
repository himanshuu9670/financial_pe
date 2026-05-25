# Terraform (Phase 10 placeholder)

Modules to add per cloud:

| Module | AWS | DigitalOcean | Railway/Render |
|--------|-----|--------------|----------------|
| Database | RDS Postgres | Managed DB | Plugin |
| Cache | ElastiCache Redis | Managed Redis | Upstash |
| Object storage | S3 + IAM | Spaces | Bucket |
| Compute | ECS/EKS | Droplets/K8s | Service |
| CDN | CloudFront | CDN | Built-in |

Keep secrets in Terraform Cloud / AWS Secrets Manager — never commit `.tfvars` with credentials.
