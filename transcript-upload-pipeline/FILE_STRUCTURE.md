# 📁 File Structure Guide

Guide complet de la structure du projet et des fichiers clés.

## 📦 Structure Complète

```
khallinetfaker-frontend/
├── .github/                    # GitHub configuration
│   └── workflows/             # CI/CD pipelines
│
├── app/                       # Next.js App Router
│   ├── page.tsx              # Home page (redirection)
│   ├── layout.tsx            # Root layout
│   ├── globals.css           # Global styles
│   ├── auth/
│   │   └── page.tsx          # Login / Sign up page
│   └── chat/
│       └── page.tsx          # Chat main interface
│
├── components/                # React components
│   ├── sidebar.tsx           # Navigation sidebar
│   ├── chat-interface.tsx    # Chat UI principal
│   ├── upload-modal.tsx      # File upload modal
│   ├── actions-panel.tsx     # Quick action buttons
│   └── ui/
│       └── button.tsx        # Reusable UI components
│       └── input.tsx         # Input components
│
├── lib/                       # Utilities & helpers
│   ├── api.ts                # Axios API client
│   ├── store.ts              # Zustand state store
│   ├── auth-utils.ts         # Token management
│   └── utils.ts              # Helper functions (cn, etc)
│
├── hooks/                     # Custom React hooks
│   └── useApi.ts             # API hook for data fetching
│
├── types/                     # TypeScript definitions
│   └── index.ts              # Global types
│
├── public/                    # Static assets
│   └── [icons, images]
│
├── .env.local                 # Environment variables (local)
├── .env.local.example         # Example env template
├── .gitignore                 # Git ignore rules
├── middleware.ts              # Next.js middleware (auth)
├── next.config.mjs            # Next.js configuration
├── tsconfig.json              # TypeScript config
├── tailwind.config.ts         # Tailwind CSS config
├── postcss.config.mjs         # PostCSS config
├── package.json               # Dependencies
├── pnpm-lock.yaml             # Dependency lock file
│
├── 📖 Documentation
│   ├── README.md              # Main documentation
│   ├── QUICKSTART.md          # 5-minute setup guide
│   ├── FRONTEND_SETUP.md      # Complete setup guide
│   ├── CONFIG.md              # Configuration guide
│   ├── API_INTEGRATION.md     # API endpoints doc
│   ├── DEPLOY.md              # Deployment guide
│   ├── COMMANDS.md            # Commands reference
│   └── FILE_STRUCTURE.md      # This file
│
└── .vercel/                   # Vercel configuration (auto-generated)
```

---

## 🔑 Key Files Explained

### 1. Core Application

#### `app/layout.tsx`
```typescript
// Root layout for entire app
// Imports fonts, global styles
// Wraps all pages
// Metadata & viewport settings
```

**Modify when:**
- Adding new fonts
- Adding global providers
- Changing metadata

#### `app/page.tsx`
```typescript
// Home page / landing page
// Currently redirects to /auth or /chat
```

**Modify when:**
- You want a public landing page
- Change redirect logic

#### `middleware.ts`
```typescript
// Runs before each request
// Handles auth redirects
// Can add logging, headers, etc
```

**Modify when:**
- Adding rate limiting
- Adding request logging
- Changing auth flow

---

### 2. Pages

#### `app/auth/page.tsx`
```typescript
// Login & Sign up page
// Form handling
// User authentication
// Token storage
```

**Features:**
- Register new user
- Login existing user
- Error handling
- Toggle between login/signup

**Modify when:**
- Adding OAuth / social login
- Changing form layout
- Adding email verification

#### `app/chat/page.tsx`
```typescript
// Main chat interface
// Protected route (requires auth)
// Displays sidebar + chat
```

**Modify when:**
- Changing layout
- Adding new features
- Changing route structure

---

### 3. Components

#### `components/sidebar.tsx`
```typescript
// Left navigation bar
// New Chat button
// Upload Transcript button
// Chat history list
// User profile section
// Logout button
```

**Key Functions:**
- `handleNewChat()`: Create new conversation
- `handleLogout()`: Logout user
- Displays chat list from Zustand store

**Modify when:**
- Adding new navigation items
- Changing chat list display
- Adding user menu items

#### `components/chat-interface.tsx`
```typescript
// Main chat area
// Message display
// Input field
// Loading states
// Actions panel
```

**Key Functions:**
- `handleSendMessage()`: Send message to API
- Auto-scroll to latest message
- Show typing indicator
- Display errors

**Modify when:**
- Changing message layout
- Adding new features (reactions, etc)
- Changing input behavior

#### `components/upload-modal.tsx`
```typescript
// File upload dialog
// Drag & drop support
// File validation
// Upload progress
```

**Key Functions:**
- `handleDrop()`: Handle file drop
- `handleFile()`: Upload file to backend
- Form validation

**Modify when:**
- Supporting more file types
- Changing UI
- Adding upload progress bar

#### `components/actions-panel.tsx`
```typescript
// Quick action buttons
// Get Summary
// Ask Questions
// Start Chat
```

**Key Functions:**
- `handleGetSummary()`: Call AI summary endpoint
- `handleAskQuestions()`: Ask AI for questions
- `handleStartChat()`: Start conversation

**Modify when:**
- Adding new AI actions
- Changing button layout
- Adding more prompts

---

### 4. Libraries

#### `lib/api.ts`
```typescript
// Axios HTTP client
// All API endpoints
// Request interceptors
// Error handling
```

**Exports:**
- `authAPI`: Register/Login
- `transcriptAPI`: Upload file
- `chatAPI`: Send message
- `healthAPI`: Health check

**When to modify:**
- Adding new endpoints
- Changing request format
- Adding response transformation

