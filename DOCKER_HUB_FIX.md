# Docker Hub Authentication Fix

## Problem

When running `docker-compose up -d postgres redis`, you may see:

```
Error response from daemon: Head "https://registry-1.docker.io/v2/library/redis/manifests/7-alpine": unauthorized: email must be verified before using account
```

## Solution

### Option 1: Login to Docker Hub (Recommended)

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

Then try again:
```bash
docker-compose up -d postgres redis
```

### Option 2: Pull Images Manually (No Login Required)

The images `postgres:15-alpine` and `redis:7-alpine` are **public images** and should work without login. If you're still getting errors:

```bash
# Pull images directly
docker pull postgres:15-alpine
docker pull redis:7-alpine

# Then try docker-compose
docker-compose up -d postgres redis
```

### Option 3: Verify Docker Hub Account

If you have a Docker Hub account but still get errors:

1. Go to https://hub.docker.com
2. Verify your email address (check email for verification link)
3. Try `docker login` again

### Option 4: Use Without Docker Hub Account

If you don't want to create a Docker Hub account:

1. The images are public, so they should work without login
2. Try pulling manually first:
   ```bash
   docker pull postgres:15-alpine
   docker pull redis:7-alpine
   ```
3. If that works, then `docker-compose up -d postgres redis` should work

## Additional Notes

### Docker Compose Version Warning

If you see:
```
the attribute `version` is obsolete, it will be ignored
```

This is just a **warning** - it won't break anything. You can:
- Ignore it (it's harmless)
- Or remove the `version: "3.8"` line from `docker-compose.yml` (if you copied from example)

### Windows-Specific Issues

On Windows, make sure:
- Docker Desktop is running
- WSL 2 is enabled (if using WSL)
- Docker daemon is accessible

## Quick Test

After fixing, verify it works:

```bash
# Start services
docker-compose up -d postgres redis

# Check status
docker-compose ps

# Should show:
# NAME                STATUS
# investiq-postgres   Up (healthy)
# investiq-redis      Up (healthy)
```

