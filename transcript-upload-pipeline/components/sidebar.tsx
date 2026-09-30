'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuthStore, useChatStore } from '@/lib/store';
import { useState, useEffect } from 'react';
import { UploadModal } from './upload-modal';
import { BenchmarkModal } from './benchmark-modal';
import { BenchmarkResults } from './benchmark-results';
import { BenchmarkProgressModal } from './benchmark-progress-modal';
import { benchmarkAPI, chatAPI, BenchmarkRequest, BenchmarkResponse } from '@/lib/api';

export function Sidebar() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { chats, currentChatId, setCurrentChat, createChat, deleteChat, setChats } = useChatStore();
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isBenchmarkOpen, setIsBenchmarkOpen] = useState(false);
  const [benchmarkResults, setBenchmarkResults] = useState<BenchmarkResponse | null>(null);
  const [benchmarkLoading, setBenchmarkLoading] = useState(false);
  const [activeBenchmarkRequest, setActiveBenchmarkRequest] = useState<BenchmarkRequest | null>(null);

  // Sync past conversation history from PostgreSQL on login or page load
  useEffect(() => {
    if (!user) return;
    const fetchChats = async () => {
      try {
        const res = await chatAPI.list();
        if (res.data && Array.isArray(res.data) && res.data.length > 0) {
          const backendChats = res.data;
          setChats(backendChats);
          if (!currentChatId && backendChats.length > 0) {
            setCurrentChat(backendChats[0].id);
          }
        }
      } catch (err) {
        console.error('Error fetching chat history from backend:', err);
      }
    };
    fetchChats();
  }, [user?.user_id]);

  const handleLogout = () => {
    logout(); // clears localStorage token + chat store + httpOnly cookie
    setCurrentChat(null);
    router.push('/auth');
  };

  const handleNewChat = () => {
    const chatId = createChat('', 'New Conversation');
    setCurrentChat(chatId);
  };

  return (
    <div className="w-64 bg-slate-900 border-r border-slate-700 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
            </svg>
          </div>
          <div>
            <h1 className="text-white font-bold text-sm">KhalliNetfaker</h1>
            <p className="text-slate-400 text-xs">Agent</p>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-4 space-y-2">
        <Button
          onClick={handleNewChat}
          className="w-full bg-slate-800 hover:bg-slate-700 text-white border border-slate-600 justify-start gap-2"
        >
          <span className="text-lg">+</span>
          New Chat
        </Button>
        <Button
          onClick={() => setIsUploadOpen(true)}
          className="w-full bg-slate-800 hover:bg-slate-700 text-white border border-slate-600 justify-start gap-2"
        >
          <span className="text-lg">📤</span>
          Upload Transcript
        </Button>
        <Button
          onClick={() => setIsBenchmarkOpen(true)}
          className="w-full bg-slate-800 hover:bg-slate-700 text-white border border-slate-600 justify-start gap-2"
        >
          <span className="text-lg">🔬</span>
          Benchmarking
        </Button>
      </div>

      {/* Chat Contexts */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <p className="text-slate-400 text-xs font-semibold mb-3 px-2">CHAT CONTEXTS</p>
        <div className="space-y-2">
          {chats.filter((c) => c.user_id === user?.user_id).length === 0 ? (
            <p className="text-slate-500 text-xs px-2 py-2">No conversations</p>
          ) : (
            chats
              .filter((c) => c.user_id === user?.user_id)
              .map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => setCurrentChat(chat.id)}
                  className={`w-full text-left p-3 rounded-lg transition-all text-sm ${
                    currentChatId === chat.id
                      ? 'bg-slate-700 text-white border border-cyan-500'
                      : 'text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <div className="font-semibold truncate">{chat.title}</div>
                  <div className="text-xs text-slate-500 truncate">{chat.subtitle}</div>
                </button>
              ))
          )}
        </div>
      </div>

      {/* User Section */}
      <div className="border-t border-slate-700 p-4">
        <div className="bg-slate-800 rounded-lg p-3 mb-3">
          <p className="text-slate-300 text-xs font-semibold">{user?.email || 'User'}</p>
          <p className="text-slate-500 text-xs truncate">{user?.email}</p>
          <p className="text-slate-500 text-xs mt-1">Free Plan</p>
        </div>
        <Button
          onClick={handleLogout}
          className="w-full bg-slate-700 hover:bg-slate-600 text-white text-sm py-2"
        >
          Logout
        </Button>
      </div>

      {/* Upload Modal */}
      <UploadModal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} />

      {/* Benchmark Modal */}
      <BenchmarkModal
        isOpen={isBenchmarkOpen}
        onClose={() => setIsBenchmarkOpen(false)}
        onRunBenchmark={async (request: BenchmarkRequest) => {
          setActiveBenchmarkRequest(request);
          setBenchmarkLoading(true);
          try {
            const res = await benchmarkAPI.run(request);
            setBenchmarkResults(res.data);
          } catch (error) {
            console.error('Benchmark failed:', error);
            alert('Benchmark failed. Check console for details.');
          } finally {
            setBenchmarkLoading(false);
          }
        }}
      />

      {/* Benchmark Progress & Live Logs Modal */}
      <BenchmarkProgressModal
        isOpen={benchmarkLoading}
        request={activeBenchmarkRequest}
      />

      {/* Benchmark Results */}
      <BenchmarkResults
        results={benchmarkResults}
        onClose={() => setBenchmarkResults(null)}
      />
    </div>
  );
}
