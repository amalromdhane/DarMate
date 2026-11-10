import { Component, inject, signal, OnInit } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ProfileService } from '../../services/profile.service';
import { AuthService } from '../../../../core/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  private fb   = inject(FormBuilder);
  private api  = inject(ProfileService);
  private auth = inject(AuthService);

  message = signal<{ type: 'ok' | 'err'; text: string } | null>(null);
  saving  = signal(false);

  infoForm = this.fb.nonNullable.group({
    firstName: ['', Validators.required],
    lastName:  ['', Validators.required],
    email:     ['', [Validators.required, Validators.email]],
    phone:     ['']
  });

  pwdForm = this.fb.nonNullable.group({
    currentPassword: ['', Validators.required],
    newPassword:     ['', [Validators.required, Validators.minLength(8)]]
  });

  ngOnInit() {
    this.api.get().subscribe(p => this.infoForm.patchValue(p));
  }

  saveInfo() {
    if (this.infoForm.invalid) return this.infoForm.markAllAsTouched();
    this.saving.set(true);
    this.api.update(this.infoForm.getRawValue()).subscribe({
      next: () => { this.saving.set(false); this.flash('ok', 'Profil mis à jour ✔'); },
      error: () => { this.saving.set(false); this.flash('err', 'Erreur lors de la mise à jour'); }
    });
  }

  savePassword() {
    if (this.pwdForm.invalid) return this.pwdForm.markAllAsTouched();
    this.api.changePassword(this.pwdForm.getRawValue()).subscribe({
      next: () => { this.pwdForm.reset(); this.flash('ok', 'Mot de passe modifié ✔'); },
      error: () => this.flash('err', 'Mot de passe actuel incorrect')
    });
  }

  deleteAccount() {
    if (!confirm('Supprimer définitivement votre compte ?')) return;
    this.api.deleteAccount().subscribe(() => this.auth.logout());
  }

  private flash(type: 'ok' | 'err', text: string) {
    this.message.set({ type, text });
    setTimeout(() => this.message.set(null), 3500);
  }
}