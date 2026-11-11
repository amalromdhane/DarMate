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
  private host = inject(ElementRef<HTMLElement>);

  mobileOpen   = signal(false);
  userMenuOpen = signal(false);
  unreadCount  = this.notif.unreadCount;
  hasUnread    = this.notif.hasUnread;

  toggleMobile()   { this.mobileOpen.update(v => !v); }
  closeMobile()    { this.mobileOpen.set(false); }
  toggleUserMenu() { this.userMenuOpen.update(v => !v); }
  closeUserMenu()  { this.userMenuOpen.set(false); }
  closeAll()       { this.closeMobile(); this.closeUserMenu(); }

  // Close the profile dropdown when clicking outside
  @HostListener('document:click', ['$event'])
  onDocumentClick(e: MouseEvent) {
    const menu = this.host.nativeElement.querySelector('.user-menu');
    if (menu && !menu.contains(e.target as Node)) this.closeUserMenu();
  }

  @HostListener('document:keydown.escape')
  onEscape() { this.closeUserMenu(); }

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