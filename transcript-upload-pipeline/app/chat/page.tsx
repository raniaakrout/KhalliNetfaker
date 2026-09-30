'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/sidebar';
import { ChatInterface } from '@/components/chat-interface';
import { useAuthStore } from '@/lib/store';

export default function ChatPage() {
  const router = useRouter();
  const { token } = useAuthStore();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    // Check both Zustand state and localStorage (populated by setToken on login)
    const storedToken = localStorage.getItem('token');
    if (!token && !storedToken) {
      router.replace('/auth');
    }
  }, [token, router]);

  if (!isClient) {
    return null;
  }

  const hasToken = token || localStorage.getItem('token');
  if (!hasToken) {
    return null;
  }

  return (
    <div className="flex h-screen bg-slate-900">
      <Sidebar />
      <ChatInterface />
    </div>
  );
}
