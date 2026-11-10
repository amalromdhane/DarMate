import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from './auth.service';
import { ToastService } from './toast.service';

const withToken = (token: string | null) => (token ? { setHeaders: { Authorization: `Bearer ${token}` } } : {});

export const tokenInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const authCall = req.url.includes('/auth/');
  return next(req.clone({ ...withToken(auth.token), withCredentials: true })).pipe(
    catchError((e: HttpErrorResponse) => {
      if (e.status !== 401 || authCall) return throwError(() => e);
      return auth.refresh().pipe(switchMap(() => next(req.clone(withToken(auth.token)))));
    }),
  );
};

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const toast = inject(ToastService);
  return next(req).pipe(catchError((e: HttpErrorResponse) => {
    const d = e.error?.detail;
    toast.show(typeof d === 'string' ? d : Array.isArray(d) ? d[0]?.msg ?? 'Données invalides.' : `Erreur ${e.status}`, true);
    return throwError(() => e);
  }));
};
