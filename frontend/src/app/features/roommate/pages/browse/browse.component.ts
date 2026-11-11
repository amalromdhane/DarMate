// import { DecimalPipe } from '@angular/common';
// import { Component, OnInit, computed, inject, signal } from '@angular/core';
// import { RouterLink, RouterLinkActive } from '@angular/router';
// import { ToastService } from '../../../../core/toast.service';
// import { Ref, RoommateMatch } from '../../../../models';
// import { RoommateService } from '../../services/roommate.service';
// import { SCHEDULES, initials } from '../../roommate.utils';

// @Component({
//   selector: 'app-roommate-browse', standalone: true,
//   imports: [DecimalPipe, RouterLink, RouterLinkActive],
//   templateUrl: './browse.component.html', styleUrl: 'browse.component.css'
// })
// export class BrowseComponent implements OnInit {
//   private api = inject(RoommateService);
//   private toast = inject(ToastService);

//   readonly schedules = SCHEDULES;
//   readonly levels = [1, 2, 3, 4, 5];
//   readonly initials = initials;

//   hasProfile = signal<boolean | null>(null);
//   matches = signal<RoommateMatch[]>([]);
//   cities = signal<Ref[]>([]);
//   loading = signal(true);

//   city = signal<number | undefined>(undefined);
//   minScore = signal(0);
//   kind = signal<'' | 'ROOM' | 'HOUSE'>('');
//   private timer?: ReturnType<typeof setTimeout>;

//   target = signal<RoommateMatch | null>(null);
//   msg = '';
//   sending = signal(false);

//   // "room / house" filter is applied in the browser
//   visible = computed(() => this.kind()
//     ? this.matches().filter(m => m.profile.looking_for === this.kind())
//     : this.matches());

//   ngOnInit() {
//     this.api.cities().subscribe({ next: c => this.cities.set(c) });
//     this.api.mine().subscribe({
//       next: p => { this.hasProfile.set(!!p); if (p) this.load(); else this.loading.set(false); },
//       error: () => this.loading.set(false)
//     });
//   }

//   load() {
//     this.loading.set(true);
//     this.api.search(this.city(), this.minScore()).subscribe({
//       next: r => { this.matches.set(r); this.loading.set(false); },
//       error: () => this.loading.set(false)
//     });
//   }

//   setCity(v: string) { this.city.set(v ? +v : undefined); this.load(); }
//   setScore(v: string) { this.minScore.set(+v); clearTimeout(this.timer); this.timer = setTimeout(() => this.load(), 300); }
//   setKind(k: '' | 'ROOM' | 'HOUSE') { this.kind.set(k); }

//   cityName(id?: number | null) { return this.cities().find(c => c.id === id)?.name ?? ''; }

//   contact(m: RoommateMatch) {
//     this.target.set(m);
//     this.msg = `Bonjour ${m.display_name}, notre compatibilité est de ${m.score}%. On en discute ?`;
//   }
//   send() {
//     const m = this.target(); if (!m) return;
//     this.sending.set(true);
//     this.api.send(m.profile.user_id, this.msg).subscribe({
//       next: () => { this.toast.show('Demande envoyée'); this.target.set(null); this.sending.set(false); },
//       error: () => this.sending.set(false)
//     });
//   }
// }

import { DecimalPipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { ToastService } from '../../../../core/toast.service';
import { Ref, RoommateMatch } from '../../../../models';
import { RoommateService } from '../../services/roommate.service';
import { SCHEDULES, initials } from '../../roommate.utils';

@Component({
  selector: 'app-roommate-browse', standalone: true,
  imports: [DecimalPipe, RouterLink, RouterLinkActive],
  templateUrl: './browse.component.html', styleUrl: './browse.component.css'
})
export class BrowseComponent implements OnInit {
  private api = inject(RoommateService);
  private toast = inject(ToastService);

  readonly schedules = SCHEDULES;
  readonly levels = [1, 2, 3, 4, 5];
  readonly initials = initials;

  hasProfile = signal<boolean | null>(null);
  matches = signal<RoommateMatch[]>([]);
  cities = signal<Ref[]>([]);
  loading = signal(true);

  city = signal<number | undefined>(undefined);
  minScore = signal(0);
  kind = signal<'' | 'ROOM' | 'HOUSE'>('');
  private timer?: ReturnType<typeof setTimeout>;

  target = signal<RoommateMatch | null>(null);
  msg = '';
  sending = signal(false);

  // "room / house" filter is applied in the browser
  visible = computed(() => this.kind()
    ? this.matches().filter(m => m.profile.looking_for === this.kind())
    : this.matches());

  ngOnInit() {
    this.api.cities().subscribe(c => this.cities.set(c));
    this.api.mine().subscribe({
      next: p => { this.hasProfile.set(!!p); if (p) this.load(); else this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  load() {
    this.loading.set(true);
    this.api.search(this.city(), this.minScore()).subscribe({
      next: r => { this.matches.set(r); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  setCity(v: string) { this.city.set(v ? +v : undefined); this.load(); }
  setScore(v: string) { this.minScore.set(+v); clearTimeout(this.timer); this.timer = setTimeout(() => this.load(), 300); }
  setKind(k: '' | 'ROOM' | 'HOUSE') { this.kind.set(k); }

  cityName(id?: number | null) { return this.cities().find(c => c.id === id)?.name ?? ''; }

  contact(m: RoommateMatch) {
    this.target.set(m);
    this.msg = `Bonjour ${m.display_name}, notre compatibilité est de ${m.score}%. On en discute ?`;
  }
  send() {
    const m = this.target(); if (!m) return;
    this.sending.set(true);
    this.api.send(m.profile.user_id, this.msg).subscribe({
      next: () => { this.toast.show('Demande envoyée'); this.target.set(null); this.sending.set(false); },
      error: () => this.sending.set(false)
    });
  }
}