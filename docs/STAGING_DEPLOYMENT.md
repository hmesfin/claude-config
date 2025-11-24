# Project Deployment Guide for Staging Server

This guide explains how to deploy Django/Vue.js projects on the staging server with Traefik routing.

## Server Directory Layout

```markdown
/home/hmesfin/
├── traefik/ # Traefik reverse proxy (already running)
│ ├── docker-compose.yml # Main Traefik config
│ ├── traefik.yml # Traefik settings
│ └── acme.json # SSL certificates
├── projects/ # YOUR PROJECTS GO HERE
│ ├── project1/ # Example: Django/Vue.js app
│ │ ├── docker-compose.staging.yml
│ │ ├── nginx.conf
│ │ ├── backend/ # Django code
│ │ ├── frontend/ # Vue.js code
│ │ └── .env
│ └── project2/ # Another project
└── gojjoapps-landing/ # Landing page at gojjoapps.com
```

## Key Requirements for Project Docker Compose Files

Your `docker-compose.staging.yml` MUST include:

### 1. Connect to the Proxy Network

```yaml
networks:
  proxy:
    external: true
  internal: # Optional: for internal services like DB
    driver: bridge
```

### 2. Traefik Labels on Your Web Service

For a project at `myapp-staging.example.com`, your nginx/web service needs:

```yaml
services:
  nginx: # or whatever serves your web content
    networks:
      - proxy
      - internal
    labels:
      # Required: Enable Traefik
      - "traefik.enable=true"
      - "traefik.docker.network=proxy"

      # Required: Domain routing
      - "traefik.http.routers.${PROJECT_NAME}.rule=Host(`${PROJECT_DOMAIN}`)"
      - "traefik.http.routers.${PROJECT_NAME}.entrypoints=websecure"

      # Required: SSL certificate
      - "traefik.http.routers.${PROJECT_NAME}.tls=true"
      - "traefik.http.routers.${PROJECT_NAME}.tls.certresolver=cloudflare"

      # Required: Port mapping
      - "traefik.http.services.${PROJECT_NAME}.loadbalancer.server.port=80"
```

### 3. NO Port Exposure

Don't expose ports directly - Traefik handles that:

```yaml
# DON'T DO THIS:
ports:
  - "8000:8000" # ❌ No direct port exposure

# Traefik routes traffic internally via Docker network
```

## Step-by-Step Deployment

### 1. Create Project Directory

```bash
cd ~/projects
mkdir myapp
cd myapp
```

### 2. Set Up Your Project Structure

```markdown
myapp/
├── docker-compose.staging.yml
├── nginx.conf
├── .env
├── backend/
│ ├── Dockerfile
│ ├── requirements.txt
│ └── [Django code]
└── frontend/
├── Dockerfile
├── package.json
└── [Vue.js code]
```

### 3. Configure Environment Variables

Create `.env` in your project directory:

```bash
# Project identification
PROJECT_NAME=myapp
PROJECT_DOMAIN=myapp-staging.example.com

# Django settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False

# Database
POSTGRES_PASSWORD=secure-password-here

# Redis (if using)
REDIS_PASSWORD=redis-password-here
```

### 4. Example docker-compose.staging.yml

```yaml
version: "3.8"

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
      - proxy # MUST be on proxy network for Traefik
      - internal # For backend communication
    labels:
      # Traefik configuration
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
      - internal # Only internal, not exposed to proxy
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
      - internal # Only internal

volumes:
  postgres_data:

networks:
  proxy:
    external: true # REQUIRED: Uses Traefik's network
  internal:
    driver: bridge
```

### 5. Deploy Your Project

```bash
# From your project directory (e.g., ~/projects/myapp)
docker-compose -f docker-compose.staging.yml up -d --build
```

### 6. Check Deployment

```bash
# View logs
docker-compose -f docker-compose.staging.yml logs -f

# Check if registered with Traefik
docker logs traefik | grep myapp

# Test with curl
curl -I https://myapp-staging.example.com
```

## Common Issues and Solutions

### SSL Certificate Not Working

- Ensure your domain points to the server IP in Cloudflare
- Check Traefik logs: `docker logs traefik`
- Verify labels are correct in docker-compose.yml

### 502 Bad Gateway

- Check if your service is running: `docker ps`
- Verify the port in loadbalancer.server.port matches your service
- Ensure service is on the proxy network

### Service Not Accessible

- Confirm Traefik can see it: `docker exec traefik wget -O- http://localhost:8080/api/http/routers`
- Check network connectivity: `docker network inspect proxy`
- Verify traefik.enable=true label is set

### Container Can't Connect to Database

- Ensure database is on the internal network
- Use container names for hostnames (e.g., `postgres` not `localhost`)
- Check environment variables are set correctly

## Best Practices

1. **Use Environment Variables**: Never hardcode sensitive data
2. **Separate Networks**: Use `proxy` for web services, `internal` for databases
3. **Container Names**: Use ${PROJECT_NAME} prefix to avoid conflicts
4. **Volumes**: Use named volumes for persistent data
5. **Restart Policy**: Use `unless-stopped` for production stability
6. **Build Context**: Keep Dockerfiles in subdirectories (backend/, frontend/)
7. **Static Files**: Serve through nginx, not Django

## Quick Deployment Checklist

- [ ] Project in `~/projects/` directory
- [ ] `.env` file with PROJECT_NAME and PROJECT_DOMAIN
- [ ] docker-compose.staging.yml with correct Traefik labels
- [ ] Service connected to `proxy` network
- [ ] DNS record points to server IP in Cloudflare
- [ ] No direct port exposure in docker-compose
- [ ] Internal services on `internal` network only

## Example Projects

Check these example configurations in `/home/hmesfin/traefik/`:

- `docker-compose.project-example.yml` - Full Django/Vue.js setup
- `nginx.example.conf` - Nginx configuration template
- `.env.project-example` - Environment variables template

## Need Help?

1. Check Traefik dashboard: <https://traefik.gojjoapps.com>
2. View Traefik logs: `docker logs traefik -f`
3. Check project logs: `docker-compose -f docker-compose.staging.yml logs`
4. Verify network: `docker network inspect proxy`%