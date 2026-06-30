import {
  Component, ElementRef, ViewChild, inject, effect, OnDestroy, PLATFORM_ID,
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ChatService } from '../chat.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css',
})
export class ChatComponent implements OnDestroy {
  @ViewChild('scrollAnchor') private scrollAnchor!: ElementRef;

  readonly chat = inject(ChatService);
  private readonly sanitizer = inject(DomSanitizer);
  private readonly platformId = inject(PLATFORM_ID);
  private readonly mdCache = new Map<string, SafeHtml>();

  draft = '';

  readonly suggestions = [
    'What are the PX4 flight modes?',
    'How do I calibrate the ESCs?',
    'Explain PID tuning for multirotors',
    'What does the SYS_AUTOSTART parameter do?',
  ];

  constructor() {
    this.chat.connect();

    effect(() => {
      this.chat.messages(); // track signal
      if (isPlatformBrowser(this.platformId)) {
        requestAnimationFrame(() =>
          this.scrollAnchor?.nativeElement?.scrollIntoView({ behavior: 'smooth' })
        );
      }
    });
  }

  ngOnDestroy(): void {
    this.chat.disconnect();
  }

  send(): void {
    const q = this.draft.trim();
    if (!q || this.chat.isStreaming()) return;
    this.chat.sendQuestion(q);
    this.draft = '';
  }

  ask(question: string): void {
    if (this.chat.isStreaming()) return;
    this.chat.sendQuestion(question);
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  autoResize(el: HTMLTextAreaElement): void {
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  renderMarkdown(content: string): SafeHtml {
    if (this.mdCache.has(content)) return this.mdCache.get(content)!;
    const html = this.sanitizer.bypassSecurityTrustHtml(this.toHtml(content));
    this.mdCache.set(content, html);
    return html;
  }

  private toHtml(md: string): string {
    const blocks: string[] = [];

    const text = md.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
      const i = blocks.length;
      blocks.push(
        `<pre><code${lang ? ` class="lang-${lang}"` : ''}>${this.esc(code.trim())}</code></pre>`
      );
      return `\x02BLOCK${i}\x03`;
    });

    const output = text.split(/\n\n+/).map(seg => {
      seg = seg.trim();
      if (!seg) return '';

      if (/^\x02BLOCK\d+\x03$/.test(seg)) return seg;

      if (seg.startsWith('### ')) return `<h3>${this.inl(seg.slice(4))}</h3>`;
      if (seg.startsWith('## '))  return `<h2>${this.inl(seg.slice(3))}</h2>`;
      if (seg.startsWith('# '))   return `<h1>${this.inl(seg.slice(2))}</h1>`;

      if (/^-{3,}$/.test(seg)) return '<hr>';

      if (/^[*-] /m.test(seg)) {
        const items = seg.split('\n')
          .map(l => l.replace(/^[*-] /, '').trim())
          .filter(Boolean)
          .map(l => `<li>${this.inl(l)}</li>`)
          .join('');
        return `<ul>${items}</ul>`;
      }

      if (/^\d+\. /m.test(seg)) {
        const items = seg.split('\n')
          .map(l => l.replace(/^\d+\. /, '').trim())
          .filter(Boolean)
          .map(l => `<li>${this.inl(l)}</li>`)
          .join('');
        return `<ol>${items}</ol>`;
      }

      return `<p>${this.inl(seg.replace(/\n/g, '<br>'))}</p>`;
    }).join('');

    return blocks.reduce((s, b, i) => s.split(`\x02BLOCK${i}\x03`).join(b), output);
  }

  private inl(s: string): string {
    s = s.replace(/`([^`]+)`/g, (_, c) => `<code>${this.esc(c)}</code>`);
    s = s.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/\*(.+?)\*/g, '<em>$1</em>');
    return s;
  }

  private esc(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}
