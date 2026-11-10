// import { Component, inject, signal } from '@angular/core';
// import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
// import { Router } from '@angular/router';
// import { AuthService } from '../../../../core/auth.service';
// import { ToastService } from '../../../../core/toast.service';
// @Component({ selector: 'app-register', standalone: true, imports: [ReactiveFormsModule], templateUrl: './register.component.html', styleUrl: './register.component.css' })
// export class RegisterComponent {
//   private auth = inject(AuthService); private router = inject(Router); private toast = inject(ToastService);
//   busy = signal(false);
//   form = inject(FormBuilder).nonNullable.group({
//     first_name: ['', Validators.required], last_name: ['', Validators.required],
//     email: ['', [Validators.required, Validators.email]], password: ['', [Validators.required, Validators.minLength(8)]],
//   });
//   submit(): void {
//     if (this.form.invalid) { this.form.markAllAsTouched(); return; }
//     this.busy.set(true);
//     this.auth.register({ ...this.form.getRawValue(), roles: ['SEEKER', 'OWNER'] }).subscribe({
//       next: () => { this.toast.show('Compte créé. Vous pouvez vous connecter.'); this.router.navigate(['/auth/login']); },
//       error: () => this.busy.set(false),
//     });
//   }
// }
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../../core/auth.service';
import { ToastService } from '../../../../core/toast.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {

  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private toast = inject(ToastService);
  private router = inject(Router);

  busy = signal(false);

  form = this.fb.nonNullable.group({
    first_name: ['', Validators.required],
    last_name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    role: ['SEEKER', Validators.required],
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.busy.set(true);

    const { role, ...rest } = this.form.getRawValue();

    this.auth.register({ ...rest, roles: [role] }).subscribe({
      next: () => {
        this.toast.show('Compte créé. Vous pouvez vous connecter.');
        this.router.navigate(['/auth/login']);
      },
      error: () => {
        this.busy.set(false);
      }
    });
  }
}