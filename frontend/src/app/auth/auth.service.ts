
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap, firstValueFrom } from 'rxjs';
import { jwtDecode } from 'jwt-decode';
import { RolSimple } from '../services/roles.service';

export interface User {
    id?: number;
    username: string;
    nombre: string;
    apellido: string;
    email?: string;
    telefono?: string;
    rol: RolSimple;  // Objeto rol completo
    rol_id: number;  // ID del rol
    activo: boolean;
    fecha_contratacion?: string;
    foto_perfil?: string;
    sub: string; // username in sub
    es_administrador?: boolean;
    es_operador?: boolean;
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
        
        try {
            // Set a timeout to ensure this always resolves
            await Promise.race([
                this.loadUserFromToken(),
                new Promise(resolve => setTimeout(resolve, 3000)) // 3 second timeout
            ]);
        } catch (error) {
            console.error('Error initializing auth:', error);
            // Always resolve, never block app initialization
        }
    }

    async login(username: string, password: string): Promise<void> {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        try {
            // Add timeout to login request
            const response = await Promise.race([
                firstValueFrom(
                    this.http.post<AuthResponse>(`${this.apiUrl}/token`, formData)
                ),
                new Promise<never>((_, reject) => 
                    setTimeout(() => reject(new Error('Login timeout - Backend no responde')), 10000)
                )
            ]);
            
            localStorage.setItem(this.tokenKey, response.access_token);
            
            // Load user directly without timeout after successful login
            const token = response.access_token;
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
                    rol_id: user.rol_id,
                    activo: user.activo,
                    fecha_contratacion: user.fecha_contratacion,
                    foto_perfil: user.foto_perfil,
                    sub: user.username,
                    es_administrador: user.es_administrador,
                    es_operador: user.es_operador
                });
            } catch (userError) {
                console.error('Error loading user after login:', userError);
                // Login was successful, user data will be loaded later by authGuard
            }
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
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
        if (!user || !user.rol) return false;
        
        // Verificar contra la categoria del rol
        if (allowedRoles.includes(user.rol.categoria)) {
            return true;
        }
        
        // Mantener compatibilidad con ADMIN como alias de ADMINISTRADOR
        if (user.rol.categoria === 'ADMINISTRADOR' && allowedRoles.includes('ADMIN')) {
            return true;
        }
        
        return false;
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
            
            // Fetch user details from /me endpoint without timeout
            const user = await firstValueFrom(
                this.http.get<any>(`${this.apiUrl}/me`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
            );
            
            if (user) {
                this.currentUserSubject.next({
                    id: user.id,
                    username: user.username,
                    nombre: user.nombre,
                    apellido: user.apellido,
                    email: user.email,
                    telefono: user.telefono,
                    rol: user.rol,
                    rol_id: user.rol_id,
                    activo: user.activo,
                    fecha_contratacion: user.fecha_contratacion,
                    foto_perfil: user.foto_perfil,
                    sub: user.username,
                    es_administrador: user.es_administrador,
                    es_operador: user.es_operador
                });
            }
        } catch (err: any) {
            console.error('Error loading user:', err);
            // Clear token if auth error
            if (err.status === 401) {
                localStorage.removeItem(this.tokenKey);
            }
            this.currentUserSubject.next(null);
            throw err;
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
