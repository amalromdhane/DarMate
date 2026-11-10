import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { RoommateMatch, RoommateProfile } from '../../../models';
@Injectable({ providedIn: 'root' })
export class RoommateService {
  private http = inject(HttpClient); private u = environment.apiUrl;
  mine(): Observable<RoommateProfile | null> { return this.http.get<RoommateProfile | null>(`${this.u}/roommates/me`); }
  save(b: Partial<RoommateProfile>): Observable<RoommateProfile> { return this.http.put<RoommateProfile>(`${this.u}/roommates/me`, b); }
  search(city_id?: number, min_score = 0): Observable<RoommateMatch[]> { return this.http.get<RoommateMatch[]>(`${this.u}/roommates`, { params: toParams({ city_id, min_score }) }); }
  compatibility(id: number): Observable<{ user_id: number; score: number }> { return this.http.get<{ user_id: number; score: number }>(`${this.u}/roommates/${id}/compatibility`); }
  requests(): Observable<{ id: number; message: string; status: string }[]> { return this.http.get<{ id: number; message: string; status: string }[]>(`${this.u}/roommate-requests`); }
  send(receiver_id: number, message: string): Observable<unknown> { return this.http.post(`${this.u}/roommate-requests`, { receiver_id, message }); }
  respond(id: number, accept: boolean): Observable<unknown> { return this.http.patch(`${this.u}/roommate-requests/${id}`, { accept }); }
}
