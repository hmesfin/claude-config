---
name: deploy-production
description: Generate production deployment configs (docker-compose.production.yml, .env.production.example, .github/workflows/deploy.yml) for the current project. Auto-detects Django/FastAPI stack, frontend, and Celery services. For Hetzner dedicated server with Traefik.
---

# /deploy-production

Generate or update production deployment configuration files for the current project. Targets the Hetzner dedicated server (5.9.150.47, user `deploy`) running Traefik on the `proxy-net` network.

## What This Command Does

1. Auto-detects the project stack, frontend, and background services
2. Generates or updates deployment config files + CI/CD workflow
3. Prints setup instructions (GitHub secrets, SSL, DNS, verification)

## Step 1: Auto-Detect Project

Inspect the current project directory and determine:

**Stack:**
- If `manage.py` exists AND (`config/settings/` dir OR a `settings.py` file exists) → Django
- If `pyproject.toml` exists and contains `fastapi` in `[project.dependencies]` or `[tool.poetry.dependencies]` → FastAPI
- If neither signal is clear → ask the user

**Frontend:**
- If `frontend/` directory exists containing a `package.json` → frontend present
- If `package.json` exists at project root with a `"build"` script → frontend present (monorepo)
- Otherwise → API-only (no frontend)

**Services:**
- Check `requirements.txt`, `requirements/*.txt`, or `pyproject.toml` for:
  - `celery` or `celery[redis]` → include celeryworker, celerybeat, flower services
  - `redis` → include redis service (also included automatically if celery is detected)
  - `channels` or `daphne` → print a note about websocket support (not auto-configured)

**Project name** (in priority order):
1. Parse existing `docker-compose.production.yml` for `container_name` pattern like `<name>-django` → extract `<name>`
2. Parse git remote: `git remote get-url origin` → extract repo name
3. Fall back to current directory name

**GHCR owner:**
- Parse git remote: `git remote get-url origin` → extract owner/org (e.g., `ghcr.io/<owner>/<appname>-django`)

**Domain:**
- Check existing compose file for `Host(...)` rules → extract domain
- If not found → ask the user

Report what you detected to the user before generating files.

## Step 2: Generate Files

### File: `docker-compose.production.yml` (create or update)

If this file already exists, read it first. Preserve any custom services, volumes, or environment variables not part of the canonical template. Update Traefik labels, networks, and service structure to match the patterns below. Print a summary of what changed.

**Django + Frontend + Celery pattern (full stack):**

