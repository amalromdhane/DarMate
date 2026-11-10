// import { Component, inject, OnInit, signal } from '@angular/core';
// import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
// import { Router } from '@angular/router';
// import { AuthService } from '../../../../core/auth.service';
// import { ReferenceService } from '../../../../core/reference.service';
// import { ToastService } from '../../../../core/toast.service';
// import { Page, PropertyCard, PropertyFilters, Ref } from '../../../../models';
// import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';
// import { FavoriteService } from '../../../favorites/services/favorite.service';
// import { PropertyCardComponent } from '../../components/property-card/property-card.component';
// import { PropertyService } from '../../services/property.service';
// @Component({ selector: 'app-property-list', standalone: true, imports: [ReactiveFormsModule, PropertyCardComponent, PaginationComponent], templateUrl: './property-list.component.html', styleUrl: './property-list.component.css' })
// export class PropertyListComponent implements OnInit {
//   private svc = inject(PropertyService); private favs = inject(FavoriteService); private ref = inject(ReferenceService);
//   private auth = inject(AuthService); private router = inject(Router); private toast = inject(ToastService);
//   result = signal<Page<PropertyCard> | null>(null); page = signal(1);
//   cities = signal<Ref[]>([]); categories = signal<Ref[]>([]);
//   form = inject(FormBuilder).nonNullable.group({ q: '', city_id: '', category_id: '', min_price: '', max_price: '', min_rooms: '', coliving: false, sort: 'recent' });
//   ngOnInit(): void { this.ref.cities().subscribe(c => this.cities.set(c)); this.ref.categories().subscribe(c => this.categories.set(c)); this.load(); }
//   private filters(): PropertyFilters { const v = this.form.getRawValue(); return { ...v, coliving: v.coliving || '' }; }
//   load(): void { this.svc.search(this.filters(), this.page()).subscribe(r => this.result.set(r)); }
//   apply(): void { this.page.set(1); this.load(); }
//   go(p: number): void { this.page.set(p); this.load(); }
//   toggleFav(p: PropertyCard): void {
//     if (!this.auth.isLoggedIn()) { this.router.navigate(['/auth/login']); return; }
//     (p.is_favorite ? this.favs.remove(p.id) : this.favs.add(p.id)).subscribe(() => this.load());
//   }
//   saveSearch(): void {
//     const name = prompt('Nom de la recherche ?');
//     if (name) this.svc.saveSearch(name, this.filters(), true).subscribe(() => this.toast.show('Recherche enregistrée avec alerte.'));
//   }
//   loggedIn(): boolean { return this.auth.isLoggedIn(); }
// }



import { Component, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { debounceTime } from 'rxjs';
import { AuthService } from '../../../../core/auth.service';
import { ReferenceService } from '../../../../core/reference.service';
import { ToastService } from '../../../../core/toast.service';
import { Page, PropertyCard, PropertyFilters, Ref } from '../../../../models';
import { IconComponent, IconName } from '../../../../shared/components/icon/icon.component';
import { PaginationComponent } from '../../../../shared/components/pagination/pagination.component';
import { FavoriteService } from '../../../favorites/services/favorite.service';
import { PropertyCardComponent } from '../../components/property-card/property-card.component';
import { PropertyService } from '../../services/property.service';
@Component({ selector: 'app-property-list', standalone: true, imports: [ReactiveFormsModule, PropertyCardComponent, PaginationComponent, IconComponent], templateUrl: './property-list.component.html', styleUrl: './property-list.component.css' })
export class PropertyListComponent implements OnInit {
  private svc = inject(PropertyService); private favs = inject(FavoriteService); private ref = inject(ReferenceService);
  private auth = inject(AuthService); private router = inject(Router); private toast = inject(ToastService);
  result = signal<Page<PropertyCard> | null>(null); page = signal(1); loading = signal(true);
  cities = signal<Ref[]>([]); categories = signal<Ref[]>([]);
  advanced = signal(false); active = signal<{ key: string; label: string }[]>([]);
  roomChoices = [1, 2, 3, 4]; skeletons = [1, 2, 3, 4, 5, 6];
  form = inject(FormBuilder).nonNullable.group({ q: '', city_id: '', category_id: '', min_price: '', max_price: '', min_rooms: '', coliving: false, sort: 'recent' });
  constructor() {
    this.form.valueChanges.pipe(debounceTime(350), takeUntilDestroyed()).subscribe(() => { this.page.set(1); this.refreshChips(); this.load(); });
  }
  ngOnInit(): void { this.ref.cities().subscribe(c => this.cities.set(c)); this.ref.categories().subscribe(c => this.categories.set(c)); this.load(); }
  private filters(): PropertyFilters { const v = this.form.getRawValue(); return { ...v, coliving: v.coliving || '' }; }
  load(): void {
    this.loading.set(true);
    this.svc.search(this.filters(), this.page()).subscribe({ next: r => { this.result.set(r); this.loading.set(false); }, error: () => this.loading.set(false) });
  }
  go(p: number): void { this.page.set(p); this.load(); window.scrollTo({ top: 0, behavior: 'smooth' }); }
  setCat(id: number | ''): void { this.form.patchValue({ category_id: id === '' ? '' : String(id) }); }
  setRooms(n: number): void { this.form.patchValue({ min_rooms: this.form.value.min_rooms === String(n) ? '' : String(n) }); }
  clear(key: string): void { this.form.get(key)?.reset(); }
  resetAll(): void { this.form.reset(); }
  catIcon(name: string): IconName { const n = name.toLowerCase(); return n.includes('chambre') ? 'bed' : n.includes('appart') || n.includes('studio') || n.includes('duplex') ? 'building' : 'home'; }
  private refreshChips(): void {
    const v = this.form.getRawValue(); const out: { key: string; label: string }[] = [];
    if (v.q) out.push({ key: 'q', label: `« ${v.q} »` });
    if (v.city_id) out.push({ key: 'city_id', label: this.cities().find(c => String(c.id) === v.city_id)?.name ?? 'Ville' });
    if (v.category_id) out.push({ key: 'category_id', label: this.categories().find(c => String(c.id) === v.category_id)?.name ?? 'Type' });
    if (v.min_price) out.push({ key: 'min_price', label: `≥ ${v.min_price} DT` });
    if (v.max_price) out.push({ key: 'max_price', label: `≤ ${v.max_price} DT` });
    if (v.min_rooms) out.push({ key: 'min_rooms', label: `${v.min_rooms}+ pièces` });
    if (v.coliving) out.push({ key: 'coliving', label: 'Colocation' });
    this.active.set(out);
  }
  toggleFav(p: PropertyCard): void {
    if (!this.auth.isLoggedIn()) { this.router.navigate(['/auth/login']); return; }
    (p.is_favorite ? this.favs.remove(p.id) : this.favs.add(p.id)).subscribe(() => this.load());
  }
  saveSearch(): void {
    const name = prompt('Nom de la recherche ?');
    if (name) this.svc.saveSearch(name, this.filters(), true).subscribe(() => this.toast.show('Recherche enregistrée avec alerte.'));
  }
  loggedIn(): boolean { return this.auth.isLoggedIn(); }
}

