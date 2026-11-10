import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { Review } from '../../../models';
@Injectable({ providedIn: 'root' })
export class ReviewService {
  private http = inject(HttpClient);
  create(b: { rental_request_id: number; target_type: string; rating: number; comment: string; reviewee_id: number | null }): Observable<Review> { return this.http.post<Review>(`${environment.apiUrl}/reviews`, b); }
}
