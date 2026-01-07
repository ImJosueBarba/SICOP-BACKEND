import { Component, OnInit, inject, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../auth/auth.service';

interface QuickAction {
  title: string;
  description: string;
  icon: string;
  route: string;
  color: string;
  roles: string[];
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
  encapsulation: ViewEncapsulation.None
})
export class Home implements OnInit {
  private authService = inject(AuthService);
  
  currentUser: any = null;
  currentTime: string = '';
  
  quickActions: QuickAction[] = [
    {
      title: 'Control de Operación',
      description: 'Registrar parámetros operacionales',
      icon: 'pi-cog',
      route: '/forms/control-operacion',
      color: 'blue',
      roles: ['OPERADOR']
    },
    {
      title: 'Producción por Filtros',
      description: 'Registro de producción diaria',
      icon: 'pi-filter',
      route: '/forms/produccion-filtros',
      color: 'green',
      roles: ['OPERADOR']
    },
    {
      title: 'Registro de Reactivos',
      description: 'Ingresos y egresos de reactivos',
      icon: 'pi-circle',
      route: '/forms/control-cloro',
      color: 'purple',
      roles: ['OPERADOR']
    },
    {
      title: 'Monitoreo Fisicoquímico',
      description: 'Análisis de parámetros',
      icon: 'pi-chart-bar',
      route: '/forms/monitoreo-fisicoquimico',
      color: 'orange',
      roles: ['OPERADOR']
    },
    {
      title: 'Consumo Diario',
      description: 'Registro de químicos',
      icon: 'pi-shopping-cart',
      route: '/forms/consumo-quimicos',
      color: 'indigo',
      roles: ['OPERADOR']
    },
    {
      title: 'Consumo Mensual',
      description: 'Consolidado mensual',
      icon: 'pi-calendar',
      route: '/forms/consumo-mensual',
      color: 'pink',
      roles: ['OPERADOR']
    },
    {
      title: 'Gestión de Usuarios',
      description: 'Administrar usuarios del sistema',
      icon: 'pi-users',
      route: '/admin',
      color: 'red',
      roles: ['ADMINISTRADOR']
    }
  ];

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
    
    this.updateTime();
    setInterval(() => this.updateTime(), 1000);
  }

  updateTime() {
    const now = new Date();
    this.currentTime = now.toLocaleString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  hasAccess(roles: string[]): boolean {
    if (!this.currentUser) return false;
    return roles.includes(this.currentUser.rol);
  }

  getVisibleActions(): QuickAction[] {
    return this.quickActions.filter(action => this.hasAccess(action.roles));
  }
}
