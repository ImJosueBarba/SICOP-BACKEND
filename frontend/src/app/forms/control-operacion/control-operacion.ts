import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Location, CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-control-operacion',
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './control-operacion.html'
})
export class ControlOperacion implements OnInit {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private router = inject(Router);
  private location = inject(Location);
  private authService = inject(AuthService);
  
  form!: FormGroup;
  loading = false;
  successMessage = '';
  errorMessage = '';
  
  private apiUrl = 'http://localhost:8000/api/control-operacion';

  ngOnInit() {
    const now = new Date();
    const fecha = now.toISOString().split('T')[0];
    const hora = now.toTimeString().split(' ')[0].substring(0, 5);
    
    this.form = this.fb.group({
      fecha: [fecha, Validators.required],
      hora: [hora, Validators.required],
      turbedad_ac: [null],
      turbedad_at: [null],
      color: [''],
      ph_ac: [null],
      ph_sulf: [null],
      ph_at: [null],
      dosis_sulfato: [null],
      dosis_cal: [null],
      dosis_floergel: [null],
      ff: [null],
      clarificacion_is: [null],
      clarificacion_cs: [null],
      clarificacion_fs: [null],
      presion_psi: [null],
      presion_pre: [null],
      presion_pos: [null],
      cloro_residual: [null],
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
        next: () => {
          this.successMessage = '✓ Registro guardado exitosamente';
          this.loading = false;
          setTimeout(() => {
            this.form.reset();
            const now = new Date();
            this.form.patchValue({
              fecha: now.toISOString().split('T')[0],
              hora: now.toTimeString().split(' ')[0].substring(0, 5),
              usuario_id: this.authService.getUser()?.id || null
            });
          }, 2000);
        },
        error: (error) => {
          this.errorMessage = 'Error al guardar el registro: ' + (error.error?.detail || 'Error desconocido');
          this.loading = false;
        }
      });
    }
  }

  goBack() {
    this.location.back();
  }
}
