import { Component, inject } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { MainLayout } from './layout/main-layout/main-layout';
import { CommonModule } from '@angular/common';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, MainLayout, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private router = inject(Router);
  private currentUrl: string;

  constructor() {
    // Inicializar con la URL actual
    this.currentUrl = this.router.url;
    
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.currentUrl = event.url;
    });
  }

  shouldShowLayout(): boolean {
    // No mostrar layout en login o si la URL está vacía y vamos a redirigir a login
    return !!this.currentUrl && !this.currentUrl.includes('/login');
  }
}
