import { HttpParams } from '@angular/common/http';
export function toParams(o: object): HttpParams {
  let p = new HttpParams();
  for (const [k, v] of Object.entries(o)) if (v !== '' && v !== null && v !== undefined) p = p.set(k, String(v));
  return p;
}
