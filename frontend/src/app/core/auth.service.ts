import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, of, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { Msg, TokenOut, User } from '../models';

@Injectable({ providedIn: 'root' })
export class AuthService {

//   hasRole(...roles: string[]): boolean {
//   const mine = this.user()?.roles ?? [];
//   return roles.some(r => mine.includes(r));
// }

  private http = inject(HttpClient);
  private router = inject(Router);
  private base = `${environment.apiUrl}/auth`;
  private _token = signal<string | null>(null);
  readonly user = signal<User | null>(null);
  readonly isLoggedIn = computed(() => !!this.user());
  readonly isAdmin = computed(() => this.user()?.roles?.includes('ADMIN') ?? false);
  // readonly isOwner  = computed(() => this.hasRole('OWNER'));
  // readonly isSeeker = computed(() => this.hasRole('SEEKER'));
  get token(): string | null { return this._token(); }

  private store = (r: TokenOut) => { this._token.set(r.access_token); this.user.set(r.user); };
  login(email: string, password: string): Observable<TokenOut> {
    return this.http.post<TokenOut>(`${this.base}/login`, { email, password }, { withCredentials: true }).pipe(tap(this.store));
  }
  register(body: Record<string, unknown>): Observable<User> { return this.http.post<User>(`${this.base}/register`, body); }
  refresh(): Observable<TokenOut> { return this.http.post<TokenOut>(`${this.base}/refresh`, {}, { withCredentials: true }).pipe(tap(this.store)); }
  restore(): Observable<TokenOut | null> { return this.refresh().pipe(catchError(() => of(null))); }
  forgot(email: string): Observable<Msg> { return this.http.post<Msg>(`${this.base}/forgot-password`, { email }); }
  reset(token: string, new_password: string): Observable<Msg> { return this.http.post<Msg>(`${this.base}/reset-password`, { token, new_password }); }
  logout(): void {
    this.http.post(`${this.base}/logout`, {}, { withCredentials: true }).pipe(catchError(() => of(null))).subscribe(() => {
      this._token.set(null); this.user.set(null); this.router.navigate(['/auth/login']);
    });
  }
}
