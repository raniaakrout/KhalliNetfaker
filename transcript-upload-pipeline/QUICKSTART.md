# 🚀 Quick Start - KhalliNetfaker Frontend

## 5 minutes pour démarrer

### 1️⃣ Installation

```bash
# Cloner ou télécharger le projet
cd khallinetfaker-frontend

# Installer les dépendances
pnpm install
```

### 2️⃣ Configuration

Créez ou éditez `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Si le backend est ailleurs:
```env
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

### 3️⃣ Démarrer le serveur

```bash
pnpm dev
```

Ouvrez http://localhost:3000 dans votre navigateur.

---

## ✨ Workflow typique

### 1. Créer un compte

```
URL: http://localhost:3000
↓
Cliquez "S'inscrire"
↓
Email: user@example.com
Username: john_doe
Password: password123
↓
Account créé! ✅
```

### 2. Se connecter

```
URL: http://localhost:3000
↓
Cliquez "Se connecter"
↓
Email: user@example.com
Password: password123
↓
Chat Interface! 🎉
```

### 3. Uploader une transcription

```
Cliquez "Upload Transcript" (Sidebar)
↓
Déposez un fichier .txt
   ou cliquez pour sélectionner
↓
File: meeting.txt (ou tout .txt)
↓
Transcript uploadé! 📤
```

### 4. Chatter

```
Interface de chat apparaît
↓
Cliquez sur une action:
- ✨ Get Summary
- ❓ Ask Questions
- 💬 Chat
↓
OU écrivez un message personnalisé
↓
Message envoyé! 💬
```

---

## 🔗 Points d'intégration Backend

Votre backend doit exposer ces endpoints:

| Endpoint | Méthode | Autorisation | Description |
|----------|---------|--------------|-------------|
| `/api/auth/register` | POST | ❌ | Créer un compte |
| `/api/auth/login` | POST | ❌ | Se connecter |
| `/api/transcripts` | POST | ✅ JWT | Uploader un fichier |
| `/api/chat` | POST | ✅ JWT | Envoyer un message |
| `/api/health` | GET | ❌ | Vérifier la santé |

**✅ JWT** = Requis: `Authorization: Bearer <token>`

---

## 🔍 Tests rapides

### Test 1: Backend en ligne?

```bash
curl http://localhost:8000/api/health
# Attendez: {"status": "ok"}
```

### Test 2: CORS OK?

Ouvrez la console du navigateur (F12):
```javascript
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

Pas d'erreur CORS = OK ✅

### Test 3: Register fonctionne?

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123"}'
```

Attendez un user_id = OK ✅

---

## 📱 Structure des Fichiers Importants

```
PROJECT
├── lib/
│   ├── api.ts              ← Requêtes API
│   └── store.ts            ← État global
├── app/
│   ├── auth/page.tsx       ← Login/Signup
│   ├── chat/page.tsx       ← Chat principal
│   └── page.tsx            ← Redirection
├── components/
│   ├── sidebar.tsx         ← Navigation
│   ├── chat-interface.tsx  ← Chat UI
│   ├── upload-modal.tsx    ← Upload fichier
│   └── actions-panel.tsx   ← Boutons actions
└── .env.local              ← Configuration
```

---

## ⚠️ Erreurs Courantes & Solutions

### ❌ "Cannot read properties of undefined"
**Cause**: Token manquant après login
**Solution**: Vérifiez que login retourne `access_token`

### ❌ "CORS error"
**Cause**: Backend n'a pas CORS configuré
**Solution**: Vérifiez CORSMiddleware sur backend

### ❌ "Failed to upload"
**Cause**: Fichier n'est pas .txt ou trop volumineux
**Solution**: Utilisez uniquement des fichiers .txt

### ❌ "Chat message not sending"
**Cause**: transcript_id manquant
**Solution**: Assurez-vous d'avoir uploadé un fichier d'abord

---

## 🎯 Checklist Pré-Déploiement

Avant de mettre en production:

- [ ] `.env.local` contient l'URL backend correcte
- [ ] Backend est déployé et accessible
- [ ] CORS est configuré sur backend
- [ ] JWT tokens fonctionnent
- [ ] Upload de fichiers fonctionne
- [ ] Messages sont sauvegardés en DB
- [ ] UI responsive sur mobile
- [ ] Erreurs affichées correctement

---

## 📦 Build pour Production

```bash
# Build
pnpm build

# Test production build localement
pnpm start

# Ouvrez http://localhost:3000
```

---

## 🚢 Déployer sur Vercel

```bash
# 1. Push à GitHub
git add .
git commit -m "Initial commit"
git push origin main

# 2. Sur Vercel Dashboard
# - New Project → Import Git Repository
# - Sélectionner ce repo
# - Add Environment Variable:
#   NEXT_PUBLIC_API_URL=https://your-backend-api.com

# 3. Deploy!
```

---

## 📚 Documentation Complète

Pour plus de détails:

- **API Integration**: Voir `API_INTEGRATION.md`
- **Configuration**: Voir `CONFIG.md`
- **Full README**: Voir `README.md`

---

## 💡 Prochaines Étapes

Après le démarrage initial:

1. Personnaliser le branding (logo, couleurs)
2. Ajouter plus d'actions (Export PDF, etc)
3. Implémenter notifications temps réel
4. Ajouter support de plus de formats (PDF, Audio)
5. Analytics et monitoring

---

## 🆘 Support

Si vous avez des problèmes:

1. **Vérifiez les logs**: `F12` → Console
2. **Vérifiez le backend**: Testez les endpoints avec cURL
3. **Vérifiez la config**: `.env.local` correct?
4. **Redémarrez tout**: `pnpm dev` + backend

---

**C'est parti! 🎉**

Pour des questions détaillées, consultez les autres fichiers markdown.
