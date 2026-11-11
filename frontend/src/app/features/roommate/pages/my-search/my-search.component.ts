// import { Component, OnInit, inject, signal } from '@angular/core';
// import { toSignal } from '@angular/core/rxjs-interop';
// import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
// import { Router, RouterLink, RouterLinkActive } from '@angular/router';
// import { ToastService } from '../../../../core/toast.service';
// import { Ref, RoommateProfile } from '../../../../models';
// import { RoommateService } from '../../services/roommate.service';
// import { SCHEDULES } from '../../roommate.utils';

// @Component({
//   selector: 'app-roommate-my-search', standalone: true,
//   imports: [ReactiveFormsModule, RouterLink, RouterLinkActive],
//   templateUrl: './my-search.component.html', styleUrl: 'my-search.component.css'
// })
// export class MySearchComponent implements OnInit {
//   private fb = inject(FormBuilder);
//   private api = inject(RoommateService);
//   private toast = inject(ToastService);
//   private router = inject(Router);

//   readonly schedules = Object.entries(SCHEDULES).map(([value, label]) => ({ value, label }));
//   cities = signal<Ref[]>([]);
//   busy = signal(false);
//   isNew = signal(true);

//   form = this.fb.group({
//     looking_for: ['ROOM' as 'ROOM' | 'HOUSE'],
//     city_id: [null as number | null, Validators.required],
//     budget_min: [null as number | null],
//     budget_max: [null as number | null],
//     schedule: ['FLEXIBLE'],
//     smoker: [false],
//     has_pets: [false],
//     cleanliness: [3],
//     sociability: [3],
//     about: [''],
//     is_active: [true],
//   });

//   v = toSignal(this.form.valueChanges, { initialValue: this.form.getRawValue() });

//   ngOnInit() {
//     this.api.cities().subscribe({ next: c => this.cities.set(c) });
//     this.api.mine().subscribe(p => {
//       if (!p) return;
//       this.isNew.set(false);
//       this.form.patchValue({
//         looking_for: p.looking_for ?? 'ROOM',
//         city_id: p.city_id ?? null,
//         budget_min: p.budget_min != null ? Number(p.budget_min) : null,
//         budget_max: p.budget_max != null ? Number(p.budget_max) : null,
//         schedule: p.schedule,
//         smoker: p.smoker, has_pets: p.has_pets,
//         cleanliness: p.cleanliness, sociability: p.sociability,
//         about: p.about ?? '', is_active: p.is_active,
//       });
//     });
//   }

//   setKind(k: 'ROOM' | 'HOUSE') { this.form.controls.looking_for.setValue(k); }
//   setSchedule(s: string) { this.form.controls.schedule.setValue(s); }

//   budgetOk(): boolean {
//     const { budget_min: a, budget_max: b } = this.form.getRawValue();
//     return a == null || b == null || a <= b;
//   }

//   submit() {
//     if (this.form.invalid || !this.budgetOk()) { this.form.markAllAsTouched(); return; }
//     const f = this.form.getRawValue();
//     const body = {
//       ...f,
//       city_id: f.city_id ? +f.city_id : null,
//       budget_min: f.budget_min ?? null,
//       budget_max: f.budget_max ?? null,
//       about: f.about?.trim() || null,
//     } as Partial<RoommateProfile>;

//     this.busy.set(true);
//     this.api.save(body).subscribe({
//       next: () => { this.toast.show('Recherche enregistrée 🎉'); this.router.navigate(['/roommates']); },
//       error: () => this.busy.set(false),
//     });
//   }
// }
import { Component, OnInit, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { ToastService } from '../../../../core/toast.service';
import { Ref, RoommateProfile } from '../../../../models';
import { RoommateService } from '../../services/roommate.service';
import { SCHEDULES } from '../../roommate.utils';

@Component({
  selector: 'app-roommate-my-search', standalone: true,
  imports: [ReactiveFormsModule, RouterLink, RouterLinkActive],
  templateUrl: './my-search.component.html', styleUrl: './my-search.component.css'
})
export class MySearchComponent implements OnInit {
  private fb = inject(FormBuilder);
  private api = inject(RoommateService);
  private toast = inject(ToastService);
  private router = inject(Router);

  readonly schedules = Object.entries(SCHEDULES).map(([value, label]) => ({ value, label }));
  cities = signal<Ref[]>([]);
  busy = signal(false);
  isNew = signal(true);

  form = this.fb.group({
    looking_for: ['ROOM' as 'ROOM' | 'HOUSE'],
    city_id: [null as number | null, Validators.required],
    budget_min: [null as number | null],
    budget_max: [null as number | null],
    schedule: ['FLEXIBLE'],
    smoker: [false],
    has_pets: [false],
    cleanliness: [3],
    sociability: [3],
    about: [''],
    is_active: [true],
  });

  v = toSignal(this.form.valueChanges, { initialValue: this.form.getRawValue() });

  ngOnInit() {
    this.api.cities().subscribe(c => this.cities.set(c));
    this.api.mine().subscribe(p => {
      if (!p) return;
      this.isNew.set(false);
      this.form.patchValue({
        looking_for: p.looking_for ?? 'ROOM',
        city_id: p.city_id ?? null,
        budget_min: p.budget_min != null ? Number(p.budget_min) : null,
        budget_max: p.budget_max != null ? Number(p.budget_max) : null,
        schedule: p.schedule,
        smoker: p.smoker, has_pets: p.has_pets,
        cleanliness: p.cleanliness, sociability: p.sociability,
        about: p.about ?? '', is_active: p.is_active,
      });
    });
  }

  setKind(k: 'ROOM' | 'HOUSE') { this.form.controls.looking_for.setValue(k); }
  setSchedule(s: string) { this.form.controls.schedule.setValue(s); }

  budgetOk(): boolean {
    const { budget_min: a, budget_max: b } = this.form.getRawValue();
    return a == null || b == null || a <= b;
  }

  submit() {
    if (this.form.invalid || !this.budgetOk()) { this.form.markAllAsTouched(); return; }
    const f = this.form.getRawValue();
    const body = {
      ...f,
      city_id: f.city_id ? +f.city_id : null,
      budget_min: f.budget_min ?? null,
      budget_max: f.budget_max ?? null,
      about: f.about?.trim() || null,
    } as Partial<RoommateProfile>;

    this.busy.set(true);
    this.api.save(body).subscribe({
      next: () => { this.toast.show('Recherche enregistrée 🎉'); this.router.navigate(['/roommates']); },
      error: () => this.busy.set(false),
    });
  }
}