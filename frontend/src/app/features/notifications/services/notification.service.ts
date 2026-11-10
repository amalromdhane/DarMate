// import { HttpClient } from '@angular/common/http';
// import { Injectable, inject } from '@angular/core';
// import { Observable } from 'rxjs';
// import { environment } from '../../../../environments/environment';
// import { toParams } from '../../../core/http-params';
// import { Msg, NotificationList } from '../../../models';
// @Injectable({ providedIn: 'root' })
// export class NotificationService {
//   private http = inject(HttpClient); private u = `${environment.apiUrl}/notifications`;
//   list(unread_only = false): Observable<NotificationList> { return this.http.get<NotificationList>(this.u, { params: toParams({ unread_only }) }); }
//   readAll(): Observable<Msg> { return this.http.patch<Msg>(`${this.u}/read-all`, {}); }
//   read(id: number): Observable<Msg> { return this.http.patch<Msg>(`${this.u}/${id}/read`, {}); }
// }
import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal, computed } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { Msg, NotificationList } from '../../../models';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private http = inject(HttpClient);
  private u = `${environment.apiUrl}/notifications`;

  readonly unreadCount = signal<number>(0);
  readonly hasUnread   = computed(() => this.unreadCount() > 0);

  private pollTimer?: ReturnType<typeof setInterval>;

  list(unread_only = false): Observable<NotificationList> {
    return this.http.get<NotificationList>(this.u, { params: toParams({ unread_only }) })
      .pipe(tap(res => {
        // NotificationList has no `unread` field, so derive it from items length
        // when we asked for unread-only results.
        if (unread_only) {
          this.unreadCount.set((res as any)?.items?.length ?? 0);
        }
      }));
  }

  readAll(): Observable<Msg> {
    return this.http.patch<Msg>(`${this.u}/read-all`, {})
      .pipe(tap(() => this.unreadCount.set(0)));
  }

  read(id: number): Observable<Msg> {
    return this.http.patch<Msg>(`${this.u}/${id}/read`, {})
      .pipe(tap(() => this.unreadCount.update(n => Math.max(0, n - 1))));
  }

  refreshUnread(): void {
    this.list(true).subscribe({ error: () => {} });
  }

  startPolling(intervalMs = 30_000): void {
    this.stopPolling();
    this.refreshUnread();
    this.pollTimer = setInterval(() => this.refreshUnread(), intervalMs);
  }

  stopPolling(): void {
    if (this.pollTimer) clearInterval(this.pollTimer);
    this.pollTimer = undefined;
  }

  onNewNotification(): void {
    this.unreadCount.update(n => n + 1);
  }

  reset(): void {
    this.stopPolling();
    this.unreadCount.set(0);
  }
}