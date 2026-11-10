import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { Msg, Page, PropertyCard, PropertyDetail, PropertyFilters, PropertyPayload, ReviewList, SavedSearch, Img } from '../../../models';
@Injectable({ providedIn: 'root' })
export class PropertyService {
  private http = inject(HttpClient); private u = environment.apiUrl;
  search(f: PropertyFilters, page: number, size = 12): Observable<Page<PropertyCard>> { return this.http.get<Page<PropertyCard>>(`${this.u}/properties`, { params: toParams({ ...f, page, size }) }); }
  map(f: PropertyFilters): Observable<PropertyCard[]> { return this.http.get<PropertyCard[]>(`${this.u}/properties/map`, { params: toParams(f) }); }
  mine(page = 1): Observable<Page<PropertyCard>> { return this.http.get<Page<PropertyCard>>(`${this.u}/properties/mine`, { params: toParams({ page }) }); }
  get(id: number): Observable<PropertyDetail> { return this.http.get<PropertyDetail>(`${this.u}/properties/${id}`); }
  create(b: PropertyPayload): Observable<PropertyDetail> { return this.http.post<PropertyDetail>(`${this.u}/properties`, b); }
  update(id: number, b: Partial<PropertyPayload>): Observable<PropertyDetail> { return this.http.put<PropertyDetail>(`${this.u}/properties/${id}`, b); }
  setStatus(id: number, status: string): Observable<PropertyDetail> { return this.http.patch<PropertyDetail>(`${this.u}/properties/${id}/status`, { status }); }
  remove(id: number): Observable<void> { return this.http.delete<void>(`${this.u}/properties/${id}`); }
  addImage(id: number, file: File): Observable<Img> { const f = new FormData(); f.append('file', file); return this.http.post<Img>(`${this.u}/properties/${id}/images`, f); }
  removeImage(id: number, imageId: number): Observable<void> { return this.http.delete<void>(`${this.u}/properties/${id}/images/${imageId}`); }
  stats(id: number): Observable<Record<string, number>> { return this.http.get<Record<string, number>>(`${this.u}/properties/${id}/stats`); }
  reviews(id: number): Observable<ReviewList> { return this.http.get<ReviewList>(`${this.u}/properties/${id}/reviews`); }
  savedSearches(): Observable<SavedSearch[]> { return this.http.get<SavedSearch[]>(`${this.u}/saved-searches`); }
  saveSearch(name: string, filters: PropertyFilters, alert: boolean): Observable<SavedSearch> { return this.http.post<SavedSearch>(`${this.u}/saved-searches`, { name, filters, alert }); }
  deleteSearch(id: number): Observable<void> { return this.http.delete<void>(`${this.u}/saved-searches/${id}`); }
  setAlert(id: number, active: boolean): Observable<Msg> { return this.http.put<Msg>(`${this.u}/saved-searches/${id}/alert`, { active }); }
}
