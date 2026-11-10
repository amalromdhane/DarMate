import { Component, inject, input, OnInit, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { forkJoin, of, switchMap } from 'rxjs';
import { ReferenceService } from '../../../../core/reference.service';
import { ToastService } from '../../../../core/toast.service';
import { PropertyPayload, Ref } from '../../../../models';
import { PropertyService } from '../../services/property.service';
@Component({ selector: 'app-property-form', standalone: true, imports: [ReactiveFormsModule], templateUrl: './property-form.component.html', styleUrl: './property-form.component.css' })
export class PropertyFormComponent implements OnInit {
  id = input<string>();
  private svc = inject(PropertyService); private ref = inject(ReferenceService); private router = inject(Router); private toast = inject(ToastService);
  cities = signal<Ref[]>([]); categories = signal<Ref[]>([]); files = signal<File[]>([]);
  form = inject(FormBuilder).nonNullable.group({
    title: ['', Validators.required], description: ['', Validators.required], price: [0, [Validators.required, Validators.min(1)]],
    rooms: [1, Validators.min(1)], surface_m2: [null as number | null], city_id: [0, Validators.min(1)], category_id: [0, Validators.min(1)],
    address: '', conditions: '', available_from: '', coliving_allowed: false, max_roommates: 1,
  });
  ngOnInit(): void {
    this.ref.cities().subscribe(c => this.cities.set(c)); this.ref.categories().subscribe(c => this.categories.set(c));
    const id = this.id();
    if (id) this.svc.get(+id).subscribe(p => this.form.patchValue({
      title: p.title, description: p.description ?? '', price: p.price, rooms: p.rooms ?? 1, surface_m2: p.surface_m2 ?? null,
      address: p.address ?? '', conditions: p.conditions ?? '', available_from: p.available_from ?? '',
      coliving_allowed: !!p.coliving_allowed, max_roommates: p.max_roommates ?? 1,
    }));
  }
  pick(e: Event): void { this.files.set(Array.from((e.target as HTMLInputElement).files ?? [])); }
  submit(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); this.toast.show('Complétez les champs obligatoires (ville et type compris).', true); return; }
    const v = this.form.getRawValue();
    const body: PropertyPayload = {
      ...v, city_id: +v.city_id, category_id: +v.category_id,
      available_from: v.available_from || null, max_roommates: v.coliving_allowed ? v.max_roommates : 1,
    };
    const id = this.id();
    (id ? this.svc.update(+id, body) : this.svc.create(body)).pipe(
      switchMap(p => this.files().length ? forkJoin(this.files().map(f => this.svc.addImage(p.id, f))) : of([])),
    ).subscribe(() => { this.toast.show('Annonce enregistrée.'); this.router.navigate(['/properties/mine']); });
  }
}