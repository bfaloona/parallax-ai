export interface User {
  id: string
  email: string
  tier: string
  is_active: boolean
  created_at: string
}

export interface Conversation {
  id: string
  title: string
  current_mode: string
  current_model: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[]
}

export type Mode = 'balanced' | 'creative' | 'precise' | 'technical' | 'research' | 'audit' | 'domain_expert'
export type Model = 'haiku' | 'sonnet' | 'opus'

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterRequest {
  email: string
  password: string
}

export interface LoginRequest {
  username: string  // Note: backend uses 'username' field for email
  password: string
}
