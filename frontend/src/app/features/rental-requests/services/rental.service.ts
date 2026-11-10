import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { RentalRequest } from '../../../models';
@Injectable({ providedIn: 'root' })
export class RentalService {
  private http = inject(HttpClient); private u = `${environment.apiUrl}/rental-requests`;
  list(box: 'sent' | 'received', status?: string): Observable<RentalRequest[]> { return this.http.get<RentalRequest[]>(this.u, { params: toParams({ box, status }) }); }
  create(b: { property_id: number; message: string; desired_move_in: string | null; group_id: number | null }): Observable<RentalRequest> { return this.http.post<RentalRequest>(this.u, b); }
  setStatus(id: number, status: string): Observable<RentalRequest> { return this.http.patch<RentalRequest>(`${this.u}/${id}/status`, { status }); }
  confirm(id: number): Observable<RentalRequest> { return this.http.post<RentalRequest>(`${this.u}/${id}/confirm`, {}); }
}
