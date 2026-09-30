# API Integration Guide - KhalliNetfaker Frontend

Ce document explique comment le frontend communique avec votre backend FastAPI.

## 🔗 Endpoints Intégrés

### 1. Authentication

#### Register (Créer un compte)
```
POST /api/auth/register
```

**Request:**
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "user@example.com"
}
```

**Frontend Usage:**
```typescript
import { authAPI } from '@/lib/api';

const response = await authAPI.register(
  'user@example.com',
  'john_doe',
  'password'
);
```

---

#### Login (Se connecter)
```
POST /api/auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Frontend Usage:**
```typescript
import { authAPI } from '@/lib/api';

const response = await authAPI.login('user@example.com', 'password');
const token = response.data.access_token;
localStorage.setItem('token', token);
```

---

### 2. Transcripts

#### Upload Transcript
```
POST /api/transcripts
```

**Request:** (multipart/form-data)
```
file: <File> (file.txt)
```

**Response:**
```json
{
  "transcript_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "meeting_2024.txt",
  "minutes": {
    "summary": "Résumé de la réunion...",
    "key_decisions": ["Décision 1", "Décision 2"],
    "action_items": ["Action 1", "Action 2"],
    "sentiment": "positive"
  }
}
```

**Frontend Usage:**
```typescript
import { transcriptAPI } from '@/lib/api';

const file = new File(['content...'], 'meeting.txt');
const response = await transcriptAPI.upload(file);
const { transcript_id, minutes } = response.data;
```

**Autorisation:**
- Requiert un token JWT valide (header `Authorization: Bearer <token>`)
- Utilisateur doit être authentifié

---

### 3. Chat

#### Send Message
```
POST /api/chat
```

**Request:**
```json
{
  "transcript_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Résume cette réunion",
  "thread_id": "chat_1234567890"
}
```

**Response:**
```json
{
  "answer": "Réponse générée par l'IA..."
}
```

**Frontend Usage:**
```typescript
import { chatAPI } from '@/lib/api';

const response = await chatAPI.send(
  'transcript_id',
  'Message utilisateur',
  'thread_id'
);
const answer = response.data.answer;
```

**Autorisation:**
- Requiert un token JWT valide
- Utilisateur doit être authentifié

---

### 4. Health Check

#### Vérifier l'API
```
GET /api/health
```

**Response:**
```json
{
  "status": "ok"
}
```

**Frontend Usage:**
```typescript
import { healthAPI } from '@/lib/api';

await healthAPI.check();
```

---

## 🔐 Authentication & Tokens

### Flow d'authentification

```
┌─────────────┐
│   Login     │
└──────┬──────┘
       │ POST /api/auth/login
       ↓
┌──────────────────────┐
│  Backend retourne    │
│  access_token (JWT)  │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────────────┐
│ Frontend stocke dans          │
│ localStorage['token']         │
└──────┬───────────────────────┘
       │
       ↓
┌────────────────────────────────────────┐
│ Toute requête inclut le token dans     │
│ Authorization: Bearer <token>          │
└────────────────────────────────────────┘
```

### Token Interceptor

Automatiquement gérés par `lib/api.ts`:

```typescript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Gestion des tokens expiré

À implémenter selon votre backend:

```typescript
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token expiré
      localStorage.removeItem('token');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);
```

---

## 📊 Flow de données

### Upload & Chat

```
1. Upload Transcript
   ↓
   POST /api/transcripts
   ↓
   Reçoit transcript_id + MeetingMinutes
   ↓
   Crée nouveau Chat avec transcript_id
   ↓

2. Send Message
   ↓
   POST /api/chat avec transcript_id
   ↓
   Reçoit answer
   ↓
   Ajoute message au chat
   ↓

3. Chat History sauvegardé en DB
   via POST /api/chat (backend)
```

---

## 🛠️ Utilisation dans les Composants

### Exemple complet

```typescript
'use client';

import { useState } from 'react';
import { chatAPI } from '@/lib/api';
import { useApi } from '@/hooks/useApi';

export function ChatComponent() {
  const [message, setMessage] = useState('');
  
  // Utiliser le hook
  const { data, loading, error, execute } = useApi(
    (msg: string) => chatAPI.send('transcript_id', msg, 'thread_id'),
    {
      onSuccess: (data) => console.log('Message sent:', data),
      onError: (error) => console.error('Error:', error),
    }
  );

  const handleSend = async () => {
    try {
      await execute(message);
      setMessage('');
    } catch (err) {
      console.error('Failed to send message');
    }
  };

  return (
    <div>
      <input 
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message..."
      />
      <button 
        onClick={handleSend}
        disabled={loading}
      >
        {loading ? 'Sending...' : 'Send'}
      </button>
      {error && <p>Error: {error.message}</p>}
      {data && <p>Response: {data.answer}</p>}
    </div>
  );
}
```

---

## ⚠️ Gestion des Erreurs

### Types d'erreurs possibles

#### 1. Erreur d'authentification
```json
{
  "detail": "Incorrect email or password."
}
```

**Handling:**
```typescript
catch (error: any) {
  if (error.response?.status === 401) {
    console.log('Login failed');
  }
}
```

#### 2. Erreur de validation
```json
{
  "detail": "Empty file."
}
```

#### 3. Erreur serveur
```json
{
  "detail": "Internal server error"
}
```

### Gestion globale

```typescript
// lib/api.ts
api.interceptors.response.use(
  response => response,
  error => {
    const message = error.response?.data?.detail || error.message;
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);
```

---

## 📝 Variables pour les Requêtes

### Thread ID

Le `thread_id` est utilisé pour grouper les messages dans un chat:

```typescript
// Même thread = même conversation
const threadId = 'user_123_general'; // Format: user_id_context

// Ou généré automatiquement
const threadId = `chat_${Date.now()}`;
```

### Transcript ID

Le `transcript_id` identifie le fichier uploadé:

```typescript
// Reçu après upload
const transcriptId = response.data.transcript_id;

// Utilisé dans tous les chats associés au fichier
await chatAPI.send(transcriptId, message, threadId);
```

---

## 🚀 Exemples de Requêtes cURL

### 1. Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "password123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### 3. Upload

```bash
curl -X POST http://localhost:8000/api/transcripts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@meeting.txt"
```

### 4. Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript_id": "abc-123",
    "message": "Résume la réunion",
    "thread_id": "thread-1"
  }'
```

---

## ✅ Checklist d'Intégration

- [ ] Endpoints Backend fonctionnels
- [ ] CORS configuré sur backend
- [ ] Token JWT généré correctement
- [ ] Register fonctionne
- [ ] Login retourne un token
- [ ] Token stocké dans localStorage
- [ ] Token inclus dans les requêtes
- [ ] Upload accepte les .txt
- [ ] Chat sauvegarde les messages
- [ ] Réponses de l'IA générées correctement

---

## 📚 Ressources

- [Axios Documentation](https://axios-http.com/docs)
- [JWT Introduction](https://jwt.io/introduction)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)

---

**Vous êtes prêt! 🚀**
