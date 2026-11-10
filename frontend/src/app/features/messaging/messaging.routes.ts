import { Routes } from '@angular/router';
export const MESSAGING_ROUTES: Routes = [{ path: '', loadComponent: () => import('./pages/chat/chat.component').then(m => m.ChatComponent) }];
