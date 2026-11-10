// import { Routes } from '@angular/router';
// import { adminGuard, authGuard, guestGuard  } from './core/guards';

// export const routes: Routes = [
//   { path: '', pathMatch: 'full', redirectTo: 'properties' },
//   { path: 'auth', canActivate: [guestGuard], loadChildren: () => import('./features/auth/auth.routes').then(m => m.AUTH_ROUTES) },
//   { path: 'properties', loadChildren: () => import('./features/properties/properties.routes').then(m => m.PROPERTY_ROUTES) },
//   { path: 'favorites', canActivate: [authGuard ], loadChildren: () => import('./features/favorites/favorites.routes').then(m => m.FAVORITE_ROUTES) },
//   { path: 'rental-requests', canActivate: [authGuard], loadChildren: () => import('./features/rental-requests/rental-requests.routes').then(m => m.RENTAL_ROUTES) },
//   { path: 'messages', canActivate: [authGuard], loadChildren: () => import('./features/messaging/messaging.routes').then(m => m.MESSAGING_ROUTES) },
//   { path: 'notifications', canActivate: [authGuard], loadChildren: () => import('./features/notifications/notifications.routes').then(m => m.NOTIFICATION_ROUTES) },
//   { path: 'admin', canActivate: [authGuard, adminGuard], loadChildren: () => import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES) },
//   {path: 'profile',canActivate: [authGuard],loadChildren: () =>import('./features/profile/profile.routes').then(m => m.PROFILE_ROUTES)},
//   { path: '**', redirectTo: 'properties' }

// ];

import { Routes } from '@angular/router';
import { adminGuard, authGuard, guestGuard, roleGuard } from './core/guards';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'properties' },
  { path: 'auth', canActivate: [guestGuard], loadChildren: () => import('./features/auth/auth.routes').then(m => m.AUTH_ROUTES) },
  { path: 'properties', loadChildren: () => import('./features/properties/properties.routes').then(m => m.PROPERTY_ROUTES) },

  // Chercheur uniquement
  { path: 'favorites', canActivate: [authGuard, roleGuard('SEEKER')], loadChildren: () => import('./features/favorites/favorites.routes').then(m => m.FAVORITE_ROUTES) },

  // Communs aux deux rôles (l'écran s'adapte au rôle)
  { path: 'rental-requests',  canActivate: [authGuard, roleGuard('SEEKER', 'OWNER')], loadChildren: () => import('./features/rental-requests/rental-requests.routes').then(m => m.RENTAL_ROUTES) },
  { path: 'messages', canActivate: [authGuard], loadChildren: () => import('./features/messaging/messaging.routes').then(m => m.MESSAGING_ROUTES) },
  { path: 'notifications', canActivate: [authGuard], loadChildren: () => import('./features/notifications/notifications.routes').then(m => m.NOTIFICATION_ROUTES) },
  { path: 'profile', canActivate: [authGuard], loadChildren: () => import('./features/profile/profile.routes').then(m => m.PROFILE_ROUTES) },

  { path: 'admin', canActivate: [authGuard, adminGuard], loadChildren: () => import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES) },
  { path: '**', redirectTo: 'properties' },
];