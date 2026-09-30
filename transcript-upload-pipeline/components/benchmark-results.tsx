'use client';

import { BenchmarkResult, BenchmarkResponse } from '@/lib/benchmark-types';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface BenchmarkResultsProps {
  results: BenchmarkResponse | null;
  onClose: () => void;
}

export function BenchmarkResults({ results, onClose }: BenchmarkResultsProps) {
  const [expandedResult, setExpandedResult] = useState<string | null>(null);

  if (!results) return null;

  const sortedResults = [...results.results].sort(
    (a, b) => (b.metrics.score_global || 0) - (a.metrics.score_global || 0)
  );

  const formatMetric = (value: number | null) => {
    if (value === null) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };

  const getMetricColor = (value: number | null) => {
    if (value === null) return 'text-slate-500';
    if (value >= 0.7) return 'text-green-400';
    if (value >= 0.5) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-6 max-w-6xl w-full max-h-[90vh] overflow-y-auto border border-slate-600">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-bold text-white">Benchmark Results</h2>
            <p className="text-sm text-slate-400 mt-1">
              Run ID: {results.run_id} • Duration: {(results.duration_total_ms / 1000).toFixed(2)}s
            </p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-2xl">
            ×
          </button>
        </div>

        <div className="mb-4 bg-cyan-900/30 border border-cyan-600 rounded-lg p-4">
          <p className="text-cyan-300 text-sm">
            <strong>Question:</strong> {results.question}
          </p>
          {results.best_config && (
            <p className="text-green-400 text-sm mt-2">
              <strong>Best Config:</strong> {results.best_config}
            </p>
          )}
        </div>

        <div className="space-y-3">
          {sortedResults.map((result, idx) => (
            <div key={result.config_id} className="bg-slate-700 rounded-lg border border-slate-600">
              <div
                className="p-4 cursor-pointer hover:bg-slate-700/80"
                onClick={() =>
                  setExpandedResult(expandedResult === result.config_id ? null : result.config_id)
                }
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-white font-bold">#{idx + 1}</span>
                      <span className="text-cyan-400 font-mono text-sm">{result.config_id}</span>
                      {result.error && (
                        <span className="text-red-400 text-xs bg-red-900/30 px-2 py-1 rounded">
                          ERROR
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-6 gap-2 text-xs">
                      <div>
                        <p className="text-slate-400">Answer Relevancy</p>
                        <p className={`font-semibold ${getMetricColor(result.metrics.answer_relevancy)}`}>
                          {formatMetric(result.metrics.answer_relevancy)}
                        </p>
                      </div>
                      <div>
                        <p className="text-slate-400">Faithfulness</p>
                        <p className={`font-semibold ${getMetricColor(result.metrics.faithfulness)}`}>
                          {formatMetric(result.metrics.faithfulness)}
                        </p>
                      </div>
                      <div>
                        <p className="text-slate-400">Context Precision</p>
                        <p className={`font-semibold ${getMetricColor(result.metrics.contextual_precision)}`}>
                          {formatMetric(result.metrics.contextual_precision)}
                        </p>
                      </div>
                      <div>
                        <p className="text-slate-400">Context Recall</p>
                        <p className={`font-semibold ${getMetricColor(result.metrics.contextual_recall)}`}>
                          {formatMetric(result.metrics.contextual_recall)}
                        </p>
                      </div>
                      <div>
                        <p className="text-slate-400">Context Relevancy</p>
                        <p className={`font-semibold ${getMetricColor(result.metrics.contextual_relevancy)}`}>
                          {formatMetric(result.metrics.contextual_relevancy)}
                        </p>
                      </div>
                      <div>
                        <p className="text-slate-400">Global Score</p>
                        <p className={`font-bold text-base ${getMetricColor(result.metrics.score_global)}`}>
                          {formatMetric(result.metrics.score_global)}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-4 mt-2 text-xs text-slate-400">
                      <span>Latency: {result.latency_ms}ms</span>
                      <span>Chunks: {result.retrieved_chunks.length}</span>
                    </div>
                  </div>
                </div>
              </div>

              {expandedResult === result.config_id && (
                <div className="border-t border-slate-600 p-4 bg-slate-900/50">
                  {result.error ? (
                    <div className="text-red-400 text-sm">{result.error}</div>
                  ) : (
                    <div className="space-y-4">
                      <div>
                        <p className="text-slate-300 text-sm font-semibold mb-2">Answer:</p>
                        <div className="bg-slate-800 rounded p-3 text-slate-200 text-sm">
                          {result.answer}
                        </div>
                      </div>
                      <div>
                        <p className="text-slate-300 text-sm font-semibold mb-2">
                          Retrieved Chunks ({result.retrieved_chunks.length}):
                        </p>
                        <div className="space-y-2">
                          {result.retrieved_chunks.map((chunk, i) => (
                            <div key={i} className="bg-slate-800 rounded p-2 text-xs text-slate-300">
                              <span className="text-cyan-400 font-mono">[{i + 1}]</span> {chunk}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="flex justify-end mt-6">
          <Button onClick={onClose} className="bg-slate-700 hover:bg-slate-600 text-white">
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
