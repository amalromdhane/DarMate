import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RentalRequest } from '../../../../models';
import { StatusLabelPipe } from '../../../../shared/pipes/status-label.pipe';
import { RentalService } from '../../services/rental.service';
@Component({ selector: 'app-rental-list', standalone: true, imports: [RouterLink, StatusLabelPipe], templateUrl: './rental-list.component.html', styleUrl: './rental-list.component.css' })
export class RentalListComponent implements OnInit {
  private svc = inject(RentalService);
  box = signal<'sent' | 'received'>('sent'); items = signal<RentalRequest[]>([]);
  ngOnInit(): void { this.load(); }
  setBox(b: 'sent' | 'received'): void { this.box.set(b); this.load(); }
  load(): void { this.svc.list(this.box()).subscribe(i => this.items.set(i)); }
  setStatus(r: RentalRequest, s: string): void { this.svc.setStatus(r.id, s).subscribe(() => this.load()); }
  confirm(r: RentalRequest): void { this.svc.confirm(r.id).subscribe(() => this.load()); }
}
