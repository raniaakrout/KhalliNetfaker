'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function Page() {
  const router = useRouter();
  const { token } = useAuthStore();

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken || token) {
      router.push('/chat');
    } else {
      router.push('/auth');
    }
  }, [token, router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-900">
      <div className="text-center">
        <div className="animate-pulse">
          <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading...</p>
        </div>
      </div>
    </main>
  );
}
