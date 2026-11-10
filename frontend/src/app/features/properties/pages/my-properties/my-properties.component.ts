import { Component, inject, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Page, PropertyCard } from '../../../../models';
import { StatusLabelPipe } from '../../../../shared/pipes/status-label.pipe';
import { PropertyCardComponent } from '../../components/property-card/property-card.component';
import { PropertyService } from '../../services/property.service';
@Component({ selector: 'app-my-properties', standalone: true, imports: [RouterLink, PropertyCardComponent, StatusLabelPipe], templateUrl: './my-properties.component.html', styleUrl: './my-properties.component.css' })
export class MyPropertiesComponent implements OnInit {
  private svc = inject(PropertyService);
  data = signal<Page<PropertyCard> | null>(null);
  ngOnInit(): void { this.load(); }
  load(): void { this.svc.mine().subscribe(d => this.data.set(d)); }
  toggle(p: PropertyCard): void { this.svc.setStatus(p.id, p.status === 'AVAILABLE' ? 'SUSPENDED' : 'AVAILABLE').subscribe(() => this.load()); }
  remove(p: PropertyCard): void { if (confirm('Supprimer cette annonce ?')) this.svc.remove(p.id).subscribe(() => this.load()); }
}
