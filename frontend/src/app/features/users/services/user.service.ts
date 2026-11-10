import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { Msg, ReviewList, User } from '../../../models';
@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient); private u = environment.apiUrl;
  me(): Observable<User> { return this.http.get<User>(`${this.u}/users/me`); }
  update(b: Partial<User>): Observable<User> { return this.http.put<User>(`${this.u}/users/me`, b); }
  changePassword(current_password: string, new_password: string): Observable<Msg> { return this.http.put<Msg>(`${this.u}/users/me/password`, { current_password, new_password }); }
  uploadIdentity(file: File, doc_type = 'ID_CARD'): Observable<{ id: number }> { const f = new FormData(); f.append('file', file); f.append('doc_type', doc_type); return this.http.post<{ id: number }>(`${this.u}/users/me/identity-documents`, f); }
  publicProfile(id: number): Observable<User> { return this.http.get<User>(`${this.u}/users/${id}/public-profile`); }
  reviews(id: number): Observable<ReviewList> { return this.http.get<ReviewList>(`${this.u}/users/${id}/reviews`); }
  block(id: number, on: boolean): Observable<Msg> { return on ? this.http.post<Msg>(`${this.u}/users/${id}/block`, {}) : this.http.delete<Msg>(`${this.u}/users/${id}/block`); }
  report(b: { reported_user_id: number; reason: string; details: string | null; message_id: number | null }): Observable<Msg> { return this.http.post<Msg>(`${this.u}/reports`, b); }
}
