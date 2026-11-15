// // import { Component, inject, signal } from '@angular/core';
// // import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
// // import { Router } from '@angular/router';
// // import { AuthService } from '../../../../core/auth.service';
// // import { ToastService } from '../../../../core/toast.service';
// // @Component({ selector: 'app-register', standalone: true, imports: [ReactiveFormsModule], templateUrl: './register.component.html', styleUrl: './register.component.css' })
// // export class RegisterComponent {
// //   private auth = inject(AuthService); private router = inject(Router); private toast = inject(ToastService);
// //   busy = signal(false);
// //   form = inject(FormBuilder).nonNullable.group({
// //     first_name: ['', Validators.required], last_name: ['', Validators.required],
// //     email: ['', [Validators.required, Validators.email]], password: ['', [Validators.required, Validators.minLength(8)]],
// //   });
// //   submit(): void {
// //     if (this.form.invalid) { this.form.markAllAsTouched(); return; }
// //     this.busy.set(true);
// //     this.auth.register({ ...this.form.getRawValue(), roles: ['SEEKER', 'OWNER'] }).subscribe({
// //       next: () => { this.toast.show('Compte créé. Vous pouvez vous connecter.'); this.router.navigate(['/auth/login']); },
// //       error: () => this.busy.set(false),
// //     });
// //   }
// // }
// import { Component, inject, signal } from '@angular/core';
// import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
// import { Router } from '@angular/router';
// import { AuthService } from '../../../../core/auth.service';
// import { ToastService } from '../../../../core/toast.service';

// @Component({
//   selector: 'app-register',
//   standalone: true,
//   imports: [ReactiveFormsModule],
//   templateUrl: './register.component.html',
//   styleUrl: './register.component.css'
// })
// export class RegisterComponent {

//   private fb = inject(FormBuilder);
//   private auth = inject(AuthService);
//   private toast = inject(ToastService);
//   private router = inject(Router);

//   busy = signal(false);

//   form = this.fb.nonNullable.group({
//     first_name: ['', Validators.required],
//     last_name: ['', Validators.required],
//     email: ['', [Validators.required, Validators.email]],
//     password: ['', [Validators.required, Validators.minLength(8)]],
//     role: ['SEEKER', Validators.required],
//   });

//   submit(): void {
//     if (this.form.invalid) {
//       this.form.markAllAsTouched();
//       return;
//     }

//     this.busy.set(true);

//     const { role, ...rest } = this.form.getRawValue();

//     this.auth.register({ ...rest, roles: [role] }).subscribe({
//       next: () => {
//         this.toast.show('Compte créé. Vous pouvez vous connecter.');
//         this.router.navigate(['/auth/login']);
//       },
//       error: () => {
//         this.busy.set(false);
//       }
//     });
//   }
// }
import { Component, OnInit, inject, signal } from '@angular/core';
import { AbstractControl, FormBuilder, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../../core/auth.service';
import { ReferenceService } from '../../../../core/reference.service';
import { ToastService } from '../../../../core/toast.service';
import { adultValidator, maxBirthDate } from '../../../../core/validators';
import { Ref } from '../../../../models';

const sameAs = (g: AbstractControl): ValidationErrors | null =>
  g.get('password')?.value === g.get('confirm')?.value ? null : { mismatch: true };

const LABELS: Record<string, string> = {
  first_name: 'Prénom', last_name: 'Nom', email: 'Email valide', phone: 'Téléphone (8 chiffres minimum)',
  city_id: 'Ville', birth_date: 'Date de naissance (18 ans minimum, pas dans le futur)',
  password: 'Mot de passe (8 caractères minimum)', confirm: 'Confirmation du mot de passe',
};

type Field = 'first_name' | 'last_name' | 'email' | 'phone' | 'city_id' | 'birth_date' | 'password' | 'confirm';

@Component({ selector: 'app-register', standalone: true, imports: [ReactiveFormsModule, RouterLink], templateUrl: './register.component.html', styleUrl: './register.component.css' })
export class RegisterComponent implements OnInit {
  private auth = inject(AuthService); private router = inject(Router); private toast = inject(ToastService);
  private ref = inject(ReferenceService);
  busy = signal(false);
  showPwd = signal(false);
  showSummary = signal(false);
  cities = signal<Ref[]>([]);
  maxBirth = maxBirthDate();

  form = inject(FormBuilder).nonNullable.group({
    first_name: ['', [Validators.required, Validators.maxLength(80)]],
    last_name:  ['', [Validators.required, Validators.maxLength(80)]],
    email:      ['', [Validators.required, Validators.email]],
    phone:      ['', [Validators.required, Validators.pattern(/^\+?[0-9 ]{8,20}$/)]],
    city_id:    [0, Validators.min(1)],
    birth_date: ['', adultValidator],
    role:       ['SEEKER', Validators.required],
    password:   ['', [Validators.required, Validators.minLength(8)]],
    confirm:    ['', Validators.required],
  }, { validators: [sameAs] });

  ngOnInit(): void { this.ref.cities().subscribe(c => this.cities.set(c)); }

  invalid(name: Field): boolean {
    const c = this.form.controls[name];
    return c.touched && c.invalid;
  }

  missing(): string[] {
    const out = Object.entries(this.form.controls).filter(([, c]) => c.invalid).map(([k]) => LABELS[k] ?? k);
    if (this.form.errors?.['mismatch'] && !out.includes(LABELS['confirm'])) out.push('Les deux mots de passe doivent être identiques');
    return out;
  }

  private errorText(e: any): string {
    const d = e?.error?.detail;
    if (typeof d === 'string') return d;
    if (Array.isArray(d) && d[0]?.msg) return String(d[0].msg).replace(/^Value error, /, '');
    return 'Inscription impossible. Vérifiez vos informations.';
  }

  submit(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); this.showSummary.set(true); return; }
    this.showSummary.set(false);
    this.busy.set(true);
    const { role, confirm, birth_date, phone, city_id, ...rest } = this.form.getRawValue();
    this.auth.register({ ...rest, phone: phone.trim(), city_id: +city_id, birth_date: birth_date || null, roles: [role] }).subscribe({
      next: () => { this.toast.show('Compte créé. Vous pouvez vous connecter.'); this.router.navigate(['/auth/login']); },
      error: e => { this.busy.set(false); this.toast.show(this.errorText(e), true); },
    });
  }
}