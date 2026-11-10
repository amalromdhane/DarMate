// import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
// import { RouterLink, RouterLinkActive } from '@angular/router';
// import { AuthService } from '../../core/auth.service';
// import { NotificationService } from '../../features/notifications/services/notification.service';

// @Component({
//   selector: 'app-header',
//   standalone: true,
//   imports: [RouterLink, RouterLinkActive],
//   templateUrl: './header.component.html',
//   styleUrl: './header.component.css'
// })
// export class HeaderComponent implements OnInit, OnDestroy {
//   auth  = inject(AuthService);
//   notif = inject(NotificationService);

//   mobileOpen  = signal(false);
//   unreadCount = this.notif.unreadCount;
//   hasUnread   = this.notif.hasUnread;

//   toggleMobile() { this.mobileOpen.update(v => !v); }
//   closeMobile()  { this.mobileOpen.set(false); }

//   ngOnInit() {
//     if (this.auth.isLoggedIn()) this.notif.startPolling();
//   }

//   ngOnDestroy() { this.notif.stopPolling(); }

//   logout() {
//     this.notif.reset();
//     this.auth.logout();
//   }
// }


// import { Component, ElementRef, HostListener, inject, signal, OnInit, OnDestroy } from '@angular/core';
// import { RouterLink, RouterLinkActive } from '@angular/router';
// import { AuthService } from '../../core/auth.service';
// import { NotificationService } from '../../features/notifications/services/notification.service';

// @Component({
//   selector: 'app-header',
//   standalone: true,
//   imports: [RouterLink, RouterLinkActive],
//   templateUrl: './header.component.html',
//   styleUrl: './header.component.css'
// })
// export class HeaderComponent implements OnInit, OnDestroy {
//   auth  = inject(AuthService);
//   notif = inject(NotificationService);
//   private host = inject(ElementRef<HTMLElement>);

//   mobileOpen   = signal(false);
//   userMenuOpen = signal(false);
//   unreadCount  = this.notif.unreadCount;
//   hasUnread    = this.notif.hasUnread;

//   toggleMobile()   { this.mobileOpen.update(v => !v); }
//   closeMobile()    { this.mobileOpen.set(false); }
//   toggleUserMenu() { this.userMenuOpen.update(v => !v); }
//   closeUserMenu()  { this.userMenuOpen.set(false); }
//   closeAll()       { this.closeMobile(); this.closeUserMenu(); }

//   // Ferme le dropdown si on clique en dehors
//   @HostListener('document:click', ['$event'])
//   onDocumentClick(e: MouseEvent) {
//     const menu = this.host.nativeElement.querySelector('.user-menu');
//     if (menu && !menu.contains(e.target as Node)) this.closeUserMenu();
//   }

//   @HostListener('document:keydown.escape')
//   onEscape() { this.closeUserMenu(); }

//   ngOnInit() {
//     if (this.auth.isLoggedIn()) this.notif.startPolling();
//   }

//   ngOnDestroy() { this.notif.stopPolling(); }

//   logout() {
//     this.closeAll();
//     this.notif.reset();
//     this.auth.logout();
//   }
// }


import { Component, ElementRef, HostListener, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/auth.service';
import { NotificationService } from '../../features/notifications/services/notification.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent implements OnInit, OnDestroy {
  auth  = inject(AuthService);
  notif = inject(NotificationService);
  private host = inject<ElementRef<HTMLElement>>(ElementRef);

  mobileOpen   = signal(false);
  userMenuOpen = signal(false);
  unreadCount  = this.notif.unreadCount;
  hasUnread    = this.notif.hasUnread;

  toggleMobile()   { this.mobileOpen.update(v => !v); }
  toggleUserMenu() { this.userMenuOpen.update(v => !v); }
  closeAll()       { this.mobileOpen.set(false); this.userMenuOpen.set(false); }

  /** Ferme le menu utilisateur au clic en dehors. */
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    const menu = this.host.nativeElement.querySelector('.user-menu');
    if (this.userMenuOpen() && menu && !menu.contains(event.target as Node)) {
      this.userMenuOpen.set(false);
    }
  }

  /** Ferme avec la touche Échap. */
  @HostListener('document:keydown.escape')
  onEscape() { this.userMenuOpen.set(false); }

  ngOnInit() {
    if (this.auth.isLoggedIn()) this.notif.startPolling();
  }

  ngOnDestroy() { this.notif.stopPolling(); }

  logout() {
    this.closeAll();
    this.notif.reset();
    this.auth.logout();
  }
  
}