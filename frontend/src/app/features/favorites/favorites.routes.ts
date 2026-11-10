import { Routes } from '@angular/router';
export const FAVORITE_ROUTES: Routes = [{ path: '', loadComponent: () => import('./pages/favorite-list/favorite-list.component').then(m => m.FavoriteListComponent) }];
