import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-control-operacion-reporte',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './control-operacion-reporte.html',
  styleUrl: './control-operacion-reporte.css'
})
export class ControlOperacionReporte implements OnInit {
  registros: any[] = [];
  loading = false;
  error: string | null = null;
  
  // Filtros
  fechaInicio: string = '';
  fechaFin: string = '';
  
  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.cargarRegistros();
  }

  cargarRegistros() {
    this.loading = true;
    this.error = null;
    
    let url = 'http://localhost:8000/api/control-operacion/';
    const params: string[] = [];
    
    if (this.fechaInicio) {
      params.push(`fecha_inicio=${this.fechaInicio}`);
    }
    if (this.fechaFin) {
      params.push(`fecha_fin=${this.fechaFin}`);
    }
    
    if (params.length > 0) {
      url += '?' + params.join('&');
    }

    this.http.get<any[]>(url).subscribe({
      next: (data) => {
        this.registros = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Error al cargar los registros';
        console.error(err);
        this.loading = false;
      }
    });
  }

  filtrar() {
    this.cargarRegistros();
  }

  limpiarFiltros() {
    this.fechaInicio = '';
    this.fechaFin = '';
    this.cargarRegistros();
  }

  async exportarExcel() {
    if (this.registros.length === 0) {
      alert('No hay datos para exportar');
      return;
    }

    // Obtener la fecha del primer registro
    const fecha = this.registros[0]?.fecha || new Date().toISOString().split('T')[0];
    
    // Llamar al endpoint del backend
    const url = `http://localhost:8000/api/control-operacion/exportar-excel/fecha/${fecha}`;
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Error al generar el archivo Excel');
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `control_operacion_${fecha}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Error al exportar:', error);
      alert('Error al exportar el archivo Excel');
    }
  }
}
