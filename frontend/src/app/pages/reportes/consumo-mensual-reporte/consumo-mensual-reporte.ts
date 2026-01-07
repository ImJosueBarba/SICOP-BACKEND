import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import * as ExcelJS from 'exceljs';

@Component({
  selector: 'app-consumo-mensual-reporte',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './consumo-mensual-reporte.html',
  styleUrl: './consumo-mensual-reporte.css'
})
export class ConsumoMensualReporte implements OnInit {
  registros: any[] = [];
  loading = false;
  error: string | null = null;
  
  mesSeleccionado: string = '';
  anioSeleccionado: string = '';
  quimicoSeleccionado: string = '';
  
  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.cargarRegistros();
  }

  cargarRegistros() {
    this.loading = true;
    this.error = null;
    
    let url = 'http://localhost:8000/api/consumo-mensual/';
    const params: string[] = [];
    
    if (this.mesSeleccionado) {
      params.push(`mes=${this.mesSeleccionado}`);
    }
    if (this.anioSeleccionado) {
      params.push(`anio=${this.anioSeleccionado}`);
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
    this.mesSeleccionado = '';
    this.anioSeleccionado = '';
    this.quimicoSeleccionado = '';
    this.cargarRegistros();
  }

  async exportarExcel() {
    if (this.registros.length === 0) {
      alert('No hay datos para exportar');
      return;
    }

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Consumo Mensual');

    worksheet.columns = [
      { header: 'Fecha', key: 'fecha', width: 12 },
      { header: 'Químico', key: 'quimico', width: 20 },
      { header: 'Mes', key: 'mes', width: 10 },
      { header: 'Año', key: 'anio', width: 10 },
      { header: 'Consumo (kg)', key: 'consumo_kg', width: 14 },
      { header: 'Ingreso (kg)', key: 'ingreso_kg', width: 14 },
      { header: 'Guía #', key: 'guia_numero', width: 12 },
      { header: 'Remanente (kg)', key: 'remanente_kg', width: 15 },
      { header: 'Producción (m³/día)', key: 'produccion_m3_dia', width: 18 }
    ];

    this.registros.forEach(reg => {
      worksheet.addRow({
        fecha: reg.fecha,
        quimico: reg.quimico?.nombre || reg.quimico_id,
        mes: reg.mes,
        anio: reg.anio,
        consumo_kg: reg.consumo_kg,
        ingreso_kg: reg.ingreso_kg,
        guia_numero: reg.guia_numero,
        remanente_kg: reg.remanente_kg,
        produccion_m3_dia: reg.produccion_m3_dia
      });
    });

    worksheet.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };
    worksheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4472C4' }
    };

    const buffer = await workbook.xlsx.writeBuffer();
    const fecha = new Date().toISOString().split('T')[0];
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `consumo_mensual_${fecha}.xlsx`;
    a.click();
    window.URL.revokeObjectURL(url);
  }
}
