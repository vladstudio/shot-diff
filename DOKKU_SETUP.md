# Ubuntu + Dokku Setup Guide

## Fresh Ubuntu Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Dokku (latest version)
wget https://dokku.com/install/v0.36.3/bootstrap.sh
sudo DOKKU_TAG=v0.36.3 bash bootstrap.sh

# Install Let's Encrypt plugin
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
```

## Deploy Python Flask App

```bash
# Create app
sudo dokku apps:create shot-diff

# Set domain
sudo dokku domains:set shot-diff domain.com

# Deploy from GitHub
sudo dokku git:sync shot-diff https://github.com/username/repo.git main

# Build and deploy
sudo dokku ps:rebuild shot-diff

# Enable HTTPS
sudo dokku letsencrypt:set shot-diff email email@example.com
sudo dokku letsencrypt:enable shot-diff
```

## Required Files in Your Repo

- `Procfile`: `web: gunicorn server:app`
- `.python-version`: `3.11`
- `requirements.txt`: List your dependencies
- Use `opencv-python-headless` instead of `opencv-python` for headless servers

## Useful Commands

```bash
# Check app status
sudo dokku ps:report shot-diff

# View logs
sudo dokku logs shot-diff

# Restart app
sudo dokku ps:restart shot-diff

# Destroy app
sudo dokku apps:destroy shot-diff
```