'use client';

import { Button } from '@/components/ui/button';
import { useChatStore } from '@/lib/store';
import { chatAPI, transcriptAPI } from '@/lib/api';
import { useState } from 'react';

interface ActionsPanelProps {
  transcript_id?: string;
}

export function ActionsPanel({ transcript_id }: ActionsPanelProps) {
  const { currentChatId, addMessage } = useChatStore();
  const [loading, setLoading] = useState<string | null>(null);

  if (!transcript_id || !currentChatId) return null;

  const handleGetSummary = async () => {
    setLoading('summary');
    try {
      const response = await transcriptAPI.getMinutes(transcript_id);
      addMessage(currentChatId, 'user', 'Summarize this meeting');
      addMessage(currentChatId, 'assistant', JSON.stringify({
        type: 'meeting_minutes',
        ...response.data
      }));
    } catch (error) {
      console.error('Error getting summary:', error);
    } finally {
      setLoading(null);
    }
  };

  const handleAskQuestions = async () => {
    setLoading('questions');
    try {
      const response = await chatAPI.send(
        transcript_id,
        'What are the most important questions to ask about this meeting? What are the key topics to clarify?',
        currentChatId
      );
      addMessage(currentChatId, 'user', 'Questions importantes');
      addMessage(currentChatId, 'assistant', response.data.answer);
    } catch (error) {
      console.error('Error asking questions:', error);
    } finally {
      setLoading(null);
    }
  };

  const handleStartChat = async () => {
    setLoading('chat');
    try {
      const response = await chatAPI.send(
        transcript_id,
        'Hello! Tell me about this meeting. What were the main topics discussed?',
        currentChatId
      );
      addMessage(currentChatId, 'user', 'Hello!');
      addMessage(currentChatId, 'assistant', response.data.answer);
    } catch (error) {
      console.error('Error starting chat:', error);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4">
      <Button
        onClick={handleGetSummary}
        disabled={loading === 'summary'}
        className="bg-slate-700 hover:bg-slate-600 text-white border border-slate-600 flex flex-col items-center gap-2 h-24 disabled:opacity-50"
      >
        <span className="text-2xl">✨</span>
        <span className="text-xs text-center">
          {loading === 'summary' ? 'Loading...' : 'Get Summary'}
        </span>
      </Button>

      <Button
        onClick={handleAskQuestions}
        disabled={loading === 'questions'}
        className="bg-slate-700 hover:bg-slate-600 text-white border border-slate-600 flex flex-col items-center gap-2 h-24 disabled:opacity-50"
      >
        <span className="text-2xl">❓</span>
        <span className="text-xs text-center">
          {loading === 'questions' ? 'Questions...' : 'Ask Questions'}
        </span>
      </Button>

      <Button
        onClick={handleStartChat}
        disabled={loading === 'chat'}
        className="bg-slate-700 hover:bg-slate-600 text-white border border-slate-600 flex flex-col items-center gap-2 h-24 disabled:opacity-50"
      >
        <span className="text-2xl">💬</span>
        <span className="text-xs text-center">
          {loading === 'chat' ? 'Chatting...' : 'Ask Questions'}
        </span>
      </Button>
    </div>
  );
}
