import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { toParams } from './http-params';
import { Ref } from '../models';
@Injectable({ providedIn: 'root' })
export class ReferenceService {
  private http = inject(HttpClient); private u = `${environment.apiUrl}/reference`;
  regions(): Observable<Ref[]> { return this.http.get<Ref[]>(`${this.u}/regions`); }
  cities(region_id?: number): Observable<Ref[]> { return this.http.get<Ref[]>(`${this.u}/cities`, { params: toParams({ region_id }) }); }
  categories(): Observable<Ref[]> { return this.http.get<Ref[]>(`${this.u}/categories`); }
}
