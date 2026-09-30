'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { useChatStore, useAuthStore } from '@/lib/store';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function UploadModal({ isOpen, onClose }: UploadModalProps) {
  const [isDragging, setIsDragging]   = useState(false);
  const [loading,    setLoading]      = useState(false);
  const [error,      setError]        = useState('');
  const [success,    setSuccess]      = useState('');
  const [logs,       setLogs]         = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const logsEndRef   = useRef<HTMLDivElement>(null);
  const { addTranscript, createChat, setCurrentChat } = useChatStore();
  const { token } = useAuthStore();

  // Auto-scroll log panel to bottom on new entries
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  if (!isOpen) return null;

  const resetState = () => {
    setError('');
    setSuccess('');
    setLogs([]);
  };

  const appendLog = (msg: string) =>
    setLogs((prev) => [...prev, msg]);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
  };

  const handleFile = async (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'txt' && ext !== 'vtt') {
      setError('Please upload a .txt or .vtt file');
      return;
    }

    setLoading(true);
    resetState();
    appendLog(`📂 File selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`);

    // Build multipart form-data request manually so we can stream the response
    const formData = new FormData();
    formData.append('file', file);

    // Read token from localStorage (Axios Bearer interceptor source)
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    try {
      const res = await fetch(`${API_BASE_URL}/api/transcripts`, {
        method:      'POST',
        credentials: 'include',
        headers:     storedToken ? { Authorization: `Bearer ${storedToken}` } : {},
        body:        formData,
      });

      if (!res.ok || !res.body) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      // ── Parse SSE stream ────────────────────────────────────────────────────
      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let   buffer  = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE events are separated by '\n\n'
        const parts = buffer.split('\n\n');
        buffer = parts.pop() ?? '';  // keep incomplete last chunk

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith('data:')) continue;

          const jsonStr = line.slice('data:'.length).trim();
          try {
            const event = JSON.parse(jsonStr);

            if (event.type === 'log') {
              appendLog(event.message);

            } else if (event.type === 'done') {
              const { transcript_id, filename: fname, minutes } = event.data;
              addTranscript(transcript_id, fname);
              const chatId = createChat(transcript_id, `Chat — ${fname}`);
              chatId && setCurrentChat(chatId);
              setSuccess('✅ Transcript uploadé avec succès!');
              appendLog('🎉 Done! Chat created.');
              setTimeout(() => { onClose(); resetState(); }, 3000);

            } else if (event.type === 'error') {
              setError(event.message || 'An error occurred.');
              appendLog(`❌ Error: ${event.message}`);
            }
          } catch {
            // Malformed JSON line — skip
          }
        }
      }
    } catch (err: any) {
      const msg = err?.message || 'Upload error';
      setError(msg);
      appendLog(`❌ ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-xl border border-slate-700 w-full max-w-lg p-6 shadow-2xl">
        <h2 className="text-white text-lg font-semibold mb-4">Upload a Transcript</h2>

        {/* Drop Zone — hidden while processing */}
        {!loading && !success && (
          <div
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-cyan-500 bg-cyan-500/10'
                : 'border-slate-600 hover:border-slate-500'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.vtt"
              onChange={(e) => e.target.files && handleFile(e.target.files[0])}
              className="hidden"
            />
            <div className="text-4xl mb-3">📄</div>
            <p className="text-white font-semibold mb-1">Déposez votre fichier ici</p>
            <p className="text-slate-400 text-sm">ou cliquez pour sélectionner un fichier .txt / .vtt</p>
          </div>
        )}

        {/* ── Progress log panel ─────────────────────────────────────────── */}
        {logs.length > 0 && (
          <div className="mt-4 bg-slate-900 border border-slate-700 rounded-lg overflow-hidden">
            <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-700 bg-slate-800">
              <span className="text-xs font-mono text-cyan-400 font-semibold">PROCESSING LOG</span>
              {loading && (
                <span className="ml-auto flex gap-1">
                  {[0, 0.15, 0.3].map((delay, i) => (
                    <span
                      key={i}
                      className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce"
                      style={{ animationDelay: `${delay}s` }}
                    />
                  ))}
                </span>
              )}
            </div>
            <div className="max-h-48 overflow-y-auto p-3 space-y-1 font-mono text-xs">
              {logs.map((log, i) => (
                <div key={i} className="text-slate-300 leading-relaxed">
                  <span className="text-slate-500 select-none mr-2">{String(i + 1).padStart(2, '0')}</span>
                  {log}
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>
        )}

        {/* Error / Success */}
        {error && (
          <div className="mt-4 p-3 bg-red-900/60 text-red-200 rounded-lg text-sm border border-red-700">
            {error}
          </div>
        )}
        {success && (
          <div className="mt-4 p-3 bg-emerald-900/60 text-emerald-200 rounded-lg text-sm border border-emerald-700">
            {success}
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-3 mt-6">
          <Button
            onClick={() => { onClose(); resetState(); }}
            disabled={loading}
            className="flex-1 bg-slate-700 hover:bg-slate-600 text-white disabled:opacity-50"
          >
            {loading ? 'En cours…' : 'Annuler'}
          </Button>
          {!loading && !success && (
            <Button
              onClick={() => fileInputRef.current?.click()}
              className="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white"
            >
              Sélectionner
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
