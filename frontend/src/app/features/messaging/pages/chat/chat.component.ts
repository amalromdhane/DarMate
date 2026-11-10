import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from '../../../../core/auth.service';
import { ChatMessage, Conversation } from '../../../../models';
import { MessagingService } from '../../services/messaging.service';
import { RealtimeService } from '../../services/realtime.service';
@Component({ selector: 'app-chat', standalone: true, imports: [ReactiveFormsModule], templateUrl: './chat.component.html', styleUrl: './chat.component.css' })
export class ChatComponent implements OnInit, OnDestroy {
  private svc = inject(MessagingService); private rt = inject(RealtimeService); private route = inject(ActivatedRoute); private router = inject(Router);
  me = inject(AuthService).user;
  conversations = signal<Conversation[]>([]); messages = signal<ChatMessage[]>([]); current = signal<number | null>(null);
  form = inject(FormBuilder).nonNullable.group({ body: ['', Validators.required] });
  private sub = new Subscription();
  ngOnInit(): void {
    this.rt.connect();
    this.sub.add(this.rt.events.subscribe(() => { this.refresh(); this.loadMessages(); }));
    this.sub.add(this.route.queryParamMap.subscribe(p => { const c = Number(p.get('c')) || null; this.current.set(c); this.loadMessages(); }));
    this.refresh();
  }
  ngOnDestroy(): void { this.sub.unsubscribe(); }
  refresh(): void { this.svc.list().subscribe(c => this.conversations.set(c)); }
  open(id: number): void { this.router.navigate([], { queryParams: { c: id } }); }
  private loadMessages(): void {
    const id = this.current(); if (!id) return;
    this.svc.messages(id).subscribe(m => { this.messages.set([...m].sort((a, b) => a.id - b.id)); this.svc.markRead(id).subscribe(); });
  }
  send(): void {
    const id = this.current(); if (!id || this.form.invalid) return;
    this.svc.send(id, this.form.getRawValue().body).subscribe(() => { this.form.reset(); this.loadMessages(); });
  }
  attach(e: Event): void {
    const id = this.current(), f = (e.target as HTMLInputElement).files?.[0];
    if (id && f) this.svc.attach(id, f).subscribe(() => this.loadMessages());
  }
  url(id: number): string { return this.svc.attachmentUrl(id); }
}
