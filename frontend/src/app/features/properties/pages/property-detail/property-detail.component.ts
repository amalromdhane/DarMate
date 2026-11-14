// import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
// import { Router } from '@angular/router';
// import { Component, computed, inject, OnInit, input, signal } from '@angular/core';
// import { mediaUrls } from '../../../../shared/media-url';
// import { AuthService } from '../../../../core/auth.service';
// import { ToastService } from '../../../../core/toast.service';
// import { PropertyDetail, ReviewList } from '../../../../models';
// import { MessagingService } from '../../../messaging/services/messaging.service';
// import { RentalService } from '../../../rental-requests/services/rental.service';
// import { VisitService } from '../../../visits/services/visit.service';
// import { PropertyService } from '../../services/property.service';
// @Component({ selector: 'app-property-detail', standalone: true, imports: [ReactiveFormsModule], templateUrl: './property-detail.component.html', styleUrl: './property-detail.component.css' })
// export class PropertyDetailComponent implements OnInit {
//   id = input.required<string>();
//   sel = signal(0);
//  gallery = computed(() => mediaUrls(this.property()?.images));
//   private svc = inject(PropertyService); private rentals = inject(RentalService); private visits = inject(VisitService);
//   private chat = inject(MessagingService); private auth = inject(AuthService); private router = inject(Router); private toast = inject(ToastService);
//   property = signal<PropertyDetail | null>(null); reviews = signal<ReviewList | null>(null);
//   rentalForm = inject(FormBuilder).nonNullable.group({ message: ['', Validators.required], desired_move_in: '' });
//   visitForm = inject(FormBuilder).nonNullable.group({ starts_at: ['', Validators.required], ends_at: ['', Validators.required], note: '' });
//   ngOnInit(): void {
//     const n = Number(this.id());
//     this.svc.get(n).subscribe(p => this.property.set(p));
//     this.svc.reviews(n).subscribe(r => this.reviews.set(r));
//   }
//   private needLogin(): boolean { if (this.auth.isLoggedIn()) return false; this.router.navigate(['/auth/login']); return true; }
//   requestRental(): void {
//     if (this.needLogin() || this.rentalForm.invalid) return;
//     const v = this.rentalForm.getRawValue();
//     this.rentals.create({ property_id: Number(this.id()), message: v.message, desired_move_in: v.desired_move_in || null, group_id: null })
//       .subscribe(() => { this.toast.show('Demande envoyée.'); this.rentalForm.reset(); });
//   }
//   requestVisit(): void {
//     if (this.needLogin() || this.visitForm.invalid) return;
//     const v = this.visitForm.getRawValue();
//     this.visits.request({ property_id: Number(this.id()), slots: [{ starts_at: new Date(v.starts_at).toISOString(), ends_at: new Date(v.ends_at).toISOString() }], note: v.note || null, rental_request_id: null })
//       .subscribe(() => { this.toast.show('Demande de visite envoyée.'); this.visitForm.reset(); });
//   }
//   contact(): void {
//     const owner = this.property()?.owner_id;
//     if (this.needLogin() || !owner) return;
//     this.chat.open(owner).subscribe(c => this.router.navigate(['/messages'], { queryParams: { c: c.id } }));
//   }
// }

import { DatePipe } from '@angular/common';
import { Component, computed, inject, OnInit, input, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../../core/auth.service';
import { ToastService } from '../../../../core/toast.service';
import { PropertyDetail, ReviewList } from '../../../../models';
import { IconComponent } from '../../../../shared/components/icon/icon.component';
import { mediaUrls } from '../../../../shared/media-url';
import { MessagingService } from '../../../messaging/services/messaging.service';
import { RentalService } from '../../../rental-requests/services/rental.service';
import { VisitService } from '../../../visits/services/visit.service';
import { PropertyService } from '../../services/property.service';
@Component({ selector: 'app-property-detail', standalone: true, imports: [ReactiveFormsModule, RouterLink, IconComponent, DatePipe], templateUrl: './property-detail.component.html', styleUrl: './property-detail.component.css' })
export class PropertyDetailComponent implements OnInit {
  id = input.required<string>();
  auth = inject(AuthService);
  private svc = inject(PropertyService); private rentals = inject(RentalService); private visits = inject(VisitService);
  private chat = inject(MessagingService); private router = inject(Router); private toast = inject(ToastService);
  property = signal<PropertyDetail | null>(null); reviews = signal<ReviewList | null>(null);
  sel = signal(0); tab = signal<'rent' | 'visit'>('rent'); sentRent = signal(false); sentVisit = signal(false);
  gallery = computed(() => mediaUrls(this.property()?.images));
  stars = [1, 2, 3, 4, 5];
  today = new Date().toISOString().slice(0, 10);
  nowLocal = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  rentalForm = inject(FormBuilder).nonNullable.group({ message: ['', [Validators.required, Validators.minLength(10)]], desired_move_in: '' });
  visitForm = inject(FormBuilder).nonNullable.group({ starts_at: ['', Validators.required], ends_at: ['', Validators.required], note: '' });
  ngOnInit(): void {
    const n = Number(this.id());
    this.svc.get(n).subscribe(p => this.property.set(p));
    this.svc.reviews(n).subscribe(r => this.reviews.set(r));
  }
  coliving(p: PropertyDetail): boolean { return (p.coliving_allowed ?? p.coliving) === true; }

  // Seul un chercheur peut louer, visiter ou contacter, et jamais pour sa propre annonce
  canAct(p: PropertyDetail): boolean { return this.auth.isSeeker() && p.owner_id !== this.auth.user()?.id; }

  move(d: number): void { const n = this.gallery().length; this.sel.set((this.sel() + d + n) % n); }
  private needLogin(): boolean { if (this.auth.isLoggedIn()) return false; this.router.navigate(['/auth/login']); return true; }
  private notAllowed(): boolean {
    const p = this.property();
    if (p && this.canAct(p)) return false;
    this.toast.show('Cette action est réservée aux chercheurs de logement.', true);
    return true;
  }
  requestRental(): void {
    if (this.needLogin() || this.notAllowed()) return;
    if (this.rentalForm.invalid) { this.rentalForm.markAllAsTouched(); return; }
    const v = this.rentalForm.getRawValue();
    this.rentals.create({ property_id: Number(this.id()), message: v.message, desired_move_in: v.desired_move_in || null, group_id: null })
      .subscribe(() => { this.sentRent.set(true); this.rentalForm.reset(); });
  }
  requestVisit(): void {
    if (this.needLogin() || this.notAllowed()) return;
    if (this.visitForm.invalid) { this.visitForm.markAllAsTouched(); return; }
    const v = this.visitForm.getRawValue();
    if (new Date(v.ends_at) <= new Date(v.starts_at)) { this.toast.show('L’heure de fin doit être après le début.', true); return; }
    this.visits.request({ property_id: Number(this.id()), slots: [{ starts_at: new Date(v.starts_at).toISOString(), ends_at: new Date(v.ends_at).toISOString() }], note: v.note || null, rental_request_id: null })
      .subscribe(() => { this.sentVisit.set(true); this.visitForm.reset(); });
  }
  contact(): void {
    const owner = this.property()?.owner_id;
    if (this.needLogin() || this.notAllowed() || !owner) return;
    this.chat.open(owner).subscribe(c => this.router.navigate(['/messages'], { queryParams: { c: c.id } }));
  }
}