import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Table, TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { Select } from 'primeng/select';
import { PasswordModule } from 'primeng/password';
import { ToastModule } from 'primeng/toast';
import { ToolbarModule } from 'primeng/toolbar';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { MessageService, ConfirmationService } from 'primeng/api';
import { UsuariosService, Usuario } from '../../../services/usuarios.service';
import { RolesService, RolSimple } from '../../../services/roles.service';
import { TagModule } from 'primeng/tag';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { CardModule } from 'primeng/card';
import { TooltipModule } from 'primeng/tooltip';

@Component({
    selector: 'app-user-management',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        TableModule,
        ButtonModule,
        DialogModule,
        InputTextModule,
        Select,
        PasswordModule,
        ToastModule,
        ToolbarModule,
        ConfirmDialogModule,
        TagModule,
        IconFieldModule,
        InputIconModule,
        CardModule,
        TooltipModule
    ],
    providers: [MessageService, ConfirmationService],
    templateUrl: './user-management.html',
    styleUrl: './user-management.css'
})
export class UserManagement implements OnInit {
    private usuariosService = inject(UsuariosService);
    private rolesService = inject(RolesService);
    private messageService = inject(MessageService);
    private confirmationService = inject(ConfirmationService);
    private fb = inject(FormBuilder);

    usuarios: Usuario[] = [];
    usuarioDialog: boolean = false;
    form!: FormGroup;
    submitted: boolean = false;
    isEditMode: boolean = false;
    loading: boolean = false;
    rolesLoading: boolean = false;
    dialogHeaderClass: string = '';
    dialogHeaderStyle: any = {};

    // Roles dinámicos desde el backend
    roles: { label: string, value: number }[] = [];
    rolesData: RolSimple[] = [];

    ngOnInit() {
        this.initForm();
        this.loadRoles();
        this.loadUsuarios();
    }

    initForm() {
        this.form = this.fb.group({
            id: [null],
            nombre: ['', [Validators.required, Validators.minLength(2)]],
            apellido: ['', [Validators.required, Validators.minLength(2)]],
            email: ['', [Validators.email]],
            telefono: [''],
            username: ['', [Validators.required, Validators.minLength(3)]],
            password: [''],
            rol_id: [null, Validators.required],
            activo: [true],
            fecha_contratacion: ['']
        });
    }

