import { Routes } from '@angular/router';
import { roleGuard } from '../../core/guards';
export const PROPERTY_ROUTES: Routes = [
  { path: '', pathMatch: 'full', loadComponent: () => import('./pages/property-list/property-list.component').then(m => m.PropertyListComponent) },
  { path: 'new', canActivate: [roleGuard('OWNER')], loadComponent: () => import('./pages/property-form/property-form.component').then(m => m.PropertyFormComponent) },
  { path: 'mine', canActivate: [roleGuard('OWNER')], loadComponent: () => import('./pages/my-properties/my-properties.component').then(m => m.MyPropertiesComponent) },
  { path: ':id/edit', canActivate: [roleGuard('OWNER')], loadComponent: () => import('./pages/property-form/property-form.component').then(m => m.PropertyFormComponent) },
  { path: ':id', loadComponent: () => import('./pages/property-detail/property-detail.component').then(m => m.PropertyDetailComponent) },
];




// import { Routes } from '@angular/router';
// import { authGuard, roleGuard } from '../../core/guards';

// export const PROPERTY_ROUTES: Routes = [


//   {
//     path: '',
//     pathMatch: 'full',
//     loadComponent: () =>
//       import('./pages/property-list/property-list.component')
//         .then(m => m.PropertyListComponent)
//   },


//   {
//     path: 'new',
//     canActivate: [authGuard, roleGuard('SEEKER')],
//     loadComponent: () =>
//       import('./pages/property-form/property-form.component')
//         .then(m => m.PropertyFormComponent)
//   },


//   {
//     path: 'mine',
//     canActivate: [authGuard, roleGuard('OWNER')],
//     loadComponent: () =>
//       import('./pages/my-properties/my-properties.component')
//         .then(m => m.MyPropertiesComponent)
//   },


//   {
//     path: ':id/edit',
//     canActivate: [authGuard, roleGuard('OWNER')],
//     loadComponent: () =>
//       import('./pages/property-form/property-form.component')
//         .then(m => m.PropertyFormComponent)
//   },

 
//   {
//     path: ':id',
//     loadComponent: () =>
//       import('./pages/property-detail/property-detail.component')
//         .then(m => m.PropertyDetailComponent)
//   }
// ];