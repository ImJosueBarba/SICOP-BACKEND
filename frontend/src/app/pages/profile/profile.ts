import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Card } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { InputText } from 'primeng/inputtext';
import { FloatLabel } from 'primeng/floatlabel';
import { Message } from 'primeng/message';
import { FileUpload, FileUploadModule } from 'primeng/fileupload';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    Card,
    ButtonModule,
    InputText,
    FloatLabel,
    Message,
    FileUploadModule
  ],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private router = inject(Router);
  private authService = inject(AuthService);

  profileForm!: FormGroup;
  currentUser: any = null;
  loading = false;
  successMessage = '';
  errorMessage = '';
  profileImage: string | null = null;
  selectedFile: File | null = null;
  
  private apiUrl = 'http://localhost:8000/api';

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (user) {
        this.profileImage = user.foto_perfil ? `${this.apiUrl.replace('/api', '')}${user.foto_perfil}` : null;
        this.initForm();
      }
    });
  }

  initForm() {
    this.profileForm = this.fb.group({
      nombre: [this.currentUser?.nombre || '', [Validators.required]],
      email: [this.currentUser?.email || '', [Validators.required, Validators.email]],
      usuario: [{ value: this.currentUser?.username || '', disabled: true }],
      rol: [{ value: this.currentUser?.rol?.nombre || '', disabled: true }]
    });
  }

  onFileSelect(event: any) {
    const file = event.files[0];
    if (file) {
      this.selectedFile = file;
      
      // Preview image
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.profileImage = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  onRemoveImage() {
    this.selectedFile = null;
    this.profileImage = this.currentUser?.foto_perfil ? `${this.apiUrl.replace('/api', '')}${this.currentUser.foto_perfil}` : null;
  }

  async onSubmit() {
    if (this.profileForm.invalid) {
      this.errorMessage = 'Por favor completa todos los campos correctamente';
      return;
    }

    this.loading = true;
    this.successMessage = '';
    this.errorMessage = '';

    try {
      const formData = new FormData();
      formData.append('nombre', this.profileForm.get('nombre')?.value);
      formData.append('email', this.profileForm.get('email')?.value);
      
      if (this.selectedFile) {
        formData.append('foto_perfil', this.selectedFile);
      }

      const response = await this.http.put(
        `${this.apiUrl}/usuarios/${this.currentUser.id}`,
        formData
      ).toPromise();

      this.successMessage = 'Perfil actualizado exitosamente';
      
      // Recargar la página después de un momento para actualizar el usuario
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error: any) {
      this.errorMessage = error.error?.detail || 'Error al actualizar el perfil';
      setTimeout(() => {
        this.errorMessage = '';
      }, 5000);
    } finally {
      this.loading = false;
    }
  }

  goBack() {
    this.router.navigate(['/home']);
  }
}
