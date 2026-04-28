"""
Script para agregar datos de consumo mensual
"""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.consumo_quimico_mensual import ConsumoQuimicoMensual
import random

def add_consumption_data():
    db = SessionLocal()
    try:
        print("📊 Generando datos de consumo mensual...")
        
        # Generar 4 meses de datos (octubre 2025 a febrero 2026)
        consumos = []
        for i in range(5):
            # Crear fecha del primer día del mes
            if i == 0:
                fecha_mes = date(2026, 2, 1)
            elif i == 1:
                fecha_mes = date(2026, 1, 1)
            elif i == 2:
                fecha_mes = date(2025, 12, 1)
            elif i == 3:
                fecha_mes = date(2025, 11, 1)
            else:
                fecha_mes = date(2025, 10, 1)
            
            consumo = ConsumoQuimicoMensual(
                fecha=fecha_mes,
                mes=fecha_mes.month,
                anio=fecha_mes.year,
                sulfato_con=round(random.uniform(1000, 1500), 2),
                sulfato_ing=round(random.uniform(1200, 1800), 2),
                sulfato_guia=f"GS-{fecha_mes.year}-{fecha_mes.month:02d}-001",
                sulfato_re=round(random.uniform(200, 400), 2),
                cal_con=round(random.uniform(70, 100)),
                cal_ing=round(random.uniform(80, 120)),
                cal_guia=f"GC-{fecha_mes.year}-{fecha_mes.month:02d}-001",
                hipoclorito_con=round(random.uniform(200, 300), 2),
                hipoclorito_ing=round(random.uniform(250, 350), 2),
                hipoclorito_guia=f"GH-{fecha_mes.year}-{fecha_mes.month:02d}-001",
                cloro_gas_con=round(random.uniform(450, 550), 2),
                cloro_gas_ing_bal=round(random.uniform(6, 10)),
                cloro_gas_ing_bdg=round(random.uniform(1, 3)),
                cloro_gas_guia=f"GCL-{fecha_mes.year}-{fecha_mes.month:02d}-001",
                cloro_gas_egre=round(random.uniform(5, 8)),
                produccion_m3_dia=round(random.uniform(3000, 4000), 2),
                inicio_mes_kg=round(random.uniform(500, 700), 2),
                ingreso_mes_kg=round(random.uniform(1200, 1500), 2),
                consumo_mes_kg=round(random.uniform(1000, 1300), 2),
                egreso_mes_kg=round(random.uniform(600, 800), 2),
            )
            consumos.append(consumo)
        
        db.add_all(consumos)
        db.commit()
        
        print(f"✅ {len(consumos)} registros de consumo mensual insertados")
        print("\nRegistros insertados:")
        for c in consumos:
            print(f"  - {c.anio}-{c.mes:02d}: Sulfato={c.sulfato_con} kg, Cal={c.cal_con} sacos")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_consumption_data()
