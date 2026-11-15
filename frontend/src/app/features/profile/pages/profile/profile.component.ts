import { DatePipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../../../core/auth.service';
import { User } from '../../../../models';
import { UserService } from '../../../users/services/user.service';
import { adultValidator, maxBirthDate } from '../../../../core/validators';

const ROLE_LABELS: Record<string, string> = { SEEKER: 'Chercheur de logement', OWNER: 'Propriétaire', ADMIN: 'Administrateur' };
const STATUS_LABELS: Record<string, string> = { ACTIVE: 'Compte actif', PENDING: 'En attente', SUSPENDED: 'Suspendu', BLOCKED: 'Bloqué' };

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [ReactiveFormsModule, DatePipe],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  private fb = inject(FormBuilder);
  private users = inject(UserService);
  private auth = inject(AuthService);

  me = this.auth.user;
  message = signal<{ type: 'ok' | 'err'; text: string } | null>(null);
  saving = signal(false);
  changing = signal(false);
  showPwd = signal(false);

  maxBirth = maxBirthDate();

infoForm = this.fb.nonNullable.group({
  first_name: ['', [Validators.required, Validators.maxLength(80)]],
  last_name:  ['', [Validators.required, Validators.maxLength(80)]],
  phone:      ['', Validators.maxLength(30)],
  birth_date: ['', adultValidator],
  language:   ['fr'],
  bio:        ['', Validators.maxLength(2000)],
});

  pwdForm = this.fb.nonNullable.group({
    current_password: ['', Validators.required],
    new_password:     ['', [Validators.required, Validators.minLength(8)]],
  });

  fullName = computed(() => {
    const u = this.me();
    return `${u?.profile?.first_name ?? u?.first_name ?? ''} ${u?.profile?.last_name ?? u?.last_name ?? ''}`.trim();
  });
  initials = computed(() => {
    const parts = this.fullName().split(' ').filter(Boolean);
    return (parts.length ? parts.map(p => p[0]).join('') : (this.me()?.email ?? '?')[0]).slice(0, 2).toUpperCase();
  });
  roleLabels = computed(() => (this.me()?.roles ?? []).map(r => ROLE_LABELS[r] ?? r));
  statusLabel = computed(() => { const s = this.me()?.status; return s ? (STATUS_LABELS[s] ?? s) : ''; });

  ngOnInit() {
    const cached = this.me();
    if (cached) this.fill(cached);       // affichage immédiat avec l'utilisateur connecté
    this.reload();                       // puis rafraîchissement depuis l'API
  }

  private reload() {
    this.users.me().subscribe(u => { this.auth.user.set(u); this.fill(u); });
  }

  private fill(u: User) {
    const p = u.profile;
    this.infoForm.reset({
      first_name: p?.first_name ?? u.first_name ?? '',
      last_name:  p?.last_name ?? u.last_name ?? '',
      phone:      p?.phone ?? u.phone ?? '',
      birth_date: p?.birth_date ?? '',
      language:   p?.language ?? 'fr',
      bio:        p?.bio ?? u.bio ?? '',
    });
  }

  saveInfo() {
    if (this.infoForm.invalid) { this.infoForm.markAllAsTouched(); return; }
    const f = this.infoForm.getRawValue();
    this.saving.set(true);
    this.users.update({
      first_name: f.first_name.trim(), last_name: f.last_name.trim(),
      phone: f.phone.trim() || null, bio: f.bio.trim() || null,
      birth_date: f.birth_date || null, language: f.language,
    }).subscribe({
      next: () => { this.saving.set(false); this.flash('ok', 'Profil mis à jour'); this.reload(); },
      error: e => { this.saving.set(false); this.flash('err', this.detail(e, 'Erreur lors de la mise à jour')); }
    });
  }

  savePassword() {
    if (this.pwdForm.invalid) { this.pwdForm.markAllAsTouched(); return; }
    const { current_password, new_password } = this.pwdForm.getRawValue();
    this.changing.set(true);
    this.users.changePassword(current_password, new_password).subscribe({
      next: () => { this.changing.set(false); this.pwdForm.reset(); this.flash('ok', 'Mot de passe modifié'); },
      error: e => { this.changing.set(false); this.flash('err', this.detail(e, 'Mot de passe actuel incorrect')); }
    });
  }

  private detail(e: any, fallback: string): string {
  const d = e?.error?.detail;
  if (typeof d === 'string') return d;
  if (Array.isArray(d) && d[0]?.msg) return String(d[0].msg).replace(/^Value error, /, '');
  return fallback;
}

  private flash(type: 'ok' | 'err', text: string) {
    this.message.set({ type, text });
    setTimeout(() => this.message.set(null), 3500);
  }

  
}