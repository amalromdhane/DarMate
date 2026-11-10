import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { AdminUser, Page, Ref } from '../../../models';
@Injectable({ providedIn: 'root' })
export class AdminService {
  private http = inject(HttpClient); private u = `${environment.apiUrl}/admin`;
  users(q: string, page: number, status?: string): Observable<Page<AdminUser>> { return this.http.get<Page<AdminUser>>(`${this.u}/users`, { params: toParams({ q, page, status }) }); }
  setStatus(id: number, status: string): Observable<AdminUser> { return this.http.patch<AdminUser>(`${this.u}/users/${id}/status`, { status }); }
  stats(): Observable<Record<string, number>> { return this.http.get<Record<string, number>>(`${this.u}/stats`); }
  settings(): Observable<Record<string, string>> { return this.http.get<Record<string, string>>(`${this.u}/settings`); }
  saveSettings(b: Record<string, string>): Observable<Record<string, string>> { return this.http.put<Record<string, string>>(`${this.u}/settings`, b); }
  create(kind: 'regions' | 'cities' | 'categories', b: Partial<Ref>): Observable<Ref> { return this.http.post<Ref>(`${this.u}/${kind}`, b); }
  update(kind: 'regions' | 'cities' | 'categories', id: number, b: Partial<Ref>): Observable<Ref> { return this.http.put<Ref>(`${this.u}/${kind}/${id}`, b); }
  remove(kind: 'regions' | 'cities' | 'categories', id: number): Observable<void> { return this.http.delete<void>(`${this.u}/${kind}/${id}`); }
}
