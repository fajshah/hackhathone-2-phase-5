export interface User {
  id: number;
  email: string;
  firstName?: string;
  lastName?: string;
  createdAt: Date;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: Date;
  sequenceNumber: number;
}

export interface Conversation {
  id: number;
  title: string;
  description?: string;
  createdAt: Date;
  isActive: boolean;
  userId: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: any[];
  success: boolean;
}