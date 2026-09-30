'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  BenchmarkRunConfig,
  BenchmarkConfigsResponse,
  BenchmarkConfigOption,
} from '@/lib/benchmark-types';
import { benchmarkAPI, transcriptAPI, Transcript } from '@/lib/api';

interface BenchmarkModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRunBenchmark: (request: {
    transcript_id: string;
    question: string;
    ground_truth?: string;
    configs: BenchmarkRunConfig[];
  }) => void;
}

export function BenchmarkModal({ isOpen, onClose, onRunBenchmark }: BenchmarkModalProps) {
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [configs, setConfigs] = useState<BenchmarkConfigsResponse | null>(null);
  const [selectedTranscript, setSelectedTranscript] = useState('');
  const [question, setQuestion] = useState('');
  const [groundTruth, setGroundTruth] = useState('');
  const [selectedLLMs, setSelectedLLMs] = useState<string[]>([]);
  const [selectedEmbeddings, setSelectedEmbeddings] = useState<string[]>([]);
  const [selectedChunking, setSelectedChunking] = useState<string[]>([]);
  const [topK, setTopK] = useState(4);
  const [loading, setLoading] = useState(false);

  // Load transcripts and configs on mount
  useEffect(() => {
    if (isOpen) {
      transcriptAPI.list().then((res) => setTranscripts(res.data));
      benchmarkAPI.getConfigs().then((res) => {
        setConfigs(res.data);
        setTopK(res.data.top_k.default);
      });
    }
  }, [isOpen]);

  const toggleSelection = (
    id: string,
    selected: string[],
    setSelected: (val: string[]) => void
  ) => {
    if (selected.includes(id)) {
      setSelected(selected.filter((s) => s !== id));
    } else {
      setSelected([...selected, id]);
    }
  };

  const handleRun = () => {
    if (!selectedTranscript || !question || selectedLLMs.length === 0 ||
        selectedEmbeddings.length === 0 || selectedChunking.length === 0) {
      alert('Please fill all required fields and select at least one of each configuration.');
      return;
    }

    // Build all combinations
    const allConfigs: BenchmarkRunConfig[] = [];
    for (const llm of selectedLLMs) {
      for (const emb of selectedEmbeddings) {
        for (const chunk of selectedChunking) {
          allConfigs.push({
            llm,
            embedding_model: emb,
            chunking_strategy: chunk,
            top_k: topK,
          });
        }
      }
    }

    onRunBenchmark({
      transcript_id: selectedTranscript,
      question,
      ground_truth: groundTruth || undefined,
      configs: allConfigs,
    });

    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-slate-600">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white">🔬 Benchmarking Configuration</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-2xl">
            ×
          </button>
        </div>

        <div className="space-y-6">
          {/* Transcript Selection */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Transcript *
            </label>
            <select
              value={selectedTranscript}
              onChange={(e) => setSelectedTranscript(e.target.value)}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg p-2"
            >
              <option value="">Select a transcript...</option>
              {transcripts.map((t) => (
                <option key={t.transcript_id} value={t.transcript_id}>
                  {t.filename}
                </option>
              ))}
            </select>
          </div>

          {/* Question */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">Question *</label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your question..."
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg p-3 min-h-[80px]"
            />
          </div>

          {/* Ground Truth (Optional) */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Ground Truth (optional)
            </label>
            <textarea
              value={groundTruth}
              onChange={(e) => setGroundTruth(e.target.value)}
              placeholder="Expected answer for ContextualRecall metric..."
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg p-3 min-h-[60px]"
            />
          </div>

          {/* LLMs */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">LLMs *</label>
            <div className="grid grid-cols-3 gap-2">
              {configs?.llms.map((llm) => (
                <button
                  key={llm.id}
                  onClick={() => toggleSelection(llm.id, selectedLLMs, setSelectedLLMs)}
                  className={`p-3 rounded-lg border text-sm ${
                    selectedLLMs.includes(llm.id)
                      ? 'bg-cyan-600 border-cyan-500 text-white'
                      : 'bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  {llm.label}
                </button>
              ))}
            </div>
          </div>

          {/* Embeddings */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Embedding Models *
            </label>
            <div className="grid grid-cols-2 gap-2">
              {configs?.embedding_models.map((emb) => (
                <button
                  key={emb.id}
                  onClick={() => toggleSelection(emb.id, selectedEmbeddings, setSelectedEmbeddings)}
                  className={`p-3 rounded-lg border text-sm ${
                    selectedEmbeddings.includes(emb.id)
                      ? 'bg-cyan-600 border-cyan-500 text-white'
                      : 'bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  {emb.label}
                </button>
              ))}
            </div>
          </div>

          {/* Chunking Strategies */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Chunking Strategies *
            </label>
            <div className="space-y-3">
              {configs &&
                ['Semantic', 'Recursive', 'Token'].map((group) => (
                  <div key={group}>
                    <p className="text-xs text-slate-400 mb-2">{group}</p>
                    <div className="grid grid-cols-4 gap-2">
                      {configs.chunking_strategies
                        .filter((c) => c.group === group)
                        .map((chunk) => (
                          <button
                            key={chunk.id}
                            onClick={() =>
                              toggleSelection(chunk.id, selectedChunking, setSelectedChunking)
                            }
                            className={`p-2 rounded-lg border text-xs ${
                              selectedChunking.includes(chunk.id)
                                ? 'bg-cyan-600 border-cyan-500 text-white'
                                : 'bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600'
                            }`}
                          >
                            {chunk.label}
                          </button>
                        ))}
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Top K */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Top K Retrieval: {topK}
            </label>
            <input
              type="range"
              min={configs?.top_k.min || 1}
              max={configs?.top_k.max || 20}
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Summary */}
          <div className="bg-slate-700/50 rounded-lg p-4">
            <p className="text-slate-300 text-sm">
              <strong>Total configurations:</strong>{' '}
              {selectedLLMs.length * selectedEmbeddings.length * selectedChunking.length}
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end">
            <Button onClick={onClose} className="bg-slate-700 hover:bg-slate-600 text-white">
              Cancel
            </Button>
            <Button
              onClick={handleRun}
              disabled={loading}
              className="bg-cyan-600 hover:bg-cyan-500 text-white"
            >
              {loading ? 'Running...' : 'Run Benchmark'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
