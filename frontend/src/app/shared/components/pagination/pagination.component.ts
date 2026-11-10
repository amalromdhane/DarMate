import { Component, computed, input, output } from '@angular/core';
@Component({ selector: 'app-pagination', standalone: true, templateUrl: './pagination.component.html', styleUrl: './pagination.component.css' })
export class PaginationComponent {
  page = input.required<number>(); total = input.required<number>(); size = input.required<number>();
  pageChange = output<number>();
  pages = computed(() => Math.max(1, Math.ceil(this.total() / this.size())));
}
