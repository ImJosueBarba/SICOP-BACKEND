"""
Genera datos sintéticos para entrenamiento de modelos ML.

Crea datos realistas de prueba para 6 meses de operación de la planta.
"""

import sys
from datetime import date, timedelta
from pathlib import Path
import random

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models.control_operacion import ControlOperacion
from models.consumo_quimico_mensual import ConsumoQuimicoMensual
from models.monitoreo_fisicoquimico import MonitoreoFisicoquimico
from models.produccion_filtro import ProduccionFiltro


def generate_realistic_data(num_days=180):
    """
    Genera datos sintéticos realistas para entrenamiento.
    
    Args:
        num_days: Número de días de datos a generar (default: 180 = 6 meses)
    """
    print(f"Generando datos sintéticos para {num_days} días...")
    
    db = SessionLocal()
    
    try:
        # Fecha inicial
        end_date = date.today()
        start_date = end_date - timedelta(days=num_days)
        
        # Parámetros base con variación estacional
        base_params = {
            'turbedad_at': 50.0,
            'turbedad_ac': 5.0,
            'ph_at': 7.2,
            'ph_ac': 7.5,
            'temperatura': 22.0,
            'cloro_residual': 0.8,
            'conductividad_at': 400.0,
            'conductividad_ac': 380.0,
            'sulfato_aluminio': 120.0,
            'cal': 30.0,
            'hipoclorito_calcio': 15.0,
            'cloro_gas': 10.0,
            'caudal': 250.0,
            'solidos_totales': 200.0
        }
        
        print("\nGenerando datos diarios...")
        count = 0
        
        for day_offset in range(num_days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Variación estacional (más turbiedad en época de lluvias)
            month = current_date.month
            seasonal_factor = 1.3 if month in [5, 6, 7, 8, 9, 10] else 1.0
            
            # Variación aleatoria diaria
            daily_variation = random.uniform(0.85, 1.15)
            
            # Variación por día de la semana (menor demanda fin de semana)
            weekday_factor = 0.8 if current_date.weekday() >= 5 else 1.0
            
            # 1. Control de Operación
            control = ControlOperacion(
                fecha=current_date,
                turbedad_at=base_params['turbedad_at'] * seasonal_factor * daily_variation,
                turbedad_ac=base_params['turbedad_ac'] * daily_variation,
                ph_at=base_params['ph_at'] + random.uniform(-0.3, 0.3),
                ph_ac=base_params['ph_ac'] + random.uniform(-0.2, 0.2),
                temperatura=base_params['temperatura'] + random.uniform(-3, 5),
                cloro_residual=base_params['cloro_residual'] + random.uniform(-0.2, 0.3),
                conductividad_at=base_params['conductividad_at'] * seasonal_factor * random.uniform(0.9, 1.1),
                conductividad_ac=base_params['conductividad_ac'] * seasonal_factor * random.uniform(0.9, 1.1),
                presion_entrada=random.uniform(2.5, 3.5),
                presion_salida=random.uniform(2.0, 3.0),
                observaciones=f"Operación normal día {day_offset+1}"
            )
            db.add(control)
            
            # 2. Monitoreo Fisicoquímico (cada 7 días)
            if day_offset % 7 == 0:
                fisicoquimico = MonitoreoFisicoquimico(
                    fecha=current_date,
                    dureza_total=random.uniform(100, 200),
                    dureza_calcica=random.uniform(60, 120),
                    alcalinidad=random.uniform(80, 150),
                    turbiedad=base_params['turbedad_ac'] * daily_variation,
                    color=random.uniform(5, 15),
                    olor="Sin olor",
                    sabor="Sin sabor",
                    temperatura=base_params['temperatura'] + random.uniform(-2, 3),
                    ph=base_params['ph_ac'] + random.uniform(-0.2, 0.2),
                    conductividad=base_params['conductividad_ac'] * random.uniform(0.95, 1.05),
                    solidos_totales=base_params['solidos_totales'] * random.uniform(0.9, 1.1),
                    solidos_suspendidos=random.uniform(3, 8),
                    solidos_disueltos=base_params['solidos_totales'] * random.uniform(0.85, 0.95),
                    cloruros=random.uniform(10, 30),
                    sulfatos=random.uniform(50, 100),
                    nitratos=random.uniform(1, 5),
                    nitritos=random.uniform(0.01, 0.1),
                    amonio=random.uniform(0.01, 0.2),
                    hierro=random.uniform(0.05, 0.2),
                    manganeso=random.uniform(0.01, 0.1),
                    cloro_residual_libre=base_params['cloro_residual'] + random.uniform(-0.1, 0.2),
                    cumple_norma=True
                )
                db.add(fisicoquimico)
            
            # 3. Producción de Filtros (cada 7 días)
            if day_offset % 7 == 0:
                produccion = ProduccionFiltro(
                    fecha=current_date,
                    filtro_numero=random.randint(1, 4),
                    volumen_tratado=base_params['caudal'] * 24 * weekday_factor * random.uniform(0.9, 1.1),
                    caudal_promedio=base_params['caudal'] * weekday_factor * random.uniform(0.95, 1.05),
                    tiempo_operacion=random.uniform(20, 24),
                    duracion_retrolavado=random.uniform(15, 25),
                    turbedad_entrada=base_params['turbedad_at'] * seasonal_factor * random.uniform(0.9, 1.1),
                    turbedad_salida=base_params['turbedad_ac'] * random.uniform(0.9, 1.1),
                    perdida_carga_inicial=random.uniform(0.3, 0.6),
                    perdida_carga_final=random.uniform(0.8, 1.5),
                    eficiencia=random.uniform(88, 96)
                )
                db.add(produccion)
            
            count += 1
            
            # Commit cada 30 días
            if count % 30 == 0:
                db.commit()
                print(f"  ✓ {count}/{num_days} días procesados")
        
        # Commit restante
        db.commit()
        
        # 4. Consumo Químico Mensual
        print("\nGenerando consumo mensual de químicos...")
        
        num_months = (num_days // 30) + 1
        current_date = start_date
        
        for month_offset in range(num_months):
            # Calcular año y mes
            year = current_date.year
            month = current_date.month
            
            # Variación estacional
            seasonal_factor = 1.4 if month in [5, 6, 7, 8, 9, 10] else 1.0
            monthly_variation = random.uniform(0.9, 1.1)
            
            # Volumen tratado en el mes (aprox. 30 días)
            volumen_mensual = base_params['caudal'] * 24 * 30 * monthly_variation
            
            # Consumos basados en volumen y calidad de agua
            consumo = ConsumoQuimicoMensual(
                anio=year,
                mes=month,
                sulfato_aluminio=base_params['sulfato_aluminio'] * seasonal_factor * monthly_variation * 30,
                cal=base_params['cal'] * seasonal_factor * monthly_variation * 30,
                hipoclorito_calcio=base_params['hipoclorito_calcio'] * monthly_variation * 30,
                cloro_gas=base_params['cloro_gas'] * monthly_variation * 30,
                polielectrolito=random.uniform(5, 15) * 30,  # kg/mes
                carbon_activado=random.uniform(20, 50) * monthly_variation,  # kg/mes
                volumen_tratado=volumen_mensual,
                costo_total=(
                    base_params['sulfato_aluminio'] * 0.5 * seasonal_factor * monthly_variation * 30 +
                    base_params['cal'] * 0.3 * seasonal_factor * monthly_variation * 30 +
                    base_params['hipoclorito_calcio'] * 2.0 * monthly_variation * 30 +
                    base_params['cloro_gas'] * 1.5 * monthly_variation * 30
                )
            )
            db.add(consumo)
            
            print(f"  ✓ {year}-{month:02d}: {consumo.volumen_tratado:.0f} m³, ${consumo.costo_total:.2f}")
            
            # Avanzar al siguiente mes
            if month == 12:
                current_date = date(year + 1, 1, 1)
            else:
                current_date = date(year, month + 1, 1)
        
        db.commit()
        
        # Resumen
        print("\n" + "=" * 70)
        print("✅ DATOS GENERADOS EXITOSAMENTE")
        print("=" * 70)
        
        # Estadísticas
        total_control = db.query(ControlOperacion).count()
        total_consumo = db.query(ConsumoQuimicoMensual).count()
        total_fisico = db.query(MonitoreoFisicoquimico).count()
        total_produccion = db.query(ProduccionFiltro).count()
        
        print(f"\nRegistros creados:")
        print(f"  ├─ Control de Operación: {total_control}")
        print(f"  ├─ Consumo Químico Mensual: {total_consumo}")
        print(f"  ├─ Monitoreo Fisicoquímico: {total_fisico}")
        print(f"  └─ Producción de Filtros: {total_produccion}")
        print(f"\nTotal: {total_control + total_consumo + total_fisico + total_produccion} registros")
        
        print("\nEl sistema está listo para entrenar modelos ML.")
        print("Ejecute: python train_ml_model.py")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


def clear_existing_data():
    """Limpia datos existentes (opcional)."""
    print("⚠ ADVERTENCIA: Esta acción eliminará TODOS los datos existentes")
    response = input("¿Desea continuar? (s/N): ")
    
    if response.lower() != 's':
        print("Operación cancelada")
        return False
    
    db = SessionLocal()
    
    try:
        print("Eliminando datos...")
        db.query(ProduccionFiltro).delete()
        db.query(MonitoreoFisicoquimico).delete()
        db.query(ConsumoQuimicoMensual).delete()
        db.query(ControlOperacion).delete()
        db.commit()
        print("✓ Datos eliminados")
        return True
    
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()


def main():
    """Función principal."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + "  Generador de Datos Sintéticos".center(70) + "║")
    print("║" + "  Sistema ML - Optimización Consumo de Químicos".center(70) + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Menú
    print("\nOpciones:")
    print("1. Generar 180 días de datos (6 meses) - Recomendado")
    print("2. Generar 90 días de datos (3 meses) - Mínimo")
    print("3. Generar 365 días de datos (1 año)")
    print("4. Limpiar datos existentes")
    print("5. Salir")
    
    choice = input("\nSeleccione una opción (1-5): ")
    
    if choice == '1':
        generate_realistic_data(180)
    elif choice == '2':
        generate_realistic_data(90)
    elif choice == '3':
        generate_realistic_data(365)
    elif choice == '4':
        if clear_existing_data():
            print("\nPuede generar nuevos datos ejecutando este script nuevamente")
    elif choice == '5':
        print("Saliendo...")
    else:
        print("Opción inválida")


if __name__ == "__main__":
    main()
