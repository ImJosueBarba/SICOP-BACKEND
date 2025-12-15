
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    // Check if there's a token
    if (!authService.isAuthenticated()) {
        return router.createUrlTree(['/login']);
    }

    // Get current user (should be loaded by APP_INITIALIZER)
    const user = authService.getUser();
    
    if (!user) {
        // Token exists but user failed to load, redirect to login
        return router.createUrlTree(['/login']);
    }

    // Check role-based access
    const requiredRoles = route.data?.['roles'] as Array<string>;
    if (requiredRoles && !authService.hasRole(requiredRoles)) {
        // Redirect to home if role doesn't match
        return router.createUrlTree(['/home']);
    }
    
    return true;
};
