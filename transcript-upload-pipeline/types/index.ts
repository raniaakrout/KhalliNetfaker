/**
 * Global TypeScript Types for KhalliNetfaker Frontend
 */

export interface User {
  user_id: string;
  username: string;
  email: string;
  created_at?: string;
}

export interface Transcript {
  transcript_id: string;
  user_id: string;
  filename: string;
  file_hash: string;
  file_path?: string;
  vectorstore_path?: string;
  status: 'processing' | 'completed' | 'failed';
  created_at: string;
}

export interface ActionItem {
  task: string;
  owner: string | null;
  deadline: string | null;
}

export interface MeetingMinutes {
  id?: string;
  transcript_id?: string;
  summary: string;
  key_decisions: string[];
  action_items: ActionItem[];
  sentiment: string;
  created_at?: string;
}

export interface ChatMessage {
  id: string;
  transcript_id?: string;
  user_id: string;
  role: 'user' | 'assistant';
  message: string;
  created_at: string;
}

export interface Chat {
  id: string;
  transcript_id: string;
  title: string;
  subtitle: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
  }>;
  created_at: Date;
  updated_at?: Date;
}

export interface AuthResponse {
  access_token: string;
  token_type?: string;
}

export interface UploadResponse {
  transcript_id: string;
  filename: string;
  minutes: MeetingMinutes;
}

export interface ChatResponse {
  answer: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface PaginationParams {
  skip: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}
