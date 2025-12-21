import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Location, CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';

@Component({
    selector: 'app-consumo-mensual',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule
    ],
    templateUrl: './consumo-mensual.html'
})
export class ConsumoMensual implements OnInit {
    private fb = inject(FormBuilder);
    private http = inject(HttpClient);
    private router = inject(Router);
    private location = inject(Location);
    private authService = inject(AuthService);

    form!: FormGroup;
    loading = false;
    successMessage = '';
    errorMessage = '';

    private apiUrl = 'http://localhost:8000/api/consumo-mensual';

    meses = [
        { label: 'Enero', value: 1 },
        { label: 'Febrero', value: 2 },
        { label: 'Marzo', value: 3 },
        { label: 'Abril', value: 4 },
        { label: 'Mayo', value: 5 },
        { label: 'Junio', value: 6 },
        { label: 'Julio', value: 7 },
        { label: 'Agosto', value: 8 },
        { label: 'Septiembre', value: 9 },
        { label: 'Octubre', value: 10 },
        { label: 'Noviembre', value: 11 },
        { label: 'Diciembre', value: 12 }
    ];

    ngOnInit() {
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth() + 1;

        this.form = this.fb.group({
            fecha: [now.toISOString().split('T')[0], Validators.required],
            mes: [currentMonth, Validators.required],
            anio: [currentYear, Validators.required],

            // Sulfato de Aluminio
            sulfato_con: [null],
            sulfato_ing: [null],
            sulfato_guia: [''],
            sulfato_re: [null],

            // Cal
            cal_con: [null],
            cal_ing: [null],
            cal_guia: [''],

            // Hipoclorito de Calcio
            hipoclorito_con: [null],
            hipoclorito_ing: [null],
            hipoclorito_guia: [''],

            // Gas Licuado de Cloro
            cloro_gas_con: [null],
            cloro_gas_ing_bal: [null],
            cloro_gas_ing_bdg: [null],
            cloro_gas_guia: [''],
            cloro_gas_egre: [null],

            // Producción
            produccion_m3_dia: [null],

            // Resumen mensual
            inicio_mes_kg: [null],
            ingreso_mes_kg: [null],
            consumo_mes_kg: [null],
            egreso_mes_kg: [null],
            fin_mes_kg: [null],

            observaciones: [''],
            usuario_id: [this.authService.getUser()?.id || null]
        });
    }

    onSubmit() {
        if (this.form.valid) {
            this.loading = true;
            this.successMessage = '';
            this.errorMessage = '';

            this.http.post(this.apiUrl, this.form.value).subscribe({
                next: (response) => {
                    this.successMessage = 'Registro mensual guardado exitosamente';
                    this.loading = false;
                    setTimeout(() => {
                        this.successMessage = '';
                        // Optional: Navigate back or reset form
                    }, 3000);
                },
                error: (error) => {
                    this.errorMessage = 'Error al guardar el registro: ' + (error.error?.detail || error.message);
                    this.loading = false;
                }
            });
        } else {
            this.errorMessage = 'Por favor complete todos los campos requeridos';
            this.form.markAllAsTouched();
        }
    }

    goBack() {
        this.location.back();
    }
}
