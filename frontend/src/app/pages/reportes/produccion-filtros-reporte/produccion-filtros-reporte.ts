import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-produccion-filtros-reporte',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './produccion-filtros-reporte.html',
  styleUrl: './produccion-filtros-reporte.css'
})
export class ProduccionFiltrosReporte implements OnInit {
  registros: any[] = [];
  loading = false;
  error: string | null = null;
  
  fechaInicio: string = '';
  fechaFin: string = '';
  filtroFecha: string = ''; // Para exportar (YYYY-MM-DD)
  
  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.cargarRegistros();
  }

  cargarRegistros() {
    this.loading = true;
    this.error = null;
    
    let url = 'http://localhost:8000/api/produccion-filtros/';
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
    if (!this.filtroFecha) {
      alert('Seleccione una fecha para exportar');
      return;
    }

    try {
      const fecha = this.filtroFecha;
      
      const response = await fetch(`http://localhost:8000/api/produccion-filtros/exportar-excel/fecha/${fecha}`);
      
      if (!response.ok) {
        throw new Error('Error al generar el Excel');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `produccion_filtros_${fecha}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error al exportar:', error);
      alert('Error al exportar a Excel');
    }
  }
}