```yaml
volumes:
  <appname>_postgres_data: {}
  <appname>_postgres_backups: {}
  <appname>_redis_data: {}

networks:
  proxy-net:
    external: true
  <appname>-net:

services:
  django: &django
    image: ghcr.io/<owner>/<appname>-django:latest
    container_name: <appname>-django
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    env_file:
      - .env
    command: /start
    networks:
      - <appname>-net
      - proxy-net
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=proxy-net"
      - "traefik.http.routers.<appname>-django.rule=Host(`api.<domain>`)"
      - "traefik.http.routers.<appname>-django.entrypoints=websecure"
      - "traefik.http.routers.<appname>-django.tls=true"
      - "traefik.http.services.<appname>-django.loadbalancer.server.port=5000"
      - "traefik.http.routers.<appname>-django.middlewares=<appname>-csrf-headers"
      # CSRF + CORS
      - "traefik.http.middlewares.<appname>-csrf-headers.headers.hostsProxyHeaders=X-CSRFToken"
      - "traefik.http.middlewares.<appname>-csrf-headers.headers.accessControlAllowOriginList=https://<domain>,https://www.<domain>"
      - "traefik.http.middlewares.<appname>-csrf-headers.headers.accessControlAllowMethods=GET,POST,PUT,PATCH,DELETE,OPTIONS"
      - "traefik.http.middlewares.<appname>-csrf-headers.headers.accessControlAllowHeaders=Content-Type,Authorization,X-CSRFToken"
      - "traefik.http.middlewares.<appname>-csrf-headers.headers.accessControlAllowCredentials=true"
      - "traefik.http.middlewares.<appname>-csrf-headers.headers.accessControlMaxAge=86400"
      - "traefik.http.middlewares.<appname>-csrf-headers.headers.addVaryHeader=true"

  postgres:
    image: postgres:16
    container_name: <appname>-postgres
    restart: unless-stopped
    volumes:
      - <appname>_postgres_data:/var/lib/postgresql/data
      - <appname>_postgres_backups:/backups
    env_file:
      - .env
    networks:
      - <appname>-net

  redis:
    image: redis:7.2
    container_name: <appname>-redis
    restart: unless-stopped
    volumes:
      - <appname>_redis_data:/data
    networks:
      - <appname>-net

  celeryworker:
    <<: *django
    container_name: <appname>-celeryworker
    command: /start-celeryworker
    networks:
      - <appname>-net
    labels: []

  celerybeat:
    <<: *django
    container_name: <appname>-celerybeat
    command: /start-celerybeat
    networks:
      - <appname>-net
    labels: []

  flower:
    <<: *django
    container_name: <appname>-flower
    command: /start-flower
    ports:
      - "127.0.0.1:<next-available-port>:5555"
    networks:
      - <appname>-net
    labels: []

  frontend:
    image: ghcr.io/<owner>/<appname>-frontend:latest
    container_name: <appname>-frontend
    restart: unless-stopped
    networks:
      - proxy-net
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=proxy-net"
      - "traefik.http.routers.<appname>-frontend.rule=Host(`<domain>`) || Host(`www.<domain>`)"
      - "traefik.http.routers.<appname>-frontend.entrypoints=websecure"
      - "traefik.http.routers.<appname>-frontend.tls=true"
      - "traefik.http.services.<appname>-frontend.loadbalancer.server.port=80"
```

**Conditional adjustments:**

- **If FastAPI instead of Django:** Replace `django` service name with `fastapi`. Change image to `ghcr.io/<owner>/<appname>-fastapi:latest`. Adjust command to FastAPI entrypoint. Change `loadbalancer.server.port` to match (typically 8000). Adjust CSRF/CORS middleware labels if the project handles CORS in-app instead of at the proxy level.
- **If no Celery detected:** Remove `celeryworker`, `celerybeat`, and `flower` services. Remove the `&django` YAML anchor (no longer needed). Remove `<appname>_redis_data` volume if Redis is also not detected.
- **If no Redis detected (and no Celery):** Remove `redis` service and `<appname>_redis_data` volume. Remove `redis` from `depends_on`.
- **If no frontend detected:** Remove the `frontend` service entirely.
- **Flower port allocation:** Known ports — RentKee=5555, FamApp=5556, Traice=5557. Allocate the next available (5558+). Tell the user which port was assigned.

**Key conventions:**
- `tls=true` only — NO `certresolver` (Cloudflare origin certs handle SSL)
- `labels: []` on celery/flower to clear inherited Traefik labels from YAML anchor
- Django management commands: use `docker compose run --rm`, never `exec`
- All Flower ports bound to `127.0.0.1` (localhost only)

### File: `.env.production.example` (create only — never overwrite)

If this file already exists, skip it and tell the user it was preserved.

```env
# Django
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<generate-unique-key>
DJANGO_ADMIN_URL=<random-admin-path>/
DJANGO_ALLOWED_HOSTS=.<domain>
DJANGO_SECURE_SSL_REDIRECT=False

# Email (SendGrid)
DJANGO_SERVER_EMAIL=noreply@<domain>
SENDGRID_API_KEY=<key>
SENDGRID_GENERATE_MESSAGE_ID=True
SENDGRID_MERGE_FIELD_FORMAT=None

# Storage (Cloudflare R2)
DJANGO_CLOUDFLARE_R2_ACCESS_KEY_ID=<key>
DJANGO_CLOUDFLARE_R2_SECRET_ACCESS_KEY=<secret>
DJANGO_CLOUDFLARE_R2_BUCKET_NAME=<bucket>
DJANGO_CLOUDFLARE_R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
DJANGO_CLOUDFLARE_R2_CUSTOM_DOMAIN=<optional-cdn-domain>

# Gunicorn
WEB_CONCURRENCY=4

# Sentry
SENTRY_DSN=<dsn>

# Redis
REDIS_URL=redis://redis:6379/0

# Celery / Flower
CELERY_FLOWER_USER=admin
CELERY_FLOWER_PASSWORD=<strong-password>

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=<dbname>
POSTGRES_USER=<dbuser>
POSTGRES_PASSWORD=<strong-password>
```

