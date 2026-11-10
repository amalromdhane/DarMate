import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface UserProfile {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
}

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private http = inject(HttpClient);
  private url = '/api/users/me';

  get()                     { return this.http.get<UserProfile>(this.url); }
  update(data: UserProfile) { return this.http.put<UserProfile>(this.url, data); }
  changePassword(data: { currentPassword: string; newPassword: string }) {
    return this.http.put<void>(`${this.url}/password`, data);
  }
  deleteAccount()           { return this.http.delete<void>(this.url); }
}