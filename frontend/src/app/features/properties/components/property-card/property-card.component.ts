// import { Component, computed, input, output, signal } from '@angular/core';
// import { RouterLink } from '@angular/router';
// import { Img, PropertyCard } from '../../../../models';
// import { mediaUrls } from '../../../../shared/media-url';
// @Component({ selector: 'app-property-card', standalone: true, imports: [RouterLink], templateUrl: './property-card.component.html', styleUrl: './property-card.component.css' })
// export class PropertyCardComponent {
//   property = input.required<PropertyCard>(); showFav = input(true);
//   favToggle = output<PropertyCard>();
//   index = signal(0);
//   urls = computed(() => {
//     const p = this.property() as unknown as Record<string, unknown>;
//     const fromImages = mediaUrls(p['images'] as Img[] | undefined);
//     if (fromImages.length) return fromImages;
//     const cover = (p['cover_url'] ?? p['image_url'] ?? p['cover'] ?? p['main_image'] ?? p['thumbnail']) as string | undefined;
//     return mediaUrls(cover ? [{ id: 0, url: cover }] : []);
//   });
//   current = computed(() => this.urls()[this.index()] ?? null);
//   move(d: number): void { const n = this.urls().length; this.index.set((this.index() + d + n) % n); }
// }

import { Component, computed, input, output, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Img, PropertyCard } from '../../../../models';
import { IconComponent } from '../../../../shared/components/icon/icon.component';
import { mediaUrls } from '../../../../shared/media-url';
@Component({ selector: 'app-property-card', standalone: true, imports: [RouterLink, IconComponent], templateUrl: './property-card.component.html', styleUrl: './property-card.component.css' })
export class PropertyCardComponent {
  property = input.required<PropertyCard>(); showFav = input(true);
  favToggle = output<PropertyCard>();
  index = signal(0);
  urls = computed(() => {
    const p = this.property() as unknown as Record<string, unknown>;
    const fromImages = mediaUrls(p['images'] as Img[] | undefined);
    if (fromImages.length) return fromImages;
    const cover = (p['cover_url'] ?? p['image_url'] ?? p['cover'] ?? p['main_image'] ?? p['thumbnail']) as string | undefined;
    return mediaUrls(cover ? [{ id: 0, url: cover }] : []);
  });
  current = computed(() => this.urls()[this.index()] ?? null);
  move(d: number, e: Event): void { e.preventDefault(); e.stopPropagation(); const n = this.urls().length; this.index.set((this.index() + d + n) % n); }
}
