export interface Message {
  role: 'user' | 'assistant';
  content: string;
  section?: string;
  streaming?: boolean;
  timestamp: number;
}