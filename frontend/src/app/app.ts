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
  currentUrl: string = '';

  constructor() {
    // Inicializar con la URL actual
    this.currentUrl = this.router.url || '';
    
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.currentUrl = event.url;
    });
  }

  shouldShowLayout(): boolean {
    // Mostrar layout en todas las rutas excepto login
    return !this.currentUrl.includes('/login');
  }
}
