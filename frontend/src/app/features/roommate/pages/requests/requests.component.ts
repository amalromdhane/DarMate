import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../../core/auth.service';
import { ToastService } from '../../../../core/toast.service';
import { RoommateRequest } from '../../../../models';
import { RoommateService } from '../../services/roommate.service';

@Component({
  selector: 'app-roommate-requests', standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './requests.component.html', styleUrl: 'requests.component.css'
})
export class RequestsComponent implements OnInit {
  private api = inject(RoommateService);
  private auth = inject(AuthService);
  private toast = inject(ToastService);

  items = signal<RoommateRequest[]>([]);
  loading = signal(true);
  tab = signal<'received' | 'sent'>('received');

  private me = computed(() => this.auth.user()?.id);
  isSent = (r: RoommateRequest) => r.sender_id != null && r.sender_id === this.me();
  list = computed(() => this.items().filter(r => (this.tab() === 'sent') === this.isSent(r)));

  readonly labels: Record<string, string> = { PENDING: 'En attente', ACCEPTED: 'Acceptée', REJECTED: 'Refusée' };

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.requests().subscribe({
      next: r => { this.items.set(r); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  respond(r: RoommateRequest, accept: boolean) {
    this.api.respond(r.id, accept).subscribe(() => {
      this.toast.show(accept ? 'Demande acceptée' : 'Demande refusée');
      this.load();
    });
  }
}