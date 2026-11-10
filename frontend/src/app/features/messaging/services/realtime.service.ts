import { Injectable, inject } from '@angular/core';
import { Subject } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { AuthService } from '../../../core/auth.service';

@Injectable({ providedIn: 'root' })
export class RealtimeService {
  private auth = inject(AuthService);
  readonly events = new Subject<{ type: string }>();
  private ws?: WebSocket; private timer?: ReturnType<typeof setInterval>; private stopped = true;

  connect(): void {
    if (this.ws) return;
    this.stopped = false;
    this.ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}${environment.wsPath}`);
    this.ws.onopen = () => this.ws?.send(JSON.stringify({ type: 'auth', token: this.auth.token }));
    this.ws.onmessage = (e: MessageEvent<string>) => {
      const d = JSON.parse(e.data) as { type: string };
      if (d.type === 'ready') this.timer = setInterval(() => this.ws?.send('{"type":"ping"}'), 25000);
      else if (d.type !== 'pong') this.events.next(d);
    };
    this.ws.onclose = () => { clearInterval(this.timer); this.ws = undefined; if (!this.stopped) setTimeout(() => this.connect(), 3000); };
  }
  disconnect(): void { this.stopped = true; this.ws?.close(); }
}
