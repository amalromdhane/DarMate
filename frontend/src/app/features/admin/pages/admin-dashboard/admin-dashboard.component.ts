// import { Component, inject, OnInit, signal } from '@angular/core';
// import { FormsModule } from '@angular/forms';
// import { AdminUser, Page } from '../../../../models';
// import { StatusLabelPipe } from '../../../../shared/pipes/status-label.pipe';
// import { AdminService } from '../../services/admin.service';
// @Component({ selector: 'app-admin-dashboard', standalone: true, imports: [FormsModule, StatusLabelPipe], templateUrl: './admin-dashboard.component.html', styleUrl: './admin-dashboard.component.css' })
// export class AdminDashboardComponent implements OnInit {
//   private svc = inject(AdminService);
//   stats = signal<[string, number][]>([]); users = signal<Page<AdminUser> | null>(null); q = '';
//   ngOnInit(): void { this.svc.stats().subscribe(s => this.stats.set(Object.entries(s))); this.load(); }
//   load(): void { this.svc.users(this.q, 1).subscribe(u => this.users.set(u)); }
//   setStatus(u: AdminUser, s: string): void { this.svc.setStatus(u.id, s).subscribe(() => this.load()); }
// }

import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AdminUser, Page } from '../../../../models';
import { StatusLabelPipe } from '../../../../shared/pipes/status-label.pipe';
import { AdminService } from '../../services/admin.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [FormsModule, StatusLabelPipe],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.css'
})
export class AdminDashboardComponent implements OnInit {
  private svc = inject(AdminService);

  stats = signal<[string, number][]>([]);
  users = signal<Page<AdminUser> | null>(null);
  q = '';
  loading = signal(false);
  activeTab = signal<'all' | 'ACTIVE' | 'SUSPENDED' | 'BANNED'>('all');

  ngOnInit(): void {
    this.svc.stats().subscribe(s => this.stats.set(Object.entries(s)));
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.svc.users(this.q, 1).subscribe({
      next: u => { this.users.set(u); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  setStatus(u: AdminUser, s: string): void {
    this.svc.setStatus(u.id, s).subscribe(() => this.load());
  }

  filteredUsers(): AdminUser[] {
    const items = this.users()?.items ?? [];
    const tab = this.activeTab();
    return tab === 'all' ? items : items.filter(u => u.status === tab);
  }
}