'use client';

import { useState, useEffect, useRef } from 'react';
import { BenchmarkRequest } from '@/lib/api';

interface BenchmarkProgressModalProps {
  isOpen: boolean;
  request: BenchmarkRequest | null;
  transcriptFilename?: string;
}

export function BenchmarkProgressModal({
  isOpen,
  request,
  transcriptFilename,
}: BenchmarkProgressModalProps) {
  const [secondsElapsed, setSecondsElapsed] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Timer effect
  useEffect(() => {
    if (!isOpen) {
      setSecondsElapsed(0);
      setLogs([]);
      return;
    }

    const timer = setInterval(() => {
      setSecondsElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [isOpen]);

  // Dynamic log generator based on elapsed time and config count
  useEffect(() => {
    if (!isOpen || !request) return;

    const totalConfigs = request.configs.length;
    const initialLogs = [
      `[00:01] 🚀 Benchmark session initialized.`,
      `[00:02] 📄 Target transcript: "${transcriptFilename || request.transcript_id}"`,
      `[00:02] ❓ Evaluation question: "${request.question.length > 60 ? request.question.slice(0, 60) + '...' : request.question}"`,
      `[00:03] ⚙️ Queued ${totalConfigs} configuration(s) for sequential evaluation.`,
    ];

    setLogs(initialLogs);

    const logTimers: NodeJS.Timeout[] = [];

    // Simulate progressive milestones every few seconds
    request.configs.forEach((cfg, idx) => {
      const startDelay = 4 + idx * 18;
      const evalDelay = startDelay + 8;
      const doneDelay = startDelay + 16;

      logTimers.push(
        setTimeout(() => {
          setLogs((prev) => [
            ...prev,
            `[${formatTime(startDelay)}] 🔄 Config ${idx + 1}/${totalConfigs} [${cfg.llm.split('/').pop()} | ${cfg.embedding_model.split('/').pop()} | ${cfg.chunking_strategy}]: Generating response...`,
          ]);
        }, startDelay * 1000)
      );

      logTimers.push(
        setTimeout(() => {
          setLogs((prev) => [
            ...prev,
            `[${formatTime(evalDelay)}] ⚖️ Config ${idx + 1}/${totalConfigs}: DeepEval Judge measuring Faithfulness, Precision & Relevancy...`,
          ]);
        }, evalDelay * 1000)
      );

      logTimers.push(
        setTimeout(() => {
          setLogs((prev) => [
            ...prev,
            `[${formatTime(doneDelay)}] ✅ Config ${idx + 1}/${totalConfigs}: Evaluation metrics successfully scored.`,
          ]);
        }, doneDelay * 1000)
      );
    });

    return () => {
      logTimers.forEach(clearTimeout);
    };
  }, [isOpen, request, transcriptFilename]);

  // Auto-scroll logs to bottom
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  if (!isOpen || !request) return null;

  function formatTime(totalSec: number) {
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  const totalConfigs = request.configs.length;
  // Estimate ~20-25 seconds per configuration
  const estSeconds = Math.max(30, totalConfigs * 22);
  const progressPercent = Math.min(95, Math.round((secondsElapsed / estSeconds) * 100));

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl max-w-2xl w-full p-6 text-white overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <span className="animate-spin text-lg">⚙️</span>
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-cyan-400 rounded-full animate-ping opacity-75"></span>
            </div>
            <div>
              <h3 className="font-bold text-base text-white flex items-center gap-2">
                Benchmarking Pipeline Active
              </h3>
              <p className="text-xs text-slate-400">
                Evaluating {totalConfigs} configuration{totalConfigs > 1 ? 's' : ''} with DeepEval Judge LLM
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-1.5 text-xs font-mono text-cyan-300">
            <span>⏱️</span>
            <span>{formatTime(secondsElapsed)}</span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="my-5 space-y-2">
          <div className="flex justify-between items-center text-xs text-slate-400">
            <span>Overall Evaluation Progress</span>
            <span className="font-mono text-cyan-400">{progressPercent}%</span>
          </div>
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 transition-all duration-500 rounded-full"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4 text-xs">
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
            <span className="text-slate-400 font-medium block mb-1">Transcript</span>
            <p className="font-semibold text-slate-200 truncate">
              {transcriptFilename || request.transcript_id}
            </p>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
            <span className="text-slate-400 font-medium block mb-1">Tested Question</span>
            <p className="font-semibold text-slate-200 truncate">
              {request.question}
            </p>
          </div>
        </div>

        {/* Live Terminal Log Stream */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Pipeline Logs
            </span>
            <span className="text-[11px] text-slate-500">Auto-scrolling</span>
          </div>
          <div className="h-44 bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 font-mono text-[11px] text-slate-300 overflow-y-auto space-y-1.5 shadow-inner">
            {logs.map((log, index) => (
              <div key={index} className="leading-relaxed flex items-start gap-1">
                <span className="text-slate-500 select-none">›</span>
                <span className={log.includes('✅') ? 'text-emerald-400' : log.includes('⚖️') ? 'text-amber-300' : 'text-slate-300'}>
                  {log}
                </span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center gap-1.5 text-slate-400">
            <span>💡</span> Configurations execute sequentially to guarantee DeepEval judge stability.
          </span>
          <span className="text-[11px] text-cyan-400 animate-pulse">
            Processing...
          </span>
        </div>
      </div>
    </div>
  );
}
