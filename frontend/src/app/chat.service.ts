import { Injectable, signal, PLATFORM_ID, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Message } from './message.model';

type ServerEvent =
  | { type: 'token'; content: string }
  | { type: 'done' }
  | { type: 'error'; content: string };

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly platformId = inject(PLATFORM_ID);
  private socket: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectAttempts = 0;
  private intentionalClose = false;

  messages = signal<Message[]>([]);
  isStreaming = signal(false);
  connectionStatus = signal<'connecting' | 'online' | 'offline'>('connecting');

  private get wsUrl(): string {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${window.location.hostname}:8000/chat`;
  }

  connect(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    this.intentionalClose = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this.connectionStatus.set('connecting');
    this.socket = new WebSocket(this.wsUrl);

    this.socket.onopen = () => {
      this.connectionStatus.set('online');
      this.reconnectAttempts = 0;
    };

    this.socket.onclose = () => {
      this.connectionStatus.set('offline');
      if (this.isStreaming()) this.finishStreaming();
      if (!this.intentionalClose) this.scheduleReconnect();
    };

    this.socket.onerror = () => {
      this.connectionStatus.set('offline');
    };

    this.socket.onmessage = (event) => {
      const data: ServerEvent = JSON.parse(event.data);

      if (data.type === 'token') {
        this.appendToLastMessage(data.content);
      } else if (data.type === 'done') {
        this.finishStreaming();
      } else if (data.type === 'error') {
        this.appendToLastMessage(`\n\n[error] ${data.content}`);
        this.finishStreaming();
      }
    };
  }

  sendQuestion(question: string): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;

    const history = this.messages().map(({ role, content }) => ({ role, content }));

    this.messages.update((msgs) => [
      ...msgs,
      { role: 'user', content: question, timestamp: Date.now() },
      { role: 'assistant', content: '', streaming: true, timestamp: Date.now() },
    ]);

    this.isStreaming.set(true);
    this.socket.send(JSON.stringify({ question, history }));
  }

  private appendToLastMessage(token: string): void {
    this.messages.update((msgs) => {
      const updated = [...msgs];
      const last = updated[updated.length - 1];
      updated[updated.length - 1] = { ...last, content: last.content + token };
      return updated;
    });
  }

  private finishStreaming(): void {
    this.isStreaming.set(false);
    this.messages.update((msgs) => {
      const updated = [...msgs];
      const last = updated[updated.length - 1];
      updated[updated.length - 1] = { ...last, streaming: false };
      return updated;
    });
  }

  private scheduleReconnect(): void {
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30_000);
    this.reconnectAttempts++;
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }

  disconnect(): void {
    this.intentionalClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.socket?.close();
  }
}
