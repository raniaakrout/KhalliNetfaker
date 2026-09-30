# 🔧 Commands Reference

Toutes les commandes essentielles pour développement et production.

## 📖 Development

```bash
# Installer dépendances
pnpm install

# Démarrer serveur de développement
pnpm dev

# Open http://localhost:3000
```

---

## 🏗️ Build & Production

```bash
# Build pour production
pnpm build

# Démarrer serveur production
pnpm start

# Analyser bundle size
pnpm analyze

# Type check
pnpm type-check
```

---

## 🧪 Testing & Linting

```bash
# Linter (ESLint)
pnpm lint

# Fix linting errors
pnpm lint --fix

# Format code (Prettier)
pnpm format
```

---

## 🔄 Git Commands

```bash
# Clone repo
git clone https://github.com/USERNAME/khallinetfaker-frontend.git
cd khallinetfaker-frontend

# Create new branch
git checkout -b feature/awesome-feature

# Commit changes
git add .
git commit -m "Add awesome feature"

# Push to GitHub
git push origin feature/awesome-feature

# Create Pull Request (on GitHub)

# Merge to main
git checkout main
git merge feature/awesome-feature
git push origin main
```

---

## 🚀 Deployment Commands

### Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy (preview)
vercel

# Deploy to production
vercel --prod

# List deployments
vercel list

# Remove deployment
vercel remove khallinetfaker-frontend
```

### Docker

```bash
# Build image
docker build -t khallinetfaker-frontend:latest .

# Run container
docker run -d -p 3000:3000 khallinetfaker-frontend:latest

# View logs
docker logs khallinetfaker-frontend

# Stop container
docker stop khallinetfaker-frontend

# Remove container
docker rm khallinetfaker-frontend

# Push to Docker Hub
docker tag khallinetfaker-frontend:latest USERNAME/khallinetfaker-frontend:latest
docker push USERNAME/khallinetfaker-frontend:latest
```

---

## 🖥️ VPS / Server Commands

### SSH & File Transfer

```bash
# SSH into server
ssh user@your-vps-ip

# Copy file to server
scp file.txt user@your-vps-ip:/home/user/

# Copy from server
scp user@your-vps-ip:/home/user/file.txt ./
```

### Services

```bash
# Check nginx status
sudo systemctl status nginx

# Restart nginx
sudo systemctl restart nginx

# View nginx error logs
sudo tail -f /var/log/nginx/error.log

# View nginx access logs
sudo tail -f /var/log/nginx/access.log

# Check firewall
sudo ufw status

# Allow port
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
```

### SSL/Certificates

```bash
# Get SSL certificate
sudo certbot certonly --nginx -d khallinetfaker.com

# Renew certificates
sudo certbot renew

# Check certificate expiry
sudo certbot certificates

# Manual renewal
sudo certbot renew --force-renewal
```

---

## 🐛 Debugging Commands

### Frontend

```bash
# Check Next.js build errors
pnpm build

# Run in debug mode
NODE_DEBUG=* pnpm dev

# Clear cache
rm -rf .next

# Clear node_modules
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Browser DevTools

```javascript
// Console commands

// Check if token exists
localStorage.getItem('token')

// Clear storage
localStorage.clear()

// Check API connection
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(console.log)

// Check auth store
console.log(useAuthStore.getState())
```

---

## 📦 Package Management

```bash
# Add package
pnpm add package-name

# Add dev dependency
pnpm add -D package-name

# Remove package
pnpm remove package-name

# Update packages
pnpm update

# List installed packages
pnpm list

# Check outdated packages
pnpm outdated
```

---

## 📊 Database Commands

### Access Backend Database

```bash
# Connect to PostgreSQL
psql -h localhost -U username -d database_name

# Common queries
\dt                    # List tables
\du                    # List users
SELECT * FROM users;   # Query users
\q                     # Quit
```

---

## 🔍 Monitoring Commands

### Docker Containers

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# View container stats
docker stats

# View container logs
docker logs container_id

# Follow logs
docker logs -f container_id

# Exec command in container
docker exec -it container_id /bin/sh
```

### System Monitoring

```bash
# CPU / Memory usage
top

# Disk usage
df -h

# Memory usage
free -h

# Network monitoring
netstat -tuln

# Process status
ps aux | grep node
```

---

## 🌐 Network / API Testing

```bash
# Test API endpoint
curl http://localhost:8000/api/health

# Test with headers
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/chat

# POST request
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Upload file
curl -X POST http://localhost:8000/api/transcripts \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@meeting.txt"

