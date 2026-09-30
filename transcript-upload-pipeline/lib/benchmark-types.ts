// Types for benchmark API

export interface BenchmarkRunConfig {
  llm: string;
  embedding_model: string;
  chunking_strategy: string;
  top_k: number;
}

export interface BenchmarkRequest {
  transcript_id: string;
  question: string;
  ground_truth?: string;
  configs: BenchmarkRunConfig[];
}

export interface BenchmarkMetrics {
  answer_relevancy: number | null;
  faithfulness: number | null;
  contextual_precision: number | null;
  contextual_recall: number | null;
  contextual_relevancy: number | null;
  score_global: number | null;
}

export interface BenchmarkResult {
  config_id: string;
  llm: string;
  embedding_model: string;
  chunking_strategy: string;
  top_k: number;
  answer: string;
  retrieved_chunks: string[];
  latency_ms: number;
  metrics: BenchmarkMetrics;
  error: string | null;
}

export interface BenchmarkResponse {
  run_id: string;
  transcript_id: string;
  question: string;
  results: BenchmarkResult[];
  best_config: string | null;
  duration_total_ms: number;
}

export interface BenchmarkConfigOption {
  id: string;
  label: string;
  group?: string;
  chunk_size?: number;
  overlap?: number;
}

export interface BenchmarkConfigsResponse {
  llms: Array<{ id: string; label: string; provider: string }>;
  embedding_models: Array<{ id: string; label: string }>;
  chunking_strategies: BenchmarkConfigOption[];
  top_k: { min: number; max: number; default: number };
}
