import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Location, CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-control-cloro',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './control-cloro.html'
})
export class ControlCloro implements OnInit {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private location = inject(Location);
  private authService = inject(AuthService);
  form!: FormGroup;
  loading = false;
  successMessage = '';
  errorMessage = '';
  private apiUrl = 'http://localhost:8000/api/control-cloro';

  ngOnInit() {
    const now = new Date();
    this.form = this.fb.group({
      fecha_mes: [now.toISOString().split('T')[0], Validators.required],
      documento_soporte: [''],
      proveedor_solicitante: [''],
      codigo: [''],
      especificacion: [''],
      cantidad_entra: [null],
      cantidad_sale: [null],
      cantidad_saldo: [null],
      observaciones: [''],
      usuario_id: [this.authService.getUser()?.id || null]
    });
  }

  onSubmit() {
    if (this.form.valid) {
      this.loading = true;
      this.http.post(this.apiUrl, this.form.value).subscribe({
        next: () => {
          this.successMessage = 'Registro guardado exitosamente';
          this.loading = false;
          setTimeout(() => { this.form.reset(); this.ngOnInit(); this.successMessage = ''; }, 2000);
        },
        error: (error) => {
          this.errorMessage = 'Error: ' + (error.error?.detail || error.message);
          this.loading = false;
        }
      });
    }
  }

  goBack() { this.location.back(); }
}
