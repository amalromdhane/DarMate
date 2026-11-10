// import { inject } from '@angular/core';
// import { CanActivateFn, Router } from '@angular/router';
// import { AuthService } from './auth.service';
// export const authGuard: CanActivateFn = () => inject(AuthService).isLoggedIn() || inject(Router).createUrlTree(['/auth/login']);
// export const guestGuard: CanActivateFn = () => !inject(AuthService).isLoggedIn() || inject(Router).createUrlTree(['/']);
// export const adminGuard: CanActivateFn = () => inject(AuthService).isAdmin() || inject(Router).createUrlTree(['/']);
// // export const roleGuard = (...roles: string[]): CanActivateFn => () =>inject(AuthService).hasRole(...roles) || inject(Router).createUrlTree(['/']);


import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = () =>
  inject(AuthService).isLoggedIn() || inject(Router).createUrlTree(['/auth/login']);

export const guestGuard: CanActivateFn = () =>
  !inject(AuthService).isLoggedIn() || inject(Router).createUrlTree(['/']);

export const adminGuard: CanActivateFn = () =>
  inject(AuthService).isAdmin() || inject(Router).createUrlTree(['/']);

/** Accès réservé à un ou plusieurs rôles. Sinon : retour à l'accueil du rôle. */
export const roleGuard = (...roles: string[]): CanActivateFn => () => {
  const auth = inject(AuthService);
  return auth.hasRole(...roles) || inject(Router).createUrlTree([auth.homeUrl()]);
};