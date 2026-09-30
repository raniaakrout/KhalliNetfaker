# 🚀 Deployment Guide - KhalliNetfaker Frontend

Guide complet pour déployer le frontend en production.

## 🎯 Options de Déploiement

### Option 1: Vercel (Recommandé) ⭐

**Avantages:**
- Intégration GitHub automatique
- Preview URLs pour chaque PR
- Auto-scaling
- CDN global
- Très simple

### Option 2: Docker + VPS

**Avantages:**
- Contrôle total
- Coût prévisible
- Peut être self-hosted

### Option 3: Autres Platforms

- AWS (Amplify, S3+CloudFront)
- Google Cloud (Cloud Run)
- Azure (App Service)
- Netlify (similaire à Vercel)

---

## 📦 Vercel (Méthode Recommandée)

### Étape 1: Préparer le Repository GitHub

```bash
# Si pas déjà fait, initialiser git
git init
git add .
git commit -m "Initial commit: KhalliNetfaker Frontend"

# Créer un repo sur GitHub
# https://github.com/new
# Nom: khallinetfaker-frontend

# Ajouter remote
git remote add origin https://github.com/YOUR_USERNAME/khallinetfaker-frontend.git
git branch -M main
git push -u origin main
```

### Étape 2: Connecter sur Vercel

```bash
# Option A: Via CLI
npm install -g vercel
vercel login
vercel

# Option B: Via Dashboard
# 1. Allez sur https://vercel.com/dashboard
# 2. Click "Add New..." → "Project"
# 3. Import Git Repository
# 4. Sélectionner khallinetfaker-frontend
```

### Étape 3: Configurer Variables d'Environnement

Sur Vercel Dashboard:

```
Project Settings → Environment Variables

Variable Name: NEXT_PUBLIC_API_URL
Value: https://your-backend-api.com
```

**Important:** Assurez-vous que l'URL backend est en HTTPS en production!

### Étape 4: Deploy

```bash
vercel --prod
```

Ou via GitHub Actions (automatique après chaque push).

---

## 🐳 Docker + VPS

### Étape 1: Créer Dockerfile

Fichier: `Dockerfile`

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy code
COPY . .

# Build
RUN pnpm build

# Runtime stage
FROM node:18-alpine

WORKDIR /app

# Install production dependencies only
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --prod --frozen-lockfile

# Copy built app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Environment
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=https://api.khallinetfaker.com

# Run
EXPOSE 3000
CMD ["pnpm", "start"]
```

### Étape 2: Créer docker-compose.yml

```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.khallinetfaker.com
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Étape 3: Build & Push Image

```bash
# Build localement
docker build -t khallinetfaker-frontend:latest .

# Test localement
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://backend:8000 \
  khallinetfaker-frontend:latest

# Push to Registry (Docker Hub / ECR)
docker tag khallinetfaker-frontend:latest YOUR_REGISTRY/khallinetfaker-frontend:latest
docker push YOUR_REGISTRY/khallinetfaker-frontend:latest
```

### Étape 4: Déployer sur VPS

```bash
# SSH into VPS
ssh user@your-vps-ip

# Pull image
docker pull YOUR_REGISTRY/khallinetfaker-frontend:latest

# Run container
docker run -d \
  -p 80:3000 \
  --name khallinetfaker-frontend \
  -e NEXT_PUBLIC_API_URL=https://api.khallinetfaker.com \
  -e NODE_ENV=production \
  --restart always \
  YOUR_REGISTRY/khallinetfaker-frontend:latest
```

### Étape 5: Setup Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/khallinetfaker

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name khallinetfaker.com www.khallinetfaker.com;

    # Redirect HTTP → HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name khallinetfaker.com www.khallinetfaker.com;

    # SSL Certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/khallinetfaker.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/khallinetfaker.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Activer:
```bash
sudo ln -s /etc/nginx/sites-available/khallinetfaker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔐 SSL/TLS Setup

### Let's Encrypt (Gratuit)

```bash
# Via Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d khallinetfaker.com -d www.khallinetfaker.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 📊 Monitoring & Logging

### Application Logs (Docker)

```bash
docker logs khallinetfaker-frontend

# Follow logs
docker logs -f khallinetfaker-frontend
```

### System Monitoring

```bash
# CPU / Memory
docker stats khallinetfaker-frontend

# Or use monitoring stack:
# - Prometheus
# - Grafana
# - ELK Stack
```

### Vercel Analytics

```typescript
// app/layout.tsx - Déjà inclus
import { Analytics } from '@vercel/analytics/next'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
```

Dashboard: https://vercel.com/analytics

---

## 🔄 CI/CD Pipeline

