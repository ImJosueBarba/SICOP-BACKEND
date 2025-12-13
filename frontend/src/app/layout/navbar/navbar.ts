import { Component, OnInit, inject } from '@angular/core';
import { RouterModule, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar implements OnInit {
  private authService = inject(AuthService);
  private router = inject(Router);

  currentUser: any = null;
  mobileMenuOpen = false;
  openDropdowns = new Set<string>();

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
  }

  toggleMobile() {
    this.mobileMenuOpen = !this.mobileMenuOpen;
  }

  toggleDropdown(dropdown: string) {
    if (this.openDropdowns.has(dropdown)) {
      this.openDropdowns.delete(dropdown);
    } else {
      this.openDropdowns.add(dropdown);
    }
  }

  isDropdownOpen(dropdown: string): boolean {
    return this.openDropdowns.has(dropdown);
  }

  logout() {
    this.authService.logout();
  }
}

