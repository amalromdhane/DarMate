import { Injectable, signal } from '@angular/core';
@Injectable({ providedIn: 'root' })
export class ToastService {
  readonly message = signal<{ text: string; error: boolean } | null>(null);
  show(text: string, error = false): void { this.message.set({ text, error }); setTimeout(() => this.message.set(null), 4000); }
}
