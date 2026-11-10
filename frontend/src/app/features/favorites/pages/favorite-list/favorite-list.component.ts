import { Component, inject, OnInit, signal } from '@angular/core';
import { PropertyCard } from '../../../../models';
import { PropertyCardComponent } from '../../../properties/components/property-card/property-card.component';
import { FavoriteService } from '../../services/favorite.service';
@Component({ selector: 'app-favorite-list', standalone: true, imports: [PropertyCardComponent], templateUrl: './favorite-list.component.html', styleUrl: './favorite-list.component.css' })
export class FavoriteListComponent implements OnInit {
  private svc = inject(FavoriteService); items = signal<PropertyCard[]>([]);
  ngOnInit(): void { this.load(); }
  load(): void { this.svc.list().subscribe(i => this.items.set(i.map(p => ({ ...p, is_favorite: true })))); }
  remove(p: PropertyCard): void { this.svc.remove(p.id).subscribe(() => this.load()); }
}