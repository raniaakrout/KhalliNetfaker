'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { useChatStore } from '@/lib/store';
import { chatAPI, transcriptAPI, evaluationAPI, Transcript, EvalResult } from '@/lib/api';

interface ActionItem {
  task: string;
  owner: string | null;
  deadline: string | null;
}

interface MeetingMinutesData {
  summary: string;
  key_decisions: string[];
  action_items: ActionItem[];
  sentiment: string;
  transcript_id?: string;
}

function isMeetingMinutesJSON(content: string) {
  try {
    const data = JSON.parse(content);
    return data && typeof data === 'object' && data.type === 'meeting_minutes';
  } catch {
    return false;
  }
}

interface EvalButtonProps {
  question: string;
  answer: string;
  chunks: string[];
  transcriptId: string;
}

function EvalButton({ question, answer, chunks, transcriptId }: EvalButtonProps) {
  const [evaluating, setEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState<EvalResult | null>(null);

  const handleEvaluateRag = async () => {
    if (!transcriptId) return;
    setEvaluating(true);
    try {
      const response = await evaluationAPI.evaluateRag(
        transcriptId,
        question,
        answer,
        chunks
      );
      setEvalResult(response.data);
    } catch (err) {
      console.error('Error evaluating RAG:', err);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="space-y-2">
      <button
        onClick={handleEvaluateRag}
        disabled={evaluating}
        className="text-[11px] uppercase tracking-wider text-amber-300 hover:text-amber-200 font-semibold disabled:opacity-50 transition"
      >
        {evaluating ? '⏳ Evaluating...' : '🔍 Evaluate RAG'}
      </button>
      {evalResult && (
        <div className="mt-2 p-2 bg-slate-800/50 rounded border border-slate-600/50 text-xs space-y-1">
          {evalResult.metrics.map((metric, idx) => (
            <div key={idx} className="flex justify-between items-start">
              <span className="text-slate-300">{metric.name}</span>
              <span className={metric.passed ? 'text-emerald-400' : 'text-red-400'}>
                {metric.score.toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MeetingMinutesCard({ data }: { data: MeetingMinutesData }) {
  const sentimentColors = {
    Positive: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    Neutral: 'bg-slate-100 text-slate-700 border-slate-200',
    Negative: 'bg-rose-50 text-rose-700 border-rose-100',
  };

  const sentimentClass = sentimentColors[data.sentiment as keyof typeof sentimentColors] || sentimentColors.Neutral;
  const [evaluating, setEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState<EvalResult | null>(null);
  const [showEvalPanel, setShowEvalPanel] = useState(false);
  const [referenceSummary, setReferenceSummary] = useState('');

  const handleEvaluateSummary = async (transcriptId: string) => {
    if (!transcriptId) return;
    setEvaluating(true);
    try {
      const response = await evaluationAPI.evaluateSummary(
        transcriptId,
        referenceSummary.trim() || undefined
      );
      setEvalResult(response.data);
    } catch (err) {
      console.error('Error evaluating summary:', err);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="bg-white border border-slate-100 rounded-xl shadow-md p-6 w-full max-w-xl text-slate-800 my-2">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
        <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2">
          <span>📋</span> Meeting Minutes
        </h3>
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${sentimentClass}`}>
          {data.sentiment}
        </span>
      </div>

      {/* Summary */}
      <div className="mb-6">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Summary</h4>
        <p className="text-sm text-slate-600 leading-relaxed">{data.summary}</p>
      </div>

      {/* Key Decisions */}
      {data.key_decisions && data.key_decisions.length > 0 && (
        <div className="mb-6">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Key Decisions</h4>
          <ul className="space-y-2 font-sans">
            {data.key_decisions.map((decision, index) => (
              <li key={index} className="text-sm text-slate-600 flex items-start gap-2">
                <span className="text-cyan-500 mt-0.5">✓</span>
                <span>{decision}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Action Items */}
      {data.action_items && data.action_items.length > 0 && (
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Action Items</h4>
          <div className="space-y-3">
            {data.action_items.map((item, index) => (
              <div key={index} className="bg-slate-50 border border-slate-100 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <span className="text-indigo-500 mt-0.5 text-base">🎯</span>
                  <span className="text-sm font-medium text-slate-700">{item.task}</span>
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 pl-6 text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <span>👤</span> {item.owner || 'Not specified'}
                  </span>
                  <span className="flex items-center gap-1">
                    <span>📅</span> {item.deadline || 'Not specified'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Evaluate Section */}
      <div className="mt-6 pt-4 border-t border-slate-100 space-y-3">
        {!showEvalPanel ? (
          <Button
            onClick={() => setShowEvalPanel(true)}
            disabled={evaluating}
            className="bg-amber-500 hover:bg-amber-600 text-white text-sm px-4 py-2 rounded-lg disabled:opacity-50"
          >
            🔍 Evaluate Minutes
          </Button>
        ) : (
          <div className="bg-amber-50/60 border border-amber-200/70 rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-700">
                Reference Summary (Ground Truth)
              </label>
              <button
                type="button"
                onClick={() => setShowEvalPanel(false)}
                className="text-xs text-slate-400 hover:text-slate-600"
              >
                ✕ Close
              </button>
            </div>
            <textarea
              value={referenceSummary}
              onChange={(e) => setReferenceSummary(e.target.value)}
              placeholder="Paste your expected reference summary here (optional — leave empty for intrinsic quality check)..."
              rows={3}
              className="w-full text-xs p-2 rounded border border-slate-200 focus:outline-none focus:ring-1 focus:ring-amber-400 bg-white text-slate-700"
            />
            <div className="flex items-center gap-2">
              <Button
                onClick={() => handleEvaluateSummary(data.transcript_id || '')}
                disabled={evaluating}
                className="bg-amber-500 hover:bg-amber-600 text-white text-xs px-3 py-1.5 rounded disabled:opacity-50"
              >
                {evaluating ? 'Evaluating (LLM Judge)...' : '🚀 Launch Evaluation'}
              </Button>
              <span className="text-[11px] text-slate-500">
                Grounds decisions & tasks on vector search
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Evaluation Results */}
      {evalResult && (
        <div className="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
          <h4 className="font-semibold text-slate-800 mb-3">Evaluation Results</h4>
          {evalResult.metrics.map((metric, idx) => (
            <div key={idx} className="mb-3 pb-3 border-b border-slate-200 last:border-0 last:mb-0">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-slate-700">{metric.name}</span>
                <span className={`text-sm font-bold ${metric.passed ? 'text-emerald-600' : 'text-red-600'}`}>
                  {metric.passed ? '✓ PASS' : '✗ FAIL'} ({metric.score.toFixed(2)})
                </span>
              </div>
              <p className="text-xs text-slate-600 whitespace-pre-wrap">{metric.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function ChatInterface() {
  const { currentChatId, getChat, addMessage, setChatTranscript } = useChatStore();
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [loadingSummary, setLoadingSummary] = useState(false);

  const chat = currentChatId ? getChat(currentChatId) : null;
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchTranscripts = async () => {
      try {
        const res = await transcriptAPI.list();
        setTranscripts(res.data);
      } catch (err) {
        console.error('Error fetching transcripts:', err);
      }
    };
    fetchTranscripts();
  }, [currentChatId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat?.messages]);

  const handleGetSummary = async () => {
    if (!chat || !chat.transcript_id) return;
    setLoadingSummary(true);
    setError('');
    try {
      const response = await transcriptAPI.getMinutes(chat.transcript_id);
      addMessage(chat.id, 'user', 'Summarize this meeting');
      addMessage(chat.id, 'assistant', JSON.stringify({
        type: 'meeting_minutes',
        ...response.data
      }));
    } catch (err: any) {
      console.error('Error getting summary:', err);
      setError('Error retrieving summary.');
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleSendMessage = async () => {
    if (!message.trim() || !currentChatId || !chat) return;

    const userMessage = message;
    setMessage('');
    setError('');
    setLoading(true);

    addMessage(currentChatId, 'user', userMessage);

    try {
      const response = await chatAPI.send(
        chat.transcript_id,
        userMessage,
        currentChatId
      );

      addMessage(currentChatId, 'assistant', response.data.answer, response.data.chunk_ids);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error sending message');
      addMessage(currentChatId, 'assistant', 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!chat) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gradient-to-b from-slate-800 to-slate-900 p-6">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mx-auto mb-6 shadow-xl shadow-cyan-500/10">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Welcome to KhalliNetfaker</h1>
          <p className="text-slate-400 text-sm leading-relaxed mb-6">
            Your meeting intelligence agent. Upload a transcript or select a conversation from the sidebar to extract insights, key decisions, and action items.
          </p>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs text-slate-400">
            <span>👈</span> Select or start a conversation to begin
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-slate-800">
      {/* Chat Header */}
      <div className="border-b border-slate-700 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-white font-semibold">{chat.title}</h2>
          <p className="text-slate-400 text-sm">{chat.subtitle}</p>
        </div>

        <div className="flex items-center gap-2">
          {/* Transcript Select Dropdown */}
          <div className="flex items-center gap-1.5 bg-slate-700 border border-slate-600 rounded-lg px-3 py-1.5 text-white">
            <span className="text-sm">📄</span>
            <select
              value={chat.transcript_id || ''}
              onChange={(e) => {
                const selectedId = e.target.value;
                const transcript = transcripts.find(t => t.transcript_id === selectedId);
                setChatTranscript(chat.id, selectedId, transcript ? `Transcript: ${transcript.filename}` : 'New conversation');
              }}
              className="bg-transparent text-sm font-medium focus:outline-none cursor-pointer max-w-[200px] text-slate-200"
            >
              <option value="" className="bg-slate-800 text-slate-400">Select Transcript...</option>
              {transcripts.map((t) => (
                <option key={t.transcript_id} value={t.transcript_id} className="bg-slate-800 text-slate-200">
                  {t.filename}
                </option>
              ))}
            </select>
          </div>

          {/* Persistent Get Summary Button */}
          <Button
            onClick={handleGetSummary}
            disabled={!chat.transcript_id || loadingSummary}
            className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white gap-2 text-sm font-semibold py-1.5 px-4 h-9 disabled:opacity-50"
          >
            <span>✨</span> {loadingSummary ? 'Loading...' : 'Get Summary'}
          </Button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chat.messages.length === 0 && (
          <div className="flex flex-col items-center justify-center min-h-[340px] max-w-lg mx-auto text-center px-4 py-8">
            {!chat.transcript_id ? (
              <div className="bg-slate-700/40 border border-slate-600/50 rounded-2xl p-6 shadow-xl w-full">
                <div className="w-14 h-14 rounded-2xl bg-slate-700 border border-slate-600 flex items-center justify-center text-2xl mx-auto mb-4">
                  📄
                </div>
                <h3 className="text-base font-bold text-white mb-2">Select a Meeting Transcript</h3>
                <p className="text-slate-400 text-xs leading-relaxed max-w-sm mx-auto">
                  Choose a transcript from the dropdown in the header above to ask questions or extract meeting minutes.
                </p>
              </div>
            ) : (
              <div className="w-full space-y-6">
                <div className="bg-slate-700/40 border border-slate-600/50 rounded-2xl p-6 shadow-xl">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-2xl mx-auto mb-4">
                    💡
                  </div>
                  <h3 className="text-base font-bold text-white mb-1.5">Transcript Ready</h3>
                  <p className="text-slate-400 text-xs max-w-md mx-auto leading-relaxed">
                    Ask any question about this meeting below, or click{' '}
                    <span className="text-cyan-400 font-semibold">✨ Get Summary</span> above to generate meeting minutes.
                  </p>
                </div>

                <div className="w-full">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2.5 text-center">
                    Suggested Questions
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {[
                      'What were the key decisions made?',
                      'List all action items and assignees',
                      'What were the main topics discussed?',
                      'What blockers or next steps were noted?',
                    ].map((prompt, idx) => (
                      <button
                        key={idx}
                        onClick={() => setMessage(prompt)}
                        className="p-3 rounded-xl bg-slate-700/50 hover:bg-slate-700 border border-slate-600/50 hover:border-cyan-500/40 text-left text-xs text-slate-300 hover:text-white transition-all duration-200 group flex items-start gap-2 shadow-sm"
                      >
                        <span className="text-cyan-400 group-hover:scale-110 transition-transform">💬</span>
                        <span className="leading-snug">{prompt}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        {chat.messages.length > 0 &&
          chat.messages.map((msg, msgIdx) => {
            const isSummary = msg.role === 'assistant' && isMeetingMinutesJSON(msg.content);
            const isAssistantMsg = msg.role === 'assistant' && !isSummary;
            const prevUserMsg = msgIdx > 0 ? chat.messages[msgIdx - 1] : null;
            const userQuestion = prevUserMsg?.role === 'user' ? prevUserMsg.content : '';

            return (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {isSummary ? (
                  <MeetingMinutesCard data={{...JSON.parse(msg.content), transcript_id: chat.transcript_id}} />
                ) : (
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg flex flex-col ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                        : 'bg-slate-700 text-slate-100'
                    }`}
                  >
                    <p className="text-sm break-words">{msg.content}</p>
                    {msg.chunk_ids && msg.chunk_ids.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-slate-600/50">
                        <span className="text-[10px] uppercase tracking-wider text-slate-400 block mb-1 font-semibold">Sources:</span>
                        <div className="flex flex-wrap gap-1">
                          {msg.chunk_ids.map((id, idx) => (
                            <span key={idx} className="bg-slate-800/80 text-cyan-300 text-[10px] px-2 py-0.5 rounded border border-slate-600/50 font-medium">
                              {id}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {isAssistantMsg && userQuestion && (
                      <div className="mt-2 pt-2 border-t border-slate-600/50">
                        <EvalButton
                          question={userQuestion}
                          answer={msg.content}
                          chunks={msg.chunk_ids || []}
                          transcriptId={chat.transcript_id}
                        />
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 px-4 py-2 rounded-lg">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-700 p-4">
        {error && (
          <div className="mb-3 p-2 bg-red-900 text-red-200 text-sm rounded border border-red-700">
            {error}
          </div>
        )}
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
            placeholder="Message KhalliNetfaker..."
            className="flex-1 bg-slate-700 border border-slate-600 text-white placeholder-slate-500 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500"
            disabled={loading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={loading || !message.trim()}
            className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white px-4 py-2 disabled:opacity-50"
          >
            ➤
          </Button>
        </div>
      </div>
    </div>
  );
}