### GitHub Actions (Vercel Auto-Deploy)

Vercel fait ça automatiquement après chaque push à `main`.

### Custom GitHub Actions

Fichier: `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Build
        run: |
          npm install -g pnpm
          pnpm install
          pnpm build

      - name: Push to Registry
        env:
          DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
          DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
        run: |
          echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
          docker build -t $DOCKER_USERNAME/khallinetfaker-frontend:latest .
          docker push $DOCKER_USERNAME/khallinetfaker-frontend:latest

      - name: Deploy to VPS
        env:
          SSH_KEY: ${{ secrets.SSH_KEY }}
          SSH_HOST: ${{ secrets.SSH_HOST }}
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh -i ~/.ssh/id_rsa user@$SSH_HOST 'docker pull YOUR_REGISTRY/khallinetfaker-frontend:latest && docker restart khallinetfaker-frontend'
```

---

## ✅ Checklist Pré-Production

- [ ] `.env.local` supprimé (les variables d'env sont en production)
- [ ] Backend API en HTTPS
- [ ] CORS configuré pour le domaine frontend
- [ ] JWT secret fort (backend)
- [ ] Database backups configurés
- [ ] Logs activés (frontend + backend)
- [ ] Monitoring activé
- [ ] SSL/TLS certifié
- [ ] Tests e2e passent
- [ ] Performance optimisée
- [ ] Analytics configurés
- [ ] Error tracking (Sentry, etc)

---

## 🚨 Troubleshooting Déploiement

### Vercel

**Problem**: Build fails
```
Solution: Vérifiez les logs de build
- Vérifiez que Node version est compatible
- Vérifiez que toutes les env vars sont définies
```

**Problem**: Site returns 500
```
Solution: Vérifiez que backend API est accessible
- Test depuis le terminal: curl NEXT_PUBLIC_API_URL
- Vérifiez CORS sur backend
```

### Docker

**Problem**: Container exits immediately
```
docker logs khallinetfaker-frontend

# Common causes:
# - Port déjà utilisé
# - Env vars manquantes
# - Build failed
```

**Problem**: Can't reach from outside
```
# Vérifiez firewall
sudo ufw allow 80
sudo ufw allow 443

# Vérifiez Nginx
sudo nginx -t
sudo systemctl status nginx
```

---

## 📈 Performance Optimization

### Vercel

Automatiquement optimisé:
- Edge caching
- Image optimization
- Code splitting
- Compression

### Docker/VPS

```bash
# Build optimisé
docker build --cache-from latest -t khallinetfaker-frontend:latest .

# Multi-stage build (voir Dockerfile ci-dessus)

# Nginx caching
add_header Cache-Control "public, max-age=3600" always;
```

---

## 🔐 Production Security

- ✅ HTTPS/SSL obligatoire
- ✅ Environment variables sécurisées
- ✅ CORS restrictif
- ✅ CSP headers
- ✅ Rate limiting backend
- ✅ Input validation
- ✅ Regular backups
- ✅ Secrets management

---

## 📝 Post-Deployment

### Tests

```bash
# Test production URL
curl https://khallinetfaker.com

# Test API connectivity
curl -X POST https://api.khallinetfaker.com/api/health

# Browser tests
# - Login
# - Upload file
# - Send message
```

### Monitoring

1. **Check logs regularly**
   ```bash
   docker logs -f khallinetfaker-frontend
   ```

2. **Monitor performance**
   - Vercel Dashboard
   - Datadog/New Relic
   - Custom monitoring

3. **Setup alerts**
   - Error rate > 1%
   - Response time > 1s
   - CPU/Memory > 80%

---

## 🔄 Rollback

### Vercel

Automatique: Cliquez "Rollback" sur le deployment précédent

### Docker

```bash
# Redéployer une version précédente
docker pull YOUR_REGISTRY/khallinetfaker-frontend:v1.0.0
docker run -d \
  -p 80:3000 \
  --name khallinetfaker-frontend \
  YOUR_REGISTRY/khallinetfaker-frontend:v1.0.0
```

---

## 📞 Support

**Issues courants:**

1. **"Cannot connect to backend"**
   - Vérifiez que backend API est accessible
   - Vérifiez URL dans variables d'env
   - Vérifiez CORS

2. **"SSL certificate error"**
   - Vérifiez expiration du certificat
   - Renouveler avec Certbot
   - Check Nginx config

3. **"Slow response time"**
   - Vérifiez backend performance
   - Vérifiez database queries
   - Activez caching

---

**Vous êtes prêt pour la production! 🚀**

Pour des questions spécifiques, consultez la documentation de votre plateforme de déploiement.
