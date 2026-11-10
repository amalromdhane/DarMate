import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { toParams } from '../../../core/http-params';
import { Group, Invitation } from '../../../models';
@Injectable({ providedIn: 'root' })
export class GroupService {
  private http = inject(HttpClient); private u = environment.apiUrl;
  mine(): Observable<Group[]> { return this.http.get<Group[]>(`${this.u}/groups`); }
  create(name: string, max_members: number): Observable<Group> { return this.http.post<Group>(`${this.u}/groups`, { name, max_members }); }
  get(id: number): Observable<Group> { return this.http.get<Group>(`${this.u}/groups/${id}`); }
  remove(id: number): Observable<void> { return this.http.delete<void>(`${this.u}/groups/${id}`); }
  invite(id: number, invitee_id: number): Observable<Invitation> { return this.http.post<Invitation>(`${this.u}/groups/${id}/invitations`, { invitee_id }); }
  removeMember(g: number, u: number): Observable<void> { return this.http.delete<void>(`${this.u}/groups/${g}/members/${u}`); }
  invitations(): Observable<Invitation[]> { return this.http.get<Invitation[]>(`${this.u}/group-invitations`); }
  respond(id: number, accept: boolean): Observable<Invitation> { return this.http.patch<Invitation>(`${this.u}/group-invitations/${id}`, { accept }); }
}
