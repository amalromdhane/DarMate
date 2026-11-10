import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { Msg, PropertyCard } from '../../../models';
@Injectable({ providedIn: 'root' })
export class FavoriteService {
  private http = inject(HttpClient); private u = `${environment.apiUrl}/favorites`;
  list(): Observable<PropertyCard[]> { return this.http.get<PropertyCard[]>(this.u); }
  add(id: number): Observable<Msg> { return this.http.put<Msg>(`${this.u}/${id}`, {}); }
  remove(id: number): Observable<Msg> { return this.http.delete<Msg>(`${this.u}/${id}`); }
}
