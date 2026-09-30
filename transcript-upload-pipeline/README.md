# KhalliNetfaker - Meeting Intelligence Agent Frontend

Un frontend Next.js complet et prêt à l'emploi pour le backend FastAPI KhalliNetfaker.

## 🚀 Démarrage rapide

### Prérequis

- Node.js 18+ 
- pnpm (ou npm/yarn)
- Backend FastAPI en cours d'exécution

### Installation

1. **Installez les dépendances:**
```bash
pnpm install
```

2. **Configurez l'URL du backend:**

Éditez `.env.local` et mettez à jour `NEXT_PUBLIC_API_URL`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Si votre backend est sur un autre serveur:
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

3. **Lancez le serveur de développement:**
```bash
pnpm dev
```

L'application sera accessible à `http://localhost:3000`

## 📋 Fonctionnalités

### ✅ Authentication
- ✔ Login/Sign up avec JWT
- ✔ Gestion automatique des tokens
- ✔ Persistance de session

### ✅ Chat Interface
- ✔ Upload de fichiers .txt
- ✔ Historique des conversations
- ✔ Interface responsive
- ✔ Gestion des messages en temps réel

### ✅ Actions rapides
- ✔ **Get Summary**: Résumé IA de la réunion
- ✔ **Ask Questions**: Questions importantes à poser
- ✔ **Chat**: Discussion libre sur le contenu

### ✅ Sidebar
- ✔ New Chat: créer une nouvelle conversation
- ✔ Upload Transcript: télécharger une nouvelle transcription
- ✔ Chat History: voir toutes les conversations
- ✔ User Profile: gérer le compte

## 🔗 Intégration Backend

Le frontend est **100% compatible** avec votre backend FastAPI. Les endpoints suivants sont utilisés:

### Authentication
- `POST /api/auth/register` - Créer un compte
- `POST /api/auth/login` - Se connecter

### Transcripts
- `POST /api/transcripts` - Uploader une transcription

### Chat
- `POST /api/chat` - Envoyer un message

### Health Check
- `GET /api/health` - Vérifier la santé de l'API

## 📁 Structure du projet

```
├── app/
│   ├── layout.tsx           # Layout principal
│   ├── page.tsx             # Page d'accueil (redirection)
│   ├── auth/
│   │   └── page.tsx         # Page Login/Sign up
│   └── chat/
│       └── page.tsx         # Page Chat
├── components/
│   ├── sidebar.tsx          # Barre latérale
│   ├── chat-interface.tsx   # Interface de chat
│   ├── upload-modal.tsx     # Modal upload
│   ├── actions-panel.tsx    # Actions rapides
│   └── ui/                  # Composants shadcn
├── lib/
│   ├── api.ts               # Client API (axios)
│   ├── store.ts             # State management (zustand)
│   └── auth-utils.ts        # Utilitaires auth
├── middleware.ts            # Redirection auth
└── .env.local              # Configuration (URL backend)
```

## 🎨 Styling

- **Tailwind CSS** pour le styling
- **Thème sombre** par défaut (slate/bleu/cyan)
- **Design responsive** mobile-first

## 🔐 Sécurité

- Tokens JWT stockés dans `localStorage`
- Tokens inclus automatiquement dans les requêtes API
- Redirection automatique pour non-authentifiés
- Validation côté client des entrées

## 🚢 Déploiement

### Vercel (recommandé)

```bash
# Push à GitHub
git push origin main

# Connect sur Vercel via dashboard
# Les variables d'env seront configurées automatiquement
```

### Variables d'environnement à définir sur Vercel:
```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

### Build pour production

```bash
pnpm build
pnpm start
```

## 🐛 Troubleshooting

### Erreur "API_URL not set"
→ Vérifiez que `.env.local` contient `NEXT_PUBLIC_API_URL`

### Erreur "Unauthorized" à l'upload
→ Assurez-vous que le backend est en cours d'exécution
→ Vérifiez que l'URL du backend est correcte dans `.env.local`

### Messages ne s'affichent pas
→ Ouvrez la console du navigateur (F12) pour voir les erreurs
→ Vérifiez les logs du backend pour les erreurs API

### CORS errors
→ Vérifiez que le backend a CORSMiddleware activé avec `allow_origins=["*"]`

## 📚 Ressources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com)
- [Zustand](https://github.com/pmndrs/zustand)
- [Axios](https://axios-http.com)

## 📝 Notes

- Le frontend utilise **Zustand** pour la gestion d'état local
- Les conversations sont sauvegardées dans `localStorage` (persistance client)
- Les messages sont sauvegardés dans la DB backend via `/api/chat`
- Support complet du **French language** dans l'interface

## ✨ Prochaines étapes

Vous pouvez facilement étendre ce frontend avec:
- Notifications en temps réel (WebSocket)
- Upload d'autres formats (PDF, audio)
- Intégration Calendrier
- Export de rapports
- Collaborations multi-utilisateurs

---

**Créé avec ❤️ pour KhalliNetfaker**