# Check DNS
nslookup khallinetfaker.com

# Check port accessibility
nc -zv localhost 3000
```

---

## 📋 Environment Setup

```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# View environment
cat .env.local

# Export environment variable
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Use in command
NEXT_PUBLIC_API_URL=http://localhost:8000 pnpm dev
```

---

## 🧹 Cleanup Commands

```bash
# Remove build artifacts
rm -rf .next

# Remove node_modules
rm -rf node_modules

# Remove lock file (use with caution!)
rm pnpm-lock.yaml

# Clear npm cache
pnpm store prune

# Remove Docker images
docker rmi khallinetfaker-frontend:latest

# Remove Docker containers
docker rm khallinetfaker-frontend

# Disk space check
du -sh .
du -sh node_modules
```

---

## ⚡ Quick Scripts

### Setup Script

```bash
#!/bin/bash
# setup.sh

echo "Installing dependencies..."
pnpm install

echo "Creating .env.local..."
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

echo "Building..."
pnpm build

echo "✅ Setup complete!"
echo "Run 'pnpm dev' to start development"
```

Usage:
```bash
chmod +x setup.sh
./setup.sh
```

### Deploy Script

```bash
#!/bin/bash
# deploy.sh

VERSION=$1
if [ -z "$VERSION" ]; then
  echo "Usage: ./deploy.sh v1.0.0"
  exit 1
fi

echo "Building Docker image: $VERSION"
docker build -t khallinetfaker-frontend:$VERSION .

echo "Pushing to registry..."
docker tag khallinetfaker-frontend:$VERSION USERNAME/khallinetfaker-frontend:$VERSION
docker push USERNAME/khallinetfaker-frontend:$VERSION

echo "✅ Deployed version: $VERSION"
```

Usage:
```bash
chmod +x deploy.sh
./deploy.sh v1.0.0
```

---

## 📚 Useful Shortcuts

```bash
# Last command
!!

# History search
Ctrl + R

# Clear screen
clear

# Current directory
pwd

# List files
ls -la

# Create directory
mkdir -p path/to/dir

# Copy file
cp source.txt dest.txt

# Move file
mv old.txt new.txt

# Remove file
rm file.txt

# Remove directory
rm -rf directory/

# Change directory
cd /path/to/dir

# Home directory
cd ~

# Parent directory
cd ..
```

---

## 🎯 Common Workflows

### Development Workflow

```bash
# 1. Start development
pnpm dev

# 2. Make changes
# Edit files in components/, pages/, etc

# 3. Test in browser
# http://localhost:3000

# 4. Commit changes
git add .
git commit -m "Feature description"

# 5. Push to GitHub
git push origin branch-name

# 6. Create PR and merge
```

### Deployment Workflow

```bash
# 1. Build
pnpm build

# 2. Test production build
pnpm start

# 3. Tag version
git tag v1.0.0

# 4. Push to GitHub
git push origin main --tags

# 5. Deploy via Vercel (automatic)
# or manually: vercel --prod

# 6. Monitor
# Check logs and analytics
```

### Bug Fix Workflow

```bash
# 1. Create bug fix branch
git checkout -b fix/bug-description

# 2. Find and fix the bug
# Use DevTools (F12) and console.log

# 3. Test the fix
pnpm dev

# 4. Commit
git add .
git commit -m "Fix: brief description"

# 5. Push and create PR
git push origin fix/bug-description

# 6. Merge after review
```

---

## 🔗 Aliases (Optional)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias kf-dev='cd ~/khallinetfaker-frontend && pnpm dev'
alias kf-build='cd ~/khallinetfaker-frontend && pnpm build'
alias kf-lint='cd ~/khallinetfaker-frontend && pnpm lint'
alias kf-test='cd ~/khallinetfaker-frontend && pnpm test'
alias kf-clean='cd ~/khallinetfaker-frontend && rm -rf .next node_modules'
```

Then reload:
```bash
source ~/.bashrc
# or
source ~/.zshrc
```

Usage:
```bash
kf-dev      # Start development
kf-build    # Build production
kf-clean    # Clean cache
```

---

## ✅ Command Checklist

Before committing:
```bash
pnpm lint          # ✅ No linting errors
pnpm type-check    # ✅ No TypeScript errors
pnpm build         # ✅ Build succeeds
```

Before deploying:
```bash
git status         # ✅ No uncommitted changes
pnpm build         # ✅ Build succeeds
pnpm start         # ✅ Production build works
```

---

**Besoin d'aide?** Consultez le README ou les autres guides! 📚
