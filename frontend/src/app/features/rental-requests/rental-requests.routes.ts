import { Routes } from '@angular/router';
export const RENTAL_ROUTES: Routes = [{ path: '', loadComponent: () => import('./pages/rental-list/rental-list.component').then(m => m.RentalListComponent) }];
