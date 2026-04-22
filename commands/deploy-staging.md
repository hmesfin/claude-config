---
name: deploy-staging
description: Generate staging deployment configs (docker-compose.staging.yml, nginx.conf, .env.staging.example) for the current project. Auto-detects Django/FastAPI stack and frontend presence. For self-hosted staging server with Traefik.
---

# /deploy-staging

Generate or update staging deployment configuration files for the current project. Targets the self-hosted staging server (192.168.1.240, user `hmesfin`) running Traefik on the `proxy` network.

## What This Command Does

1. Auto-detects the project stack and structure
2. Generates or updates deployment config files
3. Prints deployment instructions and verification commands

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
- Check `requirements.txt`, `requirements/*.txt`, or `pyproject.toml` for `redis` → include redis
- Check same files for `celery` or `celery[redis]` → include redis (celery needs it)

**Project name** (in priority order):
1. Parse existing `docker-compose.staging.yml` for `container_name` pattern like `<name>-backend` → extract `<name>`
2. Parse git remote: `git remote get-url origin` → extract repo name
3. Fall back to current directory name

Report what you detected to the user before generating files.

## Step 2: Generate Files

### File: `docker-compose.staging.yml` (create or update)

If this file already exists, read it first. Preserve any custom services, volumes, or environment variables not part of the canonical template. Update Traefik labels, networks, and service structure to match the patterns below. Print a summary of what changed.

If creating fresh, use the patterns below.

**Django + Frontend pattern:**

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: ${PROJECT_NAME}-nginx
    restart: unless-stopped
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./media:/media:ro
      - ./static:/static:ro
    networks:
      - proxy
      - internal
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=proxy"
      - "traefik.http.routers.${PROJECT_NAME}.rule=Host(`${PROJECT_DOMAIN}`)"
      - "traefik.http.routers.${PROJECT_NAME}.entrypoints=websecure"
      - "traefik.http.routers.${PROJECT_NAME}.tls=true"
      - "traefik.http.routers.${PROJECT_NAME}.tls.certresolver=cloudflare"
      - "traefik.http.services.${PROJECT_NAME}.loadbalancer.server.port=80"

  backend:
    build: ./backend
    container_name: ${PROJECT_NAME}-backend
    restart: unless-stopped
    environment:
      - SECRET_KEY=${DJANGO_SECRET_KEY}
      - DEBUG=${DEBUG}
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/${PROJECT_NAME}_db
    volumes:
      - ./backend:/app
      - ./media:/app/media
      - ./static:/app/static
    networks:
      - internal
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    container_name: ${PROJECT_NAME}-postgres
    environment:
      - POSTGRES_DB=${PROJECT_NAME}_db
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal

volumes:
  postgres_data:

networks:
  proxy:
    external: true
  internal:
    driver: bridge
```

**Conditional adjustments:**

- **If FastAPI instead of Django:** Replace the `backend` service's build context and environment. Use `uvicorn` as the command. Replace `DJANGO_SECRET_KEY` with `SECRET_KEY`. Replace `DATABASE_URL` format if the project uses a different pattern (check existing settings/config).
- **If API-only (no frontend):** Remove the `nginx` service entirely. Move the Traefik labels onto the `backend` service directly. Change `loadbalancer.server.port` to match the backend's port (8000 for Django/gunicorn, 8000 for FastAPI/uvicorn). Add `proxy` to the backend's networks list. Remove frontend-related volumes.
- **If Redis detected:** Add a redis service:
  ```yaml
  redis:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME}-redis
    restart: unless-stopped
    networks:
      - internal
  ```
  Add `redis` to backend's `depends_on`.

**Rules:**
- No direct port exposure — Traefik handles all routing
- Container names use `${PROJECT_NAME}-<service>` pattern
- Only nginx (or backend if API-only) connects to `proxy` network
- All other services on `internal` network only
- Named volumes for persistent data

### File: `nginx.conf` (create or update, skip if API-only)

Only generate if frontend was detected. If the file exists, read it first and preserve custom location blocks.

```nginx
worker_processes auto;

events {
  worker_connections 1024;
}

http {
  include       /etc/nginx/mime.types;
  default_type  application/octet-stream;
  sendfile      on;
  keepalive_timeout 65;
  client_max_body_size 10M;

  upstream backend {
    server backend:8000;
  }

  server {
    listen 80;
    server_name _;

    # Frontend static files
    location / {
      root /usr/share/nginx/html;
      try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
      proxy_pass http://backend;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django admin proxy
    location /admin/ {
      proxy_pass http://backend;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
      alias /static/;
    }

    # Media files
    location /media/ {
      alias /media/;
    }
  }
}
```

**Conditional adjustments:**
- If FastAPI: remove the `/admin/` location block. Add `/docs` and `/redoc` proxy locations if the project uses FastAPI's built-in docs.

### File: `.env.staging.example` (create only — never overwrite)

If this file already exists, skip it and tell the user it was preserved.

Generate with detected values filled in:

```env
# Project identification
PROJECT_NAME=<detected-project-name>
PROJECT_DOMAIN=<detected-project-name>.staging.gojjoapps.com

# Django settings
DJANGO_SECRET_KEY=<generate-a-secret-key>
DEBUG=False

# Database
POSTGRES_PASSWORD=<set-a-secure-password>

# Redis (if using)
# REDIS_URL=redis://redis:6379/0
```

**Conditional adjustments:**
- If FastAPI: replace Django-specific vars with FastAPI equivalents (`SECRET_KEY` instead of `DJANGO_SECRET_KEY`, remove `DEBUG`).
- If Redis detected: uncomment the `REDIS_URL` line.

## Step 3: Post-Generation Output

After generating all files, print the following to the terminal (do not write to a file):

```
## Deployment Instructions

### 1. Copy project to staging server
ssh hmesfin@192.168.1.240
cd ~/projects
mkdir <project-name>
# Copy your project files to ~/projects/<project-name>/

### 2. Create .env from template
cp .env.staging.example .env
# Edit .env with real values

### 3. DNS Setup
Create an A record in Cloudflare:
  <project-name>.staging.gojjoapps.com → 192.168.1.240

### 4. Deploy
docker-compose -f docker-compose.staging.yml up -d --build

### 5. Verify
docker-compose -f docker-compose.staging.yml logs -f
docker logs traefik | grep <project-name>
curl -I https://<project-name>.staging.gojjoapps.com

### Troubleshooting
- 502 Bad Gateway: check `docker ps`, verify service is on proxy network
- SSL issues: check Cloudflare DNS points to server, check `docker logs traefik`
- DB connection: use container names as hostnames (e.g., `postgres` not `localhost`)
```

## Important Rules

- NEVER include real secrets in generated files — use placeholders only
- NEVER expose ports directly in docker-compose — Traefik handles routing
- ALWAYS use `${PROJECT_NAME}-<service>` for container names
- ALWAYS read existing files before updating — preserve custom additions
- ALWAYS report what was detected and what was generated
