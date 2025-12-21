import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Location, CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-consumo-quimicos',
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './consumo-quimicos.html',
})
export class ConsumoQuimicos implements OnInit {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private router = inject(Router);
  private location = inject(Location);
  private authService = inject(AuthService);
  
  form!: FormGroup;
  loading = false;
  successMessage = '';
  errorMessage = '';
  quimicos: any[] = [];
  
  private apiUrl = 'http://localhost:8000/api/consumo-diario';
  private quimicosUrl = 'http://localhost:8000/api/quimicos';

  ngOnInit() {
    this.loadQuimicos();
    
    const now = new Date();
    const fecha = now.toISOString().split('T')[0];
    const hora = now.toTimeString().split(' ')[0].substring(0, 5);
    
    this.form = this.fb.group({
      fecha: [fecha, Validators.required],
      quimico_id: [null, Validators.required],
      bodega_ingresa: [null],
      bodega_egresa: [null],
      bodega_stock: [null],
      tanque1_hora: [hora],
      tanque1_lectura_inicial: [null],
      tanque1_lectura_final: [null],
      tanque1_consumo: [null],
      tanque2_hora: [null],
      tanque2_lectura_inicial: [null],
      tanque2_lectura_final: [null],
      tanque2_consumo: [null],
      total_consumo: [null],
      observaciones: [''],
      usuario_id: [this.authService.getUser()?.id || null]
    });
  }

  loadQuimicos() {
    this.http.get<any[]>(this.quimicosUrl).subscribe({
      next: (data) => {
        this.quimicos = data.map(q => ({ label: q.nombre, value: q.id }));
      },
      error: (error) => {
        console.error('Error loading chemicals:', error);
      }
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
              tanque1_hora: now.toTimeString().split(' ')[0].substring(0, 5),
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
