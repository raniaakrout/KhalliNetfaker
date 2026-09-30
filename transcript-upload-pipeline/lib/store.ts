import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Chat {
  id: string;
  user_id?: string;
  transcript_id: string;
  title: string;
  subtitle: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    chunk_ids?: string[];
  }>;
  created_at: Date;
}

interface AuthStore {
  token: string | null;
  user: { user_id: string; username: string; email: string } | null;
  setToken: (token: string) => void;
  setUser: (user: any) => void;
  logout: () => void;
}

interface ChatStore {
  chats: Chat[];
  currentChatId: string | null;
  transcripts: Array<{ transcript_id: string; filename: string }>;

  createChat: (transcript_id: string, title: string) => string;
  setCurrentChat: (chatId: string | null) => void;
  addMessage: (chatId: string, role: 'user' | 'assistant', content: string, chunk_ids?: string[]) => void;
  addTranscript: (transcript_id: string, filename: string) => void;
  getChat: (chatId: string) => Chat | undefined;
  /** Returns only chats belonging to the currently logged-in user. */
  getAllChats: () => Chat[];
  deleteChat: (chatId: string) => void;
  setChatTranscript: (chatId: string, transcript_id: string, subtitle?: string) => void;
  setChats: (chats: Chat[]) => void;
  /** Wipe all chat & transcript data (called on logout / user switch). */
  clearAll: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      setToken: (token) => {
        localStorage.setItem('token', token);
        set({ token });
      },
      setUser: (user) => {
        // If a different user logs in, wipe all previous chat data to prevent cross-user leakage
        const previousUserId = get().user?.user_id;
        if (user && previousUserId && previousUserId !== user.user_id) {
          useChatStore.getState().clearAll();
        }
        set({ user });
      },
      logout: () => {
        // Clear localStorage token
        localStorage.removeItem('token');
        // Wipe all chat data so the next user starts with a clean slate
        useChatStore.getState().clearAll();
        // Ask the backend to delete the httpOnly cookie (JS cannot do this directly)
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/logout`, {
          method: 'POST',
          credentials: 'include',
        }).catch(() => {/* ignore network errors on logout */});
        set({ token: null, user: null });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      chats: [],
      currentChatId: null,
      transcripts: [],

      createChat: (transcript_id, title) => {
        const chatId = `chat_${Date.now()}`;
        const user = useAuthStore.getState().user;
        const user_id = user?.user_id || '';

        const newChat: Chat = {
          id: chatId,
          user_id,
          transcript_id,
          title,
          subtitle: 'New conversation',
          messages: [],
          created_at: new Date(),
        };
        set((state) => ({
          chats: [newChat, ...state.chats],
          currentChatId: chatId,
        }));
        return chatId;
      },

      setCurrentChat: (chatId) => {
        set({ currentChatId: chatId });
      },

      addMessage: (chatId, role, content, chunk_ids) => {
        set((state) => ({
          chats: state.chats.map((chat) =>
            chat.id === chatId
              ? {
                  ...chat,
                  messages: [
                    ...chat.messages,
                    {
                      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                      role,
                      content,
                      timestamp: new Date(),
                      chunk_ids,
                    },
                  ],
                }
              : chat
          ),
        }));
      },

      addTranscript: (transcript_id, filename) => {
        set((state) => ({
          transcripts: [
            ...state.transcripts,
            { transcript_id, filename },
          ],
        }));
      },

      getChat: (chatId) => {
        const currentUserId = useAuthStore.getState().user?.user_id;
        const chat = get().chats.find((c) => c.id === chatId);
        // Only return the chat if it belongs to the current user
        if (!chat || chat.user_id !== currentUserId) return undefined;
        return chat;
      },

      getAllChats: () => {
        // Always scope to the current user — never expose another user's chats
        const currentUserId = useAuthStore.getState().user?.user_id;
        if (!currentUserId) return [];
        return get().chats.filter((chat) => chat.user_id === currentUserId);
      },

      setChats: (chats) => {
        set({ chats });
      },

      clearAll: () => {
        // Called on logout or user switch to prevent cross-user data leakage
        set({ chats: [], transcripts: [], currentChatId: null });
      },

      deleteChat: (chatId) => {
        set((state) => ({
          chats: state.chats.filter((chat) => chat.id !== chatId),
          currentChatId: state.currentChatId === chatId ? null : state.currentChatId,
        }));
      },
      setChatTranscript: (chatId, transcript_id, subtitle) => {
        set((state) => ({
          chats: state.chats.map((chat) =>
            chat.id === chatId
              ? {
                  ...chat,
                  transcript_id,
                  subtitle: subtitle || chat.subtitle,
                }
              : chat
          ),
        }));
      },
    }),
    {
      name: 'chat-storage',
    }
  )
);