**Conditional adjustments:**
- If FastAPI: replace Django-specific vars (`DJANGO_SETTINGS_MODULE`, `DJANGO_ADMIN_URL`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SECURE_SSL_REDIRECT`) with FastAPI equivalents.
- If no Celery: remove `CELERY_FLOWER_USER` and `CELERY_FLOWER_PASSWORD`.
- If no Redis: remove `REDIS_URL`.
- If no SendGrid detected in project: comment out email section with a note.
- If no Sentry detected: comment out `SENTRY_DSN` with a note.
- If no R2/S3 storage detected: comment out storage section with a note.

### File: `.github/workflows/deploy.yml` (create or update)

If this file exists, read it first and preserve custom steps or environment variables. Update the build/deploy pattern to match below.

**IMPORTANT:** Use raw CLI commands only. Do NOT use `docker/login-action`, `docker/build-push-action`, or `appleboy/ssh-action` — they have known issues with snap Docker and ED25519 keys.

```yaml
name: Deploy

on:
  push:
    branches: ['main']
    paths-ignore:
      - 'docs/**'
      - '**.md'

env:
  DJANGO_IMAGE: ghcr.io/${{ github.repository_owner }}/<appname>-django
  # FRONTEND_IMAGE: ghcr.io/${{ github.repository_owner }}/<appname>-frontend

jobs:
  build-and-deploy:
    runs-on: self-hosted

    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Login to GHCR
        run: echo "$GHCR_PAT" | tr -d '[:space:]' | docker login ghcr.io -u "$GHCR_USER" --password-stdin
        env:
          GHCR_PAT: ${{ secrets.GHCR_PAT }}
          GHCR_USER: ${{ github.repository_owner }}

      - name: Build and push Django image
        run: |
          docker build -f ./compose/production/django/Dockerfile \
            -t "$DJANGO_IMAGE:latest" \
            -t "$DJANGO_IMAGE:$GITHUB_SHA" \
            .
          docker push "$DJANGO_IMAGE:latest"
          docker push "$DJANGO_IMAGE:$GITHUB_SHA"

      # Uncomment if frontend detected:
      # - name: Build and push Frontend image
      #   run: |
      #     docker build -f ./compose/production/frontend/Dockerfile \
      #       -t "$FRONTEND_IMAGE:latest" \
      #       -t "$FRONTEND_IMAGE:$GITHUB_SHA" \
      #       ./frontend
      #     docker push "$FRONTEND_IMAGE:latest"
      #     docker push "$FRONTEND_IMAGE:$GITHUB_SHA"

      - name: Setup SSH key
        run: |
          mkdir -p ~/.ssh
          printf '%s\n' "$SSH_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H "$PRODUCTION_HOST" >> ~/.ssh/known_hosts
        env:
          SSH_KEY: ${{ secrets.PRODUCTION_SSH_KEY }}
          PRODUCTION_HOST: ${{ secrets.PRODUCTION_HOST }}

      - name: Deploy to production via SSH
        run: |
          ssh -i ~/.ssh/deploy_key "$PRODUCTION_USER@$PRODUCTION_HOST" bash -s -- "$GHCR_TOKEN" "$GHCR_USER" << 'DEPLOY'
            set -euo pipefail
            GHCR_TOKEN="$1"
            GHCR_USER="$2"

            cd /data/apps/<appname>

            echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

            docker compose pull
            docker compose up -d
            docker compose run --rm django python manage.py migrate --noinput
            docker compose run --rm django python manage.py collectstatic --noinput
            docker image prune -f
            docker compose ps
          DEPLOY
        env:
          PRODUCTION_HOST: ${{ secrets.PRODUCTION_HOST }}
          PRODUCTION_USER: ${{ secrets.PRODUCTION_USER }}
          GHCR_TOKEN: ${{ secrets.GHCR_PAT }}
          GHCR_USER: ${{ github.repository_owner }}
```

**Conditional adjustments:**
- If frontend detected: uncomment the `FRONTEND_IMAGE` env var and the frontend build step.
- If FastAPI: change `django` references to `fastapi` in image names and deploy commands. Adjust Dockerfile path. Replace `manage.py migrate` and `collectstatic` with FastAPI equivalents (e.g., `alembic upgrade head`).
- Check if Dockerfile path matches project structure. Common patterns:
  - Cookiecutter Django: `./compose/production/django/Dockerfile`
  - Simple projects: `./backend/Dockerfile` or `./Dockerfile`
  Adjust the `-f` flag accordingly.

## Step 3: Post-Generation Output

After generating all files, print the following to the terminal (do not write to a file):

```
## Production Deployment Setup

### 1. GitHub Secrets to Configure

Go to repo Settings → Secrets and variables → Actions, and add:

| Secret | Value | Description |
|---|---|---|
| `PRODUCTION_HOST` | `5.9.150.47` | Hetzner server IP |
| `PRODUCTION_USER` | `deploy` | SSH user on production server |
| `PRODUCTION_SSH_KEY` | (ED25519 private key) | SSH key for deploy user |
| `GHCR_PAT` | (GitHub Classic PAT) | Needs `write:packages` + `read:packages` + `delete:packages` |

### 2. Server Setup

ssh deploy@5.9.150.47
sudo mkdir -p /data/apps/<appname>
sudo chown deploy:deploy /data/apps/<appname>

# Copy docker-compose.production.yml → /data/apps/<appname>/docker-compose.yml
# Create .env from .env.production.example with real values

### 3. GHCR Login on Server (one-time)

echo "<GHCR_PAT>" | docker login ghcr.io -u <owner> --password-stdin

### 4. Cloudflare Origin Certificate

1. Cloudflare → SSL/TLS → Origin Server → Create Certificate
2. Key type: RSA (2048), Hostnames: <domain>, *.<domain>, Validity: 15 years
3. Save to server:
   sudo nano /data/proxy/certs/<domain>.pem          # paste certificate
   sudo nano /data/proxy/certs/<domain>-key.pem       # paste private key
   sudo chmod 600 /data/proxy/certs/<domain>-key.pem
4. Add to /data/proxy/dynamic.yml:
   tls:
     certificates:
       - certFile: /certs/<domain>.pem
         keyFile: /certs/<domain>-key.pem

### 5. DNS Setup (Cloudflare)

Create A records pointing to 5.9.150.47:
  - <domain>
  - www.<domain>
  - api.<domain>

Enable orange cloud proxy on all records.
Set SSL mode to Full (strict).

### 6. Flower Port

Assigned port: <next-available> (bound to 127.0.0.1 only)
Access via SSH tunnel: ssh -L <port>:127.0.0.1:<port> deploy@5.9.150.47

### 7. First Deploy

cd /data/apps/<appname>
docker compose pull
docker compose up -d
docker compose run --rm django python manage.py migrate --noinput
docker compose run --rm django python manage.py collectstatic --noinput
docker compose ps

### 8. Verify

curl -I https://api.<domain>/api/docs/
curl -I https://<domain>

### 9. Monitor

docker compose logs -f --tail=100
# Watch for 24-48 hours, then restore DNS TTL to Auto in Cloudflare
```

## Important Rules

- NEVER include real secrets in generated files — use placeholders only
- NEVER expose ports directly (except Flower on localhost) — Traefik handles routing
- NEVER use `certresolver` in labels — Cloudflare origin certs handle SSL
- NEVER use third-party GitHub Actions for Docker or SSH — use raw CLI commands
- ALWAYS use `docker compose run --rm` for management commands, never `exec`
- ALWAYS use `tls=true` only on Traefik router labels
- ALWAYS use `labels: []` on celery/flower to clear YAML anchor labels
- ALWAYS use `printf '%s\n'` for SSH keys and `tr -d '[:space:]'` for tokens in CI/CD
- ALWAYS read existing files before updating — preserve custom additions
- ALWAYS report what was detected and what was generated
