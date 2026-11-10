import { Component, inject, OnInit, signal } from '@angular/core';
import { AppNotification } from '../../../../models';
import { NotificationService } from '../../services/notification.service';
@Component({ selector: 'app-notification-list', standalone: true, templateUrl: './notification-list.component.html', styleUrl: './notification-list.component.css' })
export class NotificationListComponent implements OnInit {
  private svc = inject(NotificationService);
  items = signal<AppNotification[]>([]); unread = signal(0);
  ngOnInit(): void { this.load(); }
  load(): void { this.svc.list().subscribe(r => { this.items.set(r.items); this.unread.set(r.unread_count); }); }
  read(n: AppNotification): void { if (!n.is_read) this.svc.read(n.id).subscribe(() => this.load()); }
  readAll(): void { this.svc.readAll().subscribe(() => this.load()); }
}
