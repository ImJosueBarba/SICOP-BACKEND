import { Component, OnInit, inject, signal, ViewEncapsulation } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';

interface MenuItem {
  label: string;
  icon: string;
  route?: string;
  roles?: string[];
  children?: MenuItem[];
  expanded?: boolean;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css',
  encapsulation: ViewEncapsulation.None
})
export class Sidebar implements OnInit {
  private authService = inject(AuthService);
  private router = inject(Router);

  currentUser: any = null;
  sidebarCollapsed = signal(false);
  
  menuItems: MenuItem[] = [
    {
      label: 'Inicio',
      icon: 'pi-home',
      route: '/home',
      roles: ['ADMINISTRADOR', 'OPERADOR']
    },
    {
      label: 'Gestión de Usuarios',
      icon: 'pi-users',
      route: '/admin',
      roles: ['ADMINISTRADOR']
    },
    {
      label: 'Logs de Auditoría',
      icon: 'pi-history',
      route: '/logs',
      roles: ['ADMINISTRADOR']
    },
    {
      label: 'Matrices',
      icon: 'pi-table',
      roles: ['OPERADOR'],
      children: [
        {
          label: 'Control de Operación',
          icon: 'pi-cog',
          route: '/forms/control-operacion'
        },
        {
          label: 'Registro de Reactivos',
          icon: 'pi-circle',
          route: '/forms/control-cloro'
        },
        {
          label: 'Monitoreo Fisicoquímico',
          icon: 'pi-chart-bar',
          route: '/forms/monitoreo-fisicoquimico'
        }
      ],
      expanded: false
    },
    {
      label: 'Producción',
      icon: 'pi-chart-line',
      roles: ['OPERADOR'],
      children: [
        {
          label: 'Producción por Filtros',
          icon: 'pi-filter',
          route: '/forms/produccion-filtros'
        },
        {
          label: 'Consumo Diario',
          icon: 'pi-shopping-cart',
          route: '/forms/consumo-quimicos'
        },
        {
          label: 'Consumo Mensual',
          icon: 'pi-calendar',
          route: '/forms/consumo-mensual'
        }
      ],
      expanded: false
    },
    {
      label: 'Reportes',
      icon: 'pi-file-excel',
      roles: ['OPERADOR'],
      children: [
        {
          label: 'Control de Operación',
          icon: 'pi-eye',
          route: '/reportes/control-operacion'
        },
        {
          label: 'Registro de Reactivos',
          icon: 'pi-eye',
          route: '/reportes/cloro-libre'
        },
        {
          label: 'Monitoreo Fisicoquímico',
          icon: 'pi-eye',
          route: '/reportes/monitoreo-fisicoquimico'
        },
        {
          label: 'Producción por Filtros',
          icon: 'pi-eye',
          route: '/reportes/produccion-filtros'
        },
        {
          label: 'Consumo Diario',
          icon: 'pi-eye',
          route: '/reportes/consumo-diario'
        },
        {
          label: 'Consumo Mensual',
          icon: 'pi-eye',
          route: '/reportes/consumo-mensual'
        }
      ],
      expanded: false
    }
  ];

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
  }

  toggleSidebar() {
    this.sidebarCollapsed.update(val => !val);
  }

  toggleMenu(item: MenuItem) {
    if (item.children) {
      item.expanded = !item.expanded;
    }
  }

  hasAccess(roles?: string[]): boolean {
    if (!roles || roles.length === 0) return true;
    if (!this.currentUser || !this.currentUser.rol) return false;
    
    // Verificar contra la categoría del rol
    return roles.includes(this.currentUser.rol.categoria);
  }

  isActive(route?: string): boolean {
    if (!route) return false;
    return this.router.url === route || this.router.url.startsWith(route + '/');
  }

  hasActiveChild(item: MenuItem): boolean {
    if (!item.children) return false;
    return item.children.some(child => this.isActive(child.route));
  }
}
