import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-consumo-diario-reporte',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './consumo-diario-reporte.html',
  styleUrl: './consumo-diario-reporte.css'
})
export class ConsumoDiarioReporte implements OnInit {
  registros: any[] = [];
  loading = false;
  error: string | null = null;
  
  fechaInicio: string = '';
  fechaFin: string = '';
  quimicoSeleccionado: string = '';
  fechaExportar: string = '';
  
  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.cargarRegistros();
  }

  cargarRegistros() {
    this.loading = true;
    this.error = null;
    
    let url = 'http://localhost:8000/api/consumo-diario/';
    const params: string[] = [];
    
    if (this.fechaInicio) {
      params.push(`fecha_inicio=${this.fechaInicio}`);
    }
    if (this.fechaFin) {
      params.push(`fecha_fin=${this.fechaFin}`);
    }
    if (this.quimicoSeleccionado) {
      params.push(`quimico=${this.quimicoSeleccionado}`);
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
    this.quimicoSeleccionado = '';
    this.cargarRegistros();
  }

  async exportarExcel() {
    if (!this.fechaExportar) {
      alert('Por favor seleccione una fecha para exportar');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/consumo-diario/exportar-excel/fecha/${this.fechaExportar}`);
      
      if (!response.ok) {
        throw new Error('Error al exportar');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `consumo_diario_${this.fechaExportar}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error:', error);
      alert('Error al exportar el archivo');
    }
  }
}