**Example:**
```typescript
import { chatAPI } from '@/lib/api';

const response = await chatAPI.send(
  transcript_id,
  message,
  thread_id
);
```

#### `lib/store.ts`
```typescript
// Zustand state management
// Auth store (token, user)
// Chat store (messages, conversations)
```

**Auth Store:**
```typescript
const { token, user, setToken, logout } = useAuthStore();
```

**Chat Store:**
```typescript
const { chats, currentChat, createChat } = useChatStore();
```

**Persisted in localStorage:**
- `auth-storage`: Token + user
- `chat-storage`: Chats + messages

**When to modify:**
- Adding new state
- Changing persistence logic
- Adding new actions

#### `lib/auth-utils.ts`
```typescript
// Token management utilities
// Save / get / remove token
// Check if authenticated
```

**Functions:**
- `TokenUtils.setToken()`: Save token
- `TokenUtils.getToken()`: Retrieve token
- `TokenUtils.removeToken()`: Delete token
- `TokenUtils.isAuthenticated()`: Check auth

---

### 5. Hooks

#### `hooks/useApi.ts`
```typescript
// Custom hook for API calls
// Loading state
// Error handling
// Success callbacks
```

**Usage:**
```typescript
const { data, loading, error, execute } = useApi(
  (msg) => chatAPI.send('id', msg, 'thread'),
  {
    onSuccess: (data) => console.log('Sent'),
    onError: (error) => console.error('Failed')
  }
);
```

---

### 6. Types

#### `types/index.ts`
```typescript
// TypeScript type definitions
// User, Transcript, Chat, etc
// API request/response types
```

**Types defined:**
- `User`: User object
- `Transcript`: File metadata
- `MeetingMinutes`: AI analysis
- `Chat`: Conversation
- `ChatMessage`: Message
- `AuthResponse`: Token response
- `UploadResponse`: Upload response

**When to modify:**
- Adding new fields to models
- Changing API responses
- Adding new types

---

### 7. Configuration Files

#### `.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Purpose:** Backend API URL (public, sent to client)

**Important:** 
- `NEXT_PUBLIC_` prefix = visible to client
- Other secrets go in `.env` (server only)

#### `next.config.mjs`
```javascript
// Next.js build configuration
// Webpack settings
// Environment variables
```

#### `tsconfig.json`
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]  // Import alias
    }
  }
}
```

Enables: `import { Button } from '@/components/ui/button'`

#### `tailwind.config.ts`
```typescript
// Tailwind CSS customization
// Colors, fonts, spacing
// Plugins
```

#### `postcss.config.mjs`
```javascript
// PostCSS plugins
// Tailwind processing
// Autoprefixer
```

---

## 📂 File Locations & Purposes

| File | Purpose | Edit? |
|------|---------|-------|
| `app/page.tsx` | Home/landing | Sometimes |
| `app/auth/page.tsx` | Login/Signup | Rare |
| `app/chat/page.tsx` | Chat main | Rare |
| `lib/api.ts` | API endpoints | Never* |
| `lib/store.ts` | State | Rare |
| `components/chat-interface.tsx` | Chat UI | Often |
| `components/sidebar.tsx` | Navigation | Often |
| `.env.local` | Config | Every setup |
| `package.json` | Dependencies | Rarely |

*Never = Perfect match with backend, no changes needed

---

## 🔄 Data Flow

```
User Input (UI)
    ↓
Component (chat-interface.tsx)
    ↓
API Call (lib/api.ts)
    ↓
Backend (FastAPI)
    ↓
Response
    ↓
Store Update (lib/store.ts)
    ↓
Re-render (React)
    ↓
Updated UI
```

---

## 📊 Component Hierarchy

```
RootLayout (app/layout.tsx)
├── /auth
│   └── AuthPage (app/auth/page.tsx)
│
└── /chat
    └── ChatPage (app/chat/page.tsx)
        ├── Sidebar (sidebar.tsx)
        │   └── UploadModal (upload-modal.tsx)
        │
        └── ChatInterface (chat-interface.tsx)
            ├── ActionsPanel (actions-panel.tsx)
            └── Message List
```

---

## 🎯 Where to Make Common Changes

### Add a new page
1. Create `app/my-page/page.tsx`
2. Add route to sidebar if needed
3. Import components

### Add a new API endpoint
1. Add endpoint to `lib/api.ts`
2. Create component to call it
3. Add to actions or interface

### Add a new component
1. Create `components/my-component.tsx`
2. Import where needed
3. Pass props from parent

### Change styling
1. Modify Tailwind classes in components
2. Or update `tailwind.config.ts` for globals
3. Refresh browser

### Change API URL
1. Update `.env.local`
2. Restart `pnpm dev`

### Add environment variable
1. Add to `.env.local`
2. Use with `process.env.VAR_NAME`
3. Must restart dev server

---

## 🔍 Finding Things

### Find all API calls
```bash
grep -r "chatAPI\|transcriptAPI\|authAPI" components/ app/ lib/
```

### Find all component usage
```bash
grep -r "<ChatInterface\|<Sidebar\|<UploadModal>" .
```

### Find all state usage
```bash
grep -r "useAuthStore\|useChatStore" components/ app/
```

### Find all types usage
```bash
grep -r "User\|Transcript\|Chat" types/
```

---

## 🧹 Cleaning Up

### Remove unused files
```bash
# Find unused imports
pnpm lint --fix

# Remove unused components
# Manually delete from components/
```

### Update imports after moving files
```bash
# VS Code: 
# Right-click file → Rename → automatically updates imports
```

---

## 📚 Additional Resources

- [Next.js File Conventions](https://nextjs.org/docs/app/getting-started/project-structure)
- [React Best Practices](https://react.dev/learn)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Pro tip:** Use `Ctrl/Cmd + P` in VS Code to quickly open any file! 🚀
