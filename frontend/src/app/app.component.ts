import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './layout/header/header.component';
import { FooterComponent } from './layout/footer/footer.component';
import { ToastComponent } from './shared/components/toast/toast.component';
@Component({ selector: 'app-root', standalone: true, imports: [RouterOutlet, HeaderComponent, FooterComponent, ToastComponent], templateUrl: './app.component.html', styleUrl: './app.component.css' })
export class AppComponent {}