    loadRoles() {
        this.rolesLoading = true;
        this.rolesService.getRoles(true).subscribe({
            next: (data) => {
                this.rolesData = data;
                // Convertir roles a formato para el dropdown
                this.roles = data.map(rol => ({
                    label: rol.nombre,
                    value: rol.id
                }));
                this.rolesLoading = false;
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Error al cargar roles'
                });
                this.rolesLoading = false;
            }
        });
    }

    loadUsuarios() {
        this.loading = true;
        this.usuariosService.getUsuarios().subscribe({
            next: (data) => {
                // Crear un nuevo array para forzar la detección de cambios
                this.usuarios = [...data];
                this.loading = false;
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Error al cargar usuarios'
                });
                this.loading = false;
            }
        });
    }

    openNew() {
        // Por defecto usar el primer rol de operador (generalmente id=6: Operador de Planta)
        const operadorRol = this.rolesData.find(r => r.categoria === 'OPERADOR');
        this.form.reset({
            rol_id: operadorRol?.id || null,
            activo: true
        });
        this.form.get('password')?.setValidators([Validators.required, Validators.minLength(6)]);
        this.form.get('password')?.updateValueAndValidity();
        this.submitted = false;
        this.isEditMode = false;
        this.dialogHeaderClass = 'dialog-new';
        this.dialogHeaderStyle = {
            'background': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
            'color': 'white'
        };
        console.log('Opening new user dialog, class:', this.dialogHeaderClass);
        this.usuarioDialog = true;
    }

    editUsuario(usuario: Usuario) {
        this.form.patchValue({
            id: usuario.id,
            nombre: usuario.nombre,
            apellido: usuario.apellido,
            email: usuario.email,
            telefono: usuario.telefono,
            username: usuario.username,
            rol_id: usuario.rol_id,
            activo: usuario.activo,
            fecha_contratacion: usuario.fecha_contratacion
        });
        this.form.get('password')?.clearValidators();
        this.form.get('password')?.updateValueAndValidity();
        this.submitted = false;
        this.isEditMode = true;
        this.dialogHeaderClass = 'dialog-edit';
        this.dialogHeaderStyle = {
            'background': 'linear-gradient(135deg, #f5af19 0%, #f12711 100%)',
            'color': 'white'
        };
        console.log('Opening edit user dialog, class:', this.dialogHeaderClass);
        this.usuarioDialog = true;
    }

    deleteUsuario(usuario: Usuario) {
        this.confirmationService.confirm({
            message: `¿Está seguro de desactivar al usuario ${usuario.nombre_completo}?`,
            header: 'Confirmar',
            icon: 'pi pi-exclamation-triangle',
            acceptLabel: 'Sí',
            rejectLabel: 'No',
            accept: () => {
                this.usuariosService.deleteUsuario(usuario.id!).subscribe({
                    next: () => {
                        this.messageService.add({
                            severity: 'success',
                            summary: 'Éxito',
                            detail: 'Usuario desactivado correctamente'
                        });
                        this.loadUsuarios();
                    },
                    error: (error) => {
                        this.messageService.add({
                            severity: 'error',
                            summary: 'Error',
                            detail: error.error?.detail || 'Error al desactivar usuario'
                        });
                    }
                });
            }
        });
    }

    activarUsuario(usuario: Usuario) {
        this.confirmationService.confirm({
            message: `¿Está seguro de activar al usuario ${usuario.nombre_completo}?`,
            header: 'Confirmar',
            icon: 'pi pi-question-circle',
            acceptLabel: 'Sí',
            rejectLabel: 'No',
            accept: () => {
                this.usuariosService.activarUsuario(usuario.id!).subscribe({
                    next: () => {
                        this.messageService.add({
                            severity: 'success',
                            summary: 'Éxito',
                            detail: 'Usuario activado correctamente'
                        });
                        this.loadUsuarios();
                    },
                    error: (error) => {
                        this.messageService.add({
                            severity: 'error',
                            summary: 'Error',
                            detail: 'Error al activar usuario'
                        });
                    }
                });
            }
        });
    }

    hideDialog() {
        this.usuarioDialog = false;
        this.submitted = false;
    }

    saveUsuario() {
        this.submitted = true;

        if (this.form.invalid) {
            return;
        }

        const usuario = this.form.value;

        if (this.isEditMode) {
            // Modo edición
            const updateData: any = {
                nombre: usuario.nombre,
                apellido: usuario.apellido,
                username: usuario.username,
                rol_id: usuario.rol_id,
                activo: usuario.activo
            };

            // Solo agregar campos opcionales si tienen valor
            if (usuario.email && usuario.email.trim() !== '') {
                updateData.email = usuario.email;
            }
            if (usuario.telefono && usuario.telefono.trim() !== '') {
                updateData.telefono = usuario.telefono;
            }
            if (usuario.fecha_contratacion && usuario.fecha_contratacion.trim() !== '') {
                updateData.fecha_contratacion = usuario.fecha_contratacion;
            }

            // Solo incluir password si se proporcionó uno nuevo
            if (usuario.password && usuario.password.trim() !== '') {
                updateData.password = usuario.password;
            }

            this.usuariosService.updateUsuario(usuario.id, updateData).subscribe({
                next: (response) => {
                    this.hideDialog();
                    this.messageService.add({
                        severity: 'success',
                        summary: 'Éxito',
                        detail: 'Usuario actualizado correctamente'
                    });
                    // Recargar después de cerrar el diálogo y mostrar el mensaje
                    setTimeout(() => {
                        this.loadUsuarios();
                    }, 100);
                },
                error: (error) => {
                    this.messageService.add({
                        severity: 'error',
                        summary: 'Error',
                        detail: error.error?.detail || 'Error al actualizar usuario'
                    });
                }
            });
        } else {
            // Modo creación
            delete usuario.id;
            this.usuariosService.createUsuario(usuario).subscribe({
                next: () => {
                    this.messageService.add({
                        severity: 'success',
                        summary: 'Éxito',
                        detail: 'Usuario creado correctamente'
                    });
                    this.loadUsuarios();
                    this.hideDialog();
                },
                error: (error) => {
                    this.messageService.add({
                        severity: 'error',
                        summary: 'Error',
                        detail: error.error?.detail || 'Error al crear usuario'
                    });
                }
            });
        }
    }

    onGlobalFilter(table: Table, event: Event) {
        table.filterGlobal((event.target as HTMLInputElement).value, 'contains');
    }

    getRolSeverity(usuario: Usuario): 'success' | 'info' | 'warn' | 'danger' {
        if (!usuario.rol) return 'info';
        
        switch (usuario.rol.categoria) {
            case 'ADMINISTRADOR':
                return 'danger';
            case 'JEFATURA':
                return 'warn';
            case 'SUPERVISOR':
                return 'info';
            case 'OPERADOR':
                return 'info';
            default:
                return 'info';
        }
    }

    getEstadoSeverity(activo: boolean): 'success' | 'danger' {
        return activo ? 'success' : 'danger';
    }
}
