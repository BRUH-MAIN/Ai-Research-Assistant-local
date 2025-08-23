import axios from 'axios';
import type { Message } from '../types/types';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || 'v1';
const API_URL = `${API_BASE_URL}/api/${API_VERSION}`;

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Types matching backend models
export interface ChatRequest {
  id: string;
  sender: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

export interface ChatResponse {
  userMessage: Message;
  aiMessage: Message;
}

export interface SessionCreateResponse {
  session_id: string;
}

export interface SessionHistoryResponse {
  messages: Message[];
}

export interface SuccessResponse {
  message: string;
}

// API Service Class
class ApiService {
  // Health check endpoint
  async healthCheck(): Promise<boolean> {
    try {
      const response = await apiClient.get('/');
      return response.status === 200 && response.data.status === 'online';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  // Chat Session Management
  async createSession(): Promise<string> {
    try {
      const response = await apiClient.post<SessionCreateResponse>('/chat/sessions');
      return response.data.session_id;
    } catch (error) {
      console.error('Failed to create session:', error);
      throw new Error('Failed to create chat session');
    }
  }

  async getSessionHistory(sessionId: string): Promise<Message[]> {
    try {
      const response = await apiClient.get<SessionHistoryResponse>(`/chat/${sessionId}/history`);
      return response.data.messages || [];
    } catch (error) {
      console.error('Failed to get session history:', error);
      throw new Error('Failed to load chat history');
    }
  }

  async sendMessage(sessionId: string, message: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ChatResponse>(`/chat/${sessionId}`, message);
      return response.data;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw new Error('Failed to send message');
    }
  }

  async deleteSession(sessionId: string): Promise<boolean> {
    try {
      await apiClient.delete<SuccessResponse>(`/chat/${sessionId}`);
      return true;
    } catch (error) {
      console.error('Failed to delete session:', error);
      throw new Error('Failed to delete session');
    }
  }

  // Legacy endpoint for simple prompts
  async sendSimplePrompt(prompt: string): Promise<string> {
    try {
      const response = await apiClient.post('/chat', { prompt });
      return response.data.response;
    } catch (error) {
      console.error('Failed to send prompt:', error);
      throw new Error('Failed to process prompt');
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
