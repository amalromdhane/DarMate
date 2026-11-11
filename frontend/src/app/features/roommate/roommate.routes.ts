import { Routes } from '@angular/router';

export const ROOMMATE_ROUTES: Routes = [
  { path: '', pathMatch: 'full',
    loadComponent: () => import('./pages/browse/browse.component').then(m => m.BrowseComponent) },
  { path: 'me',
    loadComponent: () => import('./pages/my-search/my-search.component').then(m => m.MySearchComponent) },
  { path: 'requests',
    loadComponent: () => import('./pages/requests/requests.component').then(m => m.RequestsComponent) },
];