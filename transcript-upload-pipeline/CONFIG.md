# Configuration KhalliNetfaker Frontend

## Variables d'Environnement

### `.env.local` (Développement)

```env
# URL du backend FastAPI
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Exemples de configuration

#### Développement Local
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Production (Vercel)
```env
NEXT_PUBLIC_API_URL=https://api.khallinetfaker.com
```

#### Docker
```env
NEXT_PUBLIC_API_URL=http://backend:8000
```

## 🔧 Configuration Détaillée

### 1. Backend URL (REQUIRED)

La variable `NEXT_PUBLIC_API_URL` doit pointer vers votre backend FastAPI.

**Important**: Le préfixe `NEXT_PUBLIC_` rend la variable accessible côté client.

#### Vérifier la connexion:

```bash
# Test manuel
curl http://localhost:8000/api/health
```

Vous devriez recevoir:
```json
{"status": "ok"}
```

### 2. CORS et Backend

Assurez-vous que votre backend FastAPI a CORS configuré:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou ["http://localhost:3000"] en prod
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Token JWT

Les tokens JWT sont:
- Stockés dans `localStorage` sous la clé `token`
- Envoyés automatiquement dans le header `Authorization: Bearer <token>`
- Valides selon la configuration du backend

## 📦 Déploiement

### Vercel

1. **Connecter le dépôt GitHub**
```bash
git remote add origin https://github.com/YOUR_REPO
git push -u origin main
```

2. **Dashboard Vercel**
   - Nouveau projet → Importer depuis GitHub
   - Sélectionner ce dépôt
   - Ajouter la variable d'environnement

3. **Variables d'environnement (Vercel Dashboard)**
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-api.com
   ```

### Docker

Créez un `Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY . .

ENV NEXT_PUBLIC_API_URL=http://backend:8000

RUN pnpm build

EXPOSE 3000

CMD ["pnpm", "start"]
```

## 🐛 Dépannage

### Erreur: "Cannot read properties of undefined (reading 'transcript_id')"

**Cause**: La configuration du backend URL est manquante

**Solution**:
```bash
# Vérifiez .env.local
cat .env.local

# Doit contenir:
NEXT_PUBLIC_API_URL=http://localhost:8000

# Redémarrez le serveur
pnpm dev
```

### Erreur: "CORS error"

**Cause**: Le backend n'a pas CORS activé pour votre domaine

**Solution - Backend (main.py)**:
```python
# Ajouter CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Erreur: "Unauthorized" après login

**Cause**: Le token n'est pas sauvegardé correctement

**Solution**:
1. Ouvrez DevTools (F12)
2. Allez dans Application → LocalStorage
3. Vérifiez que la clé `token` existe
4. Vérifiez que sa valeur commence par `eyJ` (JWT)

### Les messages ne s'affichent pas

**Cause 1**: Erreur API non affichée

**Solution**:
```bash
# Console du navigateur (F12)
# Vous devriez voir une erreur de console

# Vérifiez les logs du backend:
# Le message doit être sauvegardé en DB
```

**Cause 2**: API retourne une erreur

**Solution**:
```python
# Vérifiez que le backend répond:
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transcript_id":"", "message":"Hello", "thread_id":"test"}'
```

## 📊 Monitoring

### Logs du Frontend

```bash
# Terminal où vous avez lancé pnpm dev
# Vous verrez les erreurs et warnings

# Pour des logs plus détaillés:
pnpm dev --verbose
```

### Logs du Backend

```bash
# Terminal du backend FastAPI
# Vous verrez les requêtes HTTP et erreurs
```

### DevTools du Navigateur

```
F12 → Console: Erreurs JavaScript
F12 → Network: Requêtes API
F12 → Application → LocalStorage: Token JWT
```

## 🔐 Sécurité

### En Développement

- localStorage n'est pas sécurisé pour les données sensibles
- Ne partagez pas votre `.env.local`

### En Production

```env
# Sur Vercel/production, utiliser HTTPS
NEXT_PUBLIC_API_URL=https://secure-api.com

# Backend doit avoir SSL/TLS
```

### Recommandations

1. **Utilisez HTTPOnly cookies** (au lieu de localStorage)
2. **Réduisez la durée de vie du token** (1 heure)
3. **Validez les requêtes côté backend**
4. **Loggez les tentatives d'accès non autorisé**

## ✅ Checklist de Configuration

- [ ] `.env.local` existe et contient `NEXT_PUBLIC_API_URL`
- [ ] Backend FastAPI est en cours d'exécution
- [ ] Backend répond à `GET /api/health`
- [ ] CORS est configuré sur le backend
- [ ] `pnpm dev` fonctionne sans erreurs
- [ ] Page de login s'affiche sur `http://localhost:3000`
- [ ] Vous pouvez créer un compte
- [ ] Vous pouvez vous connecter
- [ ] Vous pouvez uploader un fichier
- [ ] Vous pouvez envoyer un message

---

**Besoin d'aide?** Vérifiez les logs du navigateur et du backend! 🚀
