
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap, firstValueFrom } from 'rxjs';
import { jwtDecode } from 'jwt-decode';

export interface User {
    id?: number;
    username: string;
    nombre: string;
    apellido: string;
    email?: string;
    telefono?: string;
    rol: 'ADMINISTRADOR' | 'OPERADOR' | 'ADMIN';
    activo: boolean;
    fecha_contratacion?: string;
    foto_perfil?: string;
    sub: string; // username in sub
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private http = inject(HttpClient);
    private router = inject(Router);

    private apiUrl = 'http://localhost:8000/api/auth';
    private tokenKey = 'auth_token';

    private currentUserSubject = new BehaviorSubject<User | null>(null);
    public currentUser$ = this.currentUserSubject.asObservable();
    
    private isInitialized = false;

    constructor() {
        // Don't load user here, wait for initializeAuth()
    }
    
    async initializeAuth(): Promise<void> {
        if (this.isInitialized) return;
        this.isInitialized = true;
        await this.loadUserFromToken();
    }

    login(username: string, password: string): Observable<AuthResponse> {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        return this.http.post<AuthResponse>(`${this.apiUrl}/token`, formData).pipe(
            tap(response => {
                localStorage.setItem(this.tokenKey, response.access_token);
                this.loadUserFromToken();
            })
        );
    }

    logout() {
        localStorage.removeItem(this.tokenKey);
        this.currentUserSubject.next(null);
        this.router.navigate(['/login']);
    }

    getToken(): string | null {
        return localStorage.getItem(this.tokenKey);
    }

    isAuthenticated(): boolean {
        return !!this.getToken();
    }

    hasRole(allowedRoles: string[]): boolean {
        const user = this.currentUserSubject.value;
        if (!user) return false;
        // Allow ADMIN as alias for ADMINISTRADOR for backward compatibility
        if (user.rol === 'ADMINISTRADOR' && allowedRoles.includes('ADMIN')) {
            return true;
        }
        return allowedRoles.includes(user.rol);
    }

    getUser(): User | null {
        return this.currentUserSubject.value;
    }

    async loadUserFromToken(): Promise<void> {
        const token = this.getToken();
        if (!token) {
            this.currentUserSubject.next(null);
            return;
        }
        
        try {
            const decoded: any = jwtDecode(token);
            
            // Check if token is expired
            const currentTime = Math.floor(Date.now() / 1000);
            if (decoded.exp && decoded.exp < currentTime) {
                console.log('Token expired, logging out');
                this.logout();
                return;
            }
            
            // Fetch user details from /me endpoint
            try {
                const user = await firstValueFrom(
                    this.http.get<any>(`${this.apiUrl}/me`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    })
                );
                
                this.currentUserSubject.next({
                    id: user.id,
                    username: user.username,
                    nombre: user.nombre,
                    apellido: user.apellido,
                    email: user.email,
                    telefono: user.telefono,
                    rol: user.rol,
                    activo: user.activo,
                    fecha_contratacion: user.fecha_contratacion,
                    foto_perfil: user.foto_perfil,
                    sub: user.username
                });
            } catch (err: any) {
                console.error('Error loading user:', err);
                // Only logout if it's an authentication error (401)
                if (err.status === 401) {
                    this.logout();
                } else {
                    // For other errors, keep the session but don't set user
                    console.warn('Error fetching user data, but keeping token');
                    this.currentUserSubject.next(null);
                }
            }

        } catch (e) {
            console.error('Error decoding token:', e);
            this.logout();
        }
    }

    updateCurrentUser(user: any) {
        const currentUser = this.currentUserSubject.value;
        if (currentUser) {
            this.currentUserSubject.next({
                ...currentUser,
                nombre: user.nombre,
                email: user.email,
                foto_perfil: user.foto_perfil
            });
        }
    }
}
