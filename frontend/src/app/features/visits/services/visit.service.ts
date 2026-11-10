import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { Visit } from '../../../models';
@Injectable({ providedIn: 'root' })
export class VisitService {
  private http = inject(HttpClient); private u = `${environment.apiUrl}/visits`;
  request(b: { property_id: number; slots: { starts_at: string; ends_at: string }[]; note: string | null; rental_request_id: number | null }): Observable<Visit> { return this.http.post<Visit>(this.u, b); }
  calendar(start?: string, end?: string): Observable<Visit[]> { return this.http.get<Visit[]>(`${this.u}/calendar`, { params: toParams({ start, end }) }); }
  proposeSlots(id: number, slots: { starts_at: string; ends_at: string }[]): Observable<Visit> { return this.http.post<Visit>(`${this.u}/${id}/slots`, { slots }); }
  respond(id: number, action: string, slot_id?: number): Observable<Visit> { return this.http.patch<Visit>(`${this.u}/${id}`, { action, slot_id }); }
}
