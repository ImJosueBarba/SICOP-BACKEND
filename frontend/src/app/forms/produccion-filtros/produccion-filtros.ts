import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Location, CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-produccion-filtros',
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './produccion-filtros.html'
})
export class ProduccionFiltros implements OnInit {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private router = inject(Router);
  private location = inject(Location);
  private authService = inject(AuthService);

  form!: FormGroup;
  loading = false;
  successMessage = '';
  errorMessage = '';

  private apiUrl = 'http://localhost:8000/api/produccion-filtros';

  ngOnInit() {
    const now = new Date();
    const fecha = now.toISOString().split('T')[0];
    const hora = now.toTimeString().split(' ')[0].substring(0, 5);

    this.form = this.fb.group({
      fecha: [fecha, Validators.required],
      hora: [hora, Validators.required],
      filtro1_h: [null],
      filtro1_q: [null],
      filtro2_h: [null],
      filtro2_q: [null],
      filtro3_h: [null],
      filtro3_q: [null],
      filtro4_h: [null],
      filtro4_q: [null],
      filtro5_h: [null],
      filtro5_q: [null],
      filtro6_h: [null],
      filtro6_q: [null],
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
          this.successMessage = 'Registro guardado exitosamente';
          this.loading = false;
          setTimeout(() => {
            this.form.reset();
            const now = new Date();
            this.form.patchValue({
              fecha: now.toISOString().split('T')[0],
              hora: now.toTimeString().split(' ')[0].substring(0, 5),
              usuario_id: this.authService.getUser()?.id || null
            });
            this.successMessage = '';
          }, 2000);
        },
        error: (error) => {
          this.errorMessage = 'Error al guardar el registro: ' + (error.error?.detail || error.message);
          this.loading = false;
        }
      });
    }
  }

  goBack() {
    this.location.back();
  }
}
