import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Location, CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-monitoreo-fisicoquimico',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './monitoreo-fisicoquimico.html'
})
export class MonitoreoFisicoquimico implements OnInit {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private location = inject(Location);
  private authService = inject(AuthService);
  form!: FormGroup;
  loading = false;
  successMessage = '';
  errorMessage = '';
  private apiUrl = 'http://localhost:8000/api/monitoreo-fisicoquimico';

  ngOnInit() {
    const now = new Date();
    this.form = this.fb.group({
      fecha: [now.toISOString().split('T')[0], Validators.required],
      hora: [now.toTimeString().split(' ')[0].substring(0, 5), Validators.required],
      muestra_numero: [1, [Validators.required, Validators.min(1), Validators.max(3)]],
      lugar_agua_cruda: [''],
      lugar_agua_tratada: [''],
      ac_ph: [null],
      ac_ce: [null],
      ac_tds: [null],
      ac_salinidad: [null],
      ac_temperatura: [null],
      at_ph: [null],
      at_ce: [null],
      at_tds: [null],
      at_salinidad: [null],
      at_temperatura: [null],
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
