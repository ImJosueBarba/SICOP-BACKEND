"""
Script rápido para generar datos de entrenamiento ML
Genera 120 días de datos operacionales completos
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime, timedelta, time, date
from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models.control_operacion import ControlOperacion
from models.consumo_quimico_mensual import ConsumoQuimicoMensual
from models.monitoreo_fisicoquimico import MonitoreoFisicoquimico
from models.produccion_filtro import ProduccionFiltro
import random

def generate_training_data():
    db = SessionLocal()
    
    try:
        print("🔄 Limpiando datos anteriores...")
        db.query(ControlOperacion).delete()
        db.query(MonitoreoFisicoquimico).delete()
        db.query(ProduccionFiltro).delete()
        db.commit()
        print("✅ Datos anteriores eliminados\n")
        
        print("📊 Generando 120 días de datos operacionales...")
        
        # Fecha final: hoy
        end_date = datetime.now().date()
        # Fecha inicial: 120 días atrás
        start_date = end_date - timedelta(days=120)
        
        control_records = []
        fisico_records = []
        produccion_records = []
        current_date = start_date
        record_count = 0
        
        # Generar datos día por día
        while current_date <= end_date:
            # 3 lecturas operacionales por día (mañana, tarde, noche)
            for hora_str, hora_obj in [('08:00:00', time(8, 0, 0)), ('14:00:00', time(14, 0, 0)), ('20:00:00', time(20, 0, 0))]:
                # Generar valores realistas con variación
                turbedad_ac = round(random.uniform(8, 35), 2)
                turbedad_at = round(random.uniform(0.1, 0.7), 2)
                ph_ac = round(random.uniform(6.5, 8.2), 2)
                ph_at = round(random.uniform(6.8, 7.8), 2)
                cloro_residual = round(random.uniform(0.4, 1.8), 2)
                presion_psi = round(random.uniform(35, 65), 1)
                
                # Dosis correlacionadas con turbedad
                dosis_sulfato = round(turbedad_ac * 2.8 + random.uniform(-5, 5), 2)
                dosis_cal = round(turbedad_ac * 0.8 + random.uniform(-2, 2), 2)
                dosis_floergel = round(turbedad_ac * 0.15 + random.uniform(-0.5, 0.5), 2)
                
                control = ControlOperacion(
                    fecha=current_date,
                    hora=hora_obj,
                    turbedad_ac=turbedad_ac,
                    turbedad_at=turbedad_at,
                    color='Claro',
                    ph_ac=ph_ac,
                    ph_sulf=round(ph_ac - 0.3, 2),
                    ph_at=ph_at,
                    dosis_sulfato=dosis_sulfato,
                    dosis_cal=dosis_cal,
                    dosis_floergel=dosis_floergel,
                    ff=round(random.uniform(2.5, 4.5), 1),
                    clarificacion_is=round(random.uniform(1.0, 3.0), 1),
                    clarificacion_cs=round(random.uniform(0.5, 2.0), 1),
                    clarificacion_fs=round(random.uniform(0.2, 1.0), 1),
                    presion_psi=presion_psi,
                    presion_pre=round(presion_psi * 0.6, 1),
                    presion_pos=round(presion_psi * 0.4, 1),
                    presion_total=round(presion_psi * 3, 1),
                    cloro_residual=cloro_residual,
                    observaciones=f'Lectura {hora_str}'
                )
                control_records.append(control)
                record_count += 1
            
            # 1 lectura fisicoquímica por día
            fisico = MonitoreoFisicoquimico(
                fecha=current_date,
                muestra_numero=1,
                hora=time(10, 0, 0),
                lugar_agua_cruda="Toma Principal",
                lugar_agua_tratada="Salida Planta",
                ac_ph=round(random.uniform(6.5, 8.2), 2),
                ac_ce=round(random.uniform(400, 500), 1),
                ac_tds=round(random.uniform(250, 320), 1),
                ac_salinidad=round(random.uniform(0.2, 0.25), 2),
                ac_temperatura=round(random.uniform(16, 24), 2),
                at_ph=round(random.uniform(6.8, 7.8), 2),
                at_ce=round(random.uniform(350, 450), 1),
                at_tds=round(random.uniform(220, 290), 1),
                at_salinidad=round(random.uniform(0.18, 0.23), 2),
                at_temperatura=round(random.uniform(16, 24), 2),
            )
            fisico_records.append(fisico)
            
            # 1 registro de producción por día
            produccion = ProduccionFiltro(
                fecha=current_date,
                hora=time(12, 0, 0),
                filtro1_h=round(random.uniform(80, 120), 2),
                filtro1_q=round(random.uniform(25, 35), 2),
                filtro2_h=round(random.uniform(80, 120), 2),
                filtro2_q=round(random.uniform(25, 35), 2),
                filtro3_h=round(random.uniform(80, 120), 2),
                filtro3_q=round(random.uniform(25, 35), 2),
                filtro4_h=round(random.uniform(80, 120), 2),
                filtro4_q=round(random.uniform(25, 35), 2),
                filtro5_h=round(random.uniform(80, 120), 2),
                filtro5_q=round(random.uniform(25, 35), 2),
                filtro6_h=round(random.uniform(80, 120), 2),
                filtro6_q=round(random.uniform(25, 35), 2),
                caudal_total=round(random.uniform(150, 200), 2),
                observaciones="Operación normal"
            )
            produccion_records.append(produccion)
            
            current_date += timedelta(days=1)
        
        # Insertar todos los registros
        db.bulk_save_objects(control_records)
        db.bulk_save_objects(fisico_records)
        db.bulk_save_objects(produccion_records)
        db.commit()
        
        print(f"✅ {record_count} registros de control operacional insertados")
        print(f"✅ {len(fisico_records)} registros fisicoquímicos insertados")
        print(f"✅ {len(produccion_records)} registros de producción insertados")
        
        print("\n" + "="*60)
        print("✅ DATOS DE ENTRENAMIENTO GENERADOS EXITOSAMENTE")
        print("="*60)
        print(f"📊 Control Operacional: {record_count} registros")
        print(f"🔬 Monitoreo Fisicoquímico: {len(fisico_records)} registros")
        print(f"🏭 Producción: {len(produccion_records)} registros")
        print(f"📅 Rango: {start_date} a {end_date}")
        print(f"💾 Total: {record_count + len(fisico_records) + len(produccion_records)} registros")
        print("="*60)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    generate_training_data()
