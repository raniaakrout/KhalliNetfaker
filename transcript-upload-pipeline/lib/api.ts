import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Required to send httpOnly cookies cross-origin (pairs with backend allow_credentials=True)
  withCredentials: true,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  username: string;
  email: string;
}

export interface UserResponse {
  user_id: string;
  username: string;
  email: string;
}

export interface ActionItem {
  task: string;
  owner: string | null;
  deadline: string | null;
}

export interface MeetingMinutes {
  summary: string;
  key_decisions: string[];
  action_items: ActionItem[];
  sentiment: string;
}

export interface UploadResponse {
  transcript_id: string;
  filename: string;
  minutes: MeetingMinutes;
}

export interface ChatRequest {
  transcript_id: string;
  message: string;
  thread_id: string;
}

export interface ChatResponse {
  answer: string;
  chunk_ids?: string[];
}

export interface Transcript {
  transcript_id: string;
  filename: string;
  created_at: string;
  status: string;
}

// Auth endpoints
export const authAPI = {
  register: (email: string, username: string, password: string) =>
    api.post<UserResponse>('/api/auth/register', {
      email,
      username,
      password,
    }),

  login: (email: string, password: string) =>
    api.post<AuthResponse>('/api/auth/login', {
      email,
      password,
    }),
};

// Transcript endpoints
export const transcriptAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<UploadResponse>('/api/transcripts', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getMinutes: (transcript_id: string) =>
    api.get<MeetingMinutes>(`/api/transcripts/${transcript_id}/minutes`),
  list: () =>
    api.get<Transcript[]>('/api/transcripts'),
};

// Chat endpoints
export const chatAPI = {
  send: (transcript_id: string, message: string, thread_id: string) =>
    api.post<ChatResponse>('/api/chat', {
      transcript_id,
      message,
      thread_id,
    }),
  list: () => api.get<any[]>('/api/chats'),
};

export interface MetricScore {
  name: string;
  score: number;
  reason: string;
  threshold: number;
  passed: boolean;
}

export interface EvalResult {
  transcript_id: string;
  pipeline: string;
  metrics: MetricScore[];
  evaluated_at: string;
}

// Evaluation endpoints
export const evaluationAPI = {
  evaluateSummary: (transcript_id: string, reference_summary?: string) =>
    api.post<EvalResult>('/api/evaluate/summary', {
      transcript_id,
      reference_summary: reference_summary?.trim() || undefined,
    }),

  evaluateRag: (
    transcript_id: string,
    question: string,
    answer: string,
    retrieved_chunks: string[],
    expected_answer?: string
  ) =>
    api.post<EvalResult>('/api/evaluate/rag', {
      transcript_id,
      question,
      answer,
      retrieved_chunks,
      expected_answer,
    }),
};

// Health check
export const healthAPI = {
  check: () => api.get('/api/health'),
};

// Benchmark types
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

// Benchmark endpoints
export const benchmarkAPI = {
  getConfigs: () => api.get<BenchmarkConfigsResponse>('/api/benchmark/configs'),
  run: (request: BenchmarkRequest) => api.post<BenchmarkResponse>('/api/benchmark/run', request),
};
