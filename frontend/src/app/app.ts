import { Component } from '@angular/core';
import { ChatComponent } from './chat/chat.component';

@Component({
  selector: 'app-root',
  imports: [ChatComponent],
  template: '<app-chat></app-chat>',
})
export class App {}
