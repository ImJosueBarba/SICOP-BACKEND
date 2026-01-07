
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = async (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    // Check if there's a token
    if (!authService.isAuthenticated()) {
        return router.createUrlTree(['/login']);
    }

    // Get current user, load if not present
    let user = authService.getUser();
    
    if (!user) {
        // Try to load user from token
        try {
            await authService.loadUserFromToken();
            user = authService.getUser();
        } catch (error) {
            // If loading fails, redirect to login
            return router.createUrlTree(['/login']);
        }
        
        if (!user) {
            return router.createUrlTree(['/login']);
        }
    }

    // Check role-based access
    const requiredRoles = route.data?.['roles'] as Array<string>;
    if (requiredRoles && !authService.hasRole(requiredRoles)) {
        // Redirect to home if role doesn't match
        return router.createUrlTree(['/home']);
    }
    
    return true;
};
