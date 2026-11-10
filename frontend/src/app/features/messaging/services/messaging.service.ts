import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { ChatMessage, Conversation } from '../../../models';
@Injectable({ providedIn: 'root' })
export class MessagingService {
  private http = inject(HttpClient); private u = `${environment.apiUrl}/conversations`;
  list(): Observable<Conversation[]> { return this.http.get<Conversation[]>(this.u); }
  open(user_id: number): Observable<{ id: number }> { return this.http.post<{ id: number }>(this.u, { user_id }); }
  messages(id: number, before_id?: number): Observable<ChatMessage[]> { return this.http.get<ChatMessage[]>(`${this.u}/${id}/messages`, { params: toParams({ before_id }) }); }
  send(id: number, body: string, property_id: number | null = null): Observable<ChatMessage> { return this.http.post<ChatMessage>(`${this.u}/${id}/messages`, { body, property_id }); }
  attach(id: number, file: File): Observable<ChatMessage> { const f = new FormData(); f.append('file', file); return this.http.post<ChatMessage>(`${this.u}/${id}/attachments`, f); }
  markRead(id: number): Observable<void> { return this.http.patch<void>(`${this.u}/${id}/read`, {}); }
  attachmentUrl(id: number): string { return `${environment.apiUrl}/attachments/${id}`; }
}
