from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models.control_operacion import ControlOperacion
from models.usuario import Usuario
from models.rol import Rol
import sys

# Asegurar que todas las tablas estén creadas
def init_db():
    # Importar todos los modelos para que se registren
    try:
        from models import control_operacion, usuario, rol
        print("✅ Modelos importados correctamente")
    except Exception as e:
        print(f"⚠️ Error al importar modelos: {e}")

def seed_database():
    init_db()
    db = SessionLocal()
    try:
        print("🌱 Iniciando seed de datos...")
        
        # Limpiar datos existentes solo de control_operacion
        print("🗑️ Limpiando datos existentes de Control de Operación...")
        from sqlalchemy import text
        try:
            db.execute(text("TRUNCATE TABLE control_operacion RESTART IDENTITY CASCADE"))
            db.commit()
            print("✅ Datos anteriores eliminados")
        except Exception as e:
            print(f"⚠️ No se pudieron limpiar datos previos: {e}")
            db.rollback()
        
        # Control de Operación - 60 registros (2 meses)
        print("📊 Insertando datos de Control de Operación...")
        fecha_inicio = datetime.now() - timedelta(days=60)
        
        for i in range(60):
            fecha = fecha_inicio + timedelta(days=i)
            
            # 3 registros por día (3 turnos)
            for turno in range(3):
                hora = f"{7 + turno * 8:02d}:00:00"
                
                control = ControlOperacion(
                    fecha=fecha.date(),
                    hora=hora,
                    turbedad_ac=round(random.uniform(1.5, 5.0), 2),
                    turbedad_at=round(random.uniform(0.1, 0.5), 2),
                    color="Normal",
                    ph_ac=round(random.uniform(6.5, 7.5), 2),
                    ph_sulf=round(random.uniform(3.5, 4.5), 2),
                    ph_at=round(random.uniform(6.8, 7.2), 2),
                    dosis_sulfato=round(random.uniform(20, 35), 2),
                    dosis_cal=round(random.uniform(10, 20), 2),
                    dosis_floergel=round(random.uniform(0.5, 2.0), 2),
                    ff=round(random.uniform(85, 95), 2),
                    clarificacion_is=round(random.uniform(2.0, 4.0), 2),
                    clarificacion_cs=round(random.uniform(1.0, 2.5), 2),
                    clarificacion_fs=round(random.uniform(0.3, 0.8), 2),
                    presion_psi=round(random.uniform(45, 55), 2),
                    presion_pre=round(random.uniform(40, 50), 2),
                    presion_pos=round(random.uniform(35, 45), 2),
                    presion_total=round(random.uniform(120, 150), 2),
                    cloro_residual=round(random.uniform(0.5, 1.5), 2),
                    observaciones="Operación normal" if random.random() > 0.3 else "Revisión realizada",
                    usuario_id=1
                )
                db.add(control)
        
        db.commit()
        print(f"✅ Insertados {60 * 3} registros de Control de Operación")
        
        # Monitoreo Fisicoquímico - 10 registros
        print("🔬 Insertando datos de Monitoreo Fisicoquímico...")
        from sqlalchemy import text
        fecha_inicio = datetime.now() - timedelta(days=10)
        count = 0
        for i in range(4):
            fecha = fecha_inicio + timedelta(days=i)
            for muestra in range(1, 4):  # 3 muestras por día
                if count >= 10:
                    break
                db.execute(text("""
                    INSERT INTO monitoreo_fisicoquimico 
                    (fecha, muestra_numero, hora, lugar_agua_cruda, lugar_agua_tratada,
                     ac_ph, ac_ce, ac_tds, ac_salinidad, ac_temperatura,
                     at_ph, at_ce, at_tds, at_salinidad, at_temperatura, observaciones, usuario_id)
                    VALUES (:fecha, :muestra, :hora, :lugar_ac, :lugar_at,
                            :ac_ph, :ac_ce, :ac_tds, :ac_sal, :ac_temp,
                            :at_ph, :at_ce, :at_tds, :at_sal, :at_temp, :obs, :usuario_id)
                """), {
                    'fecha': fecha.date(),
                    'muestra': muestra,
                    'hora': f"{6 + muestra * 6:02d}:00:00",
                    'lugar_ac': random.choice(["Bocatoma", "Entrada Planta"]),
                    'lugar_at': random.choice(["Salida Planta", "Red Distribución"]),
                    'ac_ph': round(random.uniform(6.0, 7.5), 2),
                    'ac_ce': round(random.uniform(100, 500), 2),
                    'ac_tds': round(random.uniform(50, 300), 2),
                    'ac_sal': round(random.uniform(0.1, 0.5), 3),
                    'ac_temp': round(random.uniform(15, 22), 2),
                    'at_ph': round(random.uniform(6.5, 7.2), 2),
                    'at_ce': round(random.uniform(80, 400), 2),
                    'at_tds': round(random.uniform(40, 250), 2),
                    'at_sal': round(random.uniform(0.05, 0.4), 3),
                    'at_temp': round(random.uniform(16, 23), 2),
                    'obs': "Normal" if random.random() > 0.3 else "Requiere monitoreo",
                    'usuario_id': 1
                })
                count += 1
        10 registros
        print("💧 Insertando datos de Control de Cloro Libre...")
        codigos = ["CLO-001", "CLO-002", "HIP-001", "HIP-002"]
        proveedores = ["Quimicos SA", "Cloro Tech", "Distribuidora Norte"]
        
        fecha_inicio = datetime.now() - timedelta(days=10)
        for i in range(10):
            fecha = fecha_inicio + timedelta(days=i)
            codigo = random.choice(codigos)
            db.execute(text("""
                INSERT INTO control_cloro_libre 
                (fecha_mes, documento_soporte, proveedor_solicitante, codigo, especificacion,
                 cantidad_entra, cantidad_sale, cantidad_saldo, observaciones, usuario_id)
                VALUES (:fecha, :doc, :prov, :codigo, :espec, :entra, :sale, :saldo, :obs, :usuario_id)
            """), {
                'fecha': fecha.date(),
                'doc': f"FAC-{1000 + i}",
                'prov': proveedores[i % 3],
                'codigo': codigo,
                'espec': "Cloro granulado 65%" if "CLO" in codigo else "Hipoclorito de calcio",
                'entra': random.randint(50, 100) if i % 3 == 0 else 0,
                'sale': random.randint(10, 30),
                'saldo': 500 - (i * 20),
                'obs': "Stock normal" if i % 3 != 0 else "Reposición realizada",
                'usuario_id': 1
            })
        
        db.commit()
        print(f"✅ Insertados 11
            })
        
        db.commit()
        print(f"✅ Insertados 60 registros de Control de Cloro")
        
        # Producción de Filtros - 10 registros
        print("🔧 Insertando datos de Producción de Filtros...")
        fecha_inicio = datetime.now() - timedelta(days=10)
        for i in range(10):
            fecha = fecha_inicio + timedelta(days=i)
            hora = f"{8 + (i % 3) * 6:02d}:00:00"
            db.execute(text("""
                INSERT INTO produccion_filtros 
                (fecha, hora, filtro1_h, filtro1_q, filtro2_h, filtro2_q, filtro3_h, filtro3_q,
                 filtro4_h, filtro4_q, filtro5_h, filtro5_q, filtro6_h, filtro6_q,
                 caudal_total, observaciones, usuario_id)
                VALUES (:fecha, :hora, :f1h, :f1q, :f2h, :f2q, :f3h, :f3q,
                        :f4h, :f4q, :f5h, :f5q, :f6h, :f6q, :total, :obs, :usuario_id)
            """), {
                'fecha': fecha.date(),
                'hora': hora,
                'f1h': round(random.uniform(80, 120), 2),
                'f1q': round(random.uniform(8, 12), 2),
                'f2h': round(random.uniform(80, 120), 2),
                'f2q': round(random.uniform(8, 12), 2),
                'f3h': round(random.uniform(80, 120), 2),
                'f3q': round(random.uniform(8, 12), 2),
                'f4h': round(random.uniform(80, 120), 2),
                'f4q': round(random.uniform(8, 12), 2),
                'f5h': round(random.uniform(80, 120), 2),
                'f5q': round(random.uniform(8, 12), 2),
                'f6h': round(random.uniform(80, 120), 2),
                'f6q': round(random.uniform(8, 12), 2),
                'total': round(random.uniform(50, 70), 2),
                'obs': "Operación normal" if i % 3 != 0 else "Mantenimiento preventivo",
                'usuario_id': 1
            })
        
        db.commit()
        print(f"✅ Insertados 10 registros de Producción de Filtros")
        
        # Crear químicos primero
        print("🧪 Insertando químicos...")
        quimicos_data = [
            ("SUL-001", "Sulfato de Aluminio", "SULFATO_ALUMINIO", "KG", 25.0, 500, 5000, "Quimicos SA"),
            ("CAL-001", "Cal Hidratada", "CAL", "SACOS", 20.0, 50, 300, "Cal y Derivados"),
            ("HIP-001", "Hipoclorito de Calcio", "HIPOCLORITO", "KG", 1.0, 100, 800, "Cloro Tech"),
            ("CLO-001", "Gas Licuado de Cloro", "CLORO_GAS", "KG", 45.0, 50, 450, "Cloro Tech"),
        ]
        
        quimico_ids = {}
        for codigo, nombre, tipo, unidad, peso, stock_min, stock_actual, prov in quimicos_data:
            result = db.execute(text("""
                INSERT INTO quimicos 
                (codigo, nombre, tipo, unidad_medida, peso_por_unidad, stock_minimo, stock_actual, proveedor, activo)
                VALUES (:codigo, :nombre, :tipo, :unidad, :peso, :stock_min, :stock_actual, :prov, :activo)
                RETURNING id
            """), {
                'codigo': codigo,
                'nombre': nombre,
                'tipo': tipo,
                'unidad': unidad,
                'peso': peso,
                'stock_min': stock_min,
                'stock_actual': stock_actual,
                'prov': prov,
                'activo': True
            })
            quimico_ids[codigo] = result.fetchone()[0]
        
        db.commit()
        print(f"✅ Insertados {len(quimicos_data)} químicos")
        
        # Consumo Diario - 10 registros
        print("📋 Insertando datos de Consumo Diario...")
        fecha_inicio = datetime.now() - timedelta(days=10)
        for i in range(10):
            fecha = fecha_inicio + timedelta(days=i)
            # Rotamos entre químicos
            codigo_list = list(quimico_ids.keys())
            codigo = codigo_list[i % 4]
            quimico_id = quimico_ids[codigo]
            
            db.execute(text("""
                INSERT INTO control_consumo_diario_quimicos 
                (fecha, quimico_id, bodega_ingresa, bodega_egresa, bodega_stock,
                 tanque1_hora, tanque1_lectura_inicial, tanque1_lectura_final, tanque1_consumo,
                 tanque2_hora, tanque2_lectura_inicial, tanque2_lectura_final, tanque2_consumo,
                 total_consumo, observaciones, usuario_id)
                VALUES (:fecha, :quimico_id, :b_ing, :b_egr, :b_stock,
                        :t1_hora, :t1_ini, :t1_fin, :t1_con,
                        :t2_hora, :t2_ini, :t2_fin, :t2_con,
                        :total, :obs, :usuario_id)
            """), {
                'fecha': fecha.date(),
                'quimico_id': quimico_id,
                'b_ing': 100 if i % 4 == 0 else 0,
                'b_egr': 20 + (i * 2),
                'b_stock': 500 - (i * 10),
                't1_hora': "08:00:00",
                't1_ini': 100.0,
                't1_fin': round(100 - (10 + i), 2),
                't1_con': round(10 + i, 2),
                't2_hora': "16:00:00" if codigo == "SUL-001" else None,
                't2_ini': 100.0 if codigo == "SUL-001" else None,
                't2_fin': round(100 - (8 + i), 2) if codigo == "SUL-001" else None,
                't2_con': round(8 + i, 2) if codigo == "SUL-001" else None,
                'total': round(18 + (i * 2), 2) if codigo == "SUL-001" else round(10 + i, 2),
                'obs': "Consumo normal",
                'usuario_id': 1
            })
        
        db.commit()
        print(f"✅ Insertados 10 registros de Consumo Diario")
        
        # Consumo Mensual - 2 registros (2 meses)
        print("📊 Insertando datos de Consumo Mensual...")
        for mes in [1, 2]:
            anio = 2026
            db.execute(text("""
                INSERT INTO consumo_quimicos_mensual 
                (fecha, mes, anio, sulfato_con, sulfato_ing, sulfato_guia, sulfato_re,
                 cal_con, cal_ing, cal_guia,
                 hipoclorito_con, hipoclorito_ing, hipoclorito_guia,
                 cloro_gas_con, cloro_gas_ing_bal, cloro_gas_ing_bdg, cloro_gas_guia, cloro_gas_egre,
                 produccion_m3_dia, inicio_mes_kg, ingreso_mes_kg, consumo_mes_kg, egreso_mes_kg, fin_mes_kg,
                 observaciones, usuario_id)
                VALUES (:fecha, :mes, :anio, :sulf_con, :sulf_ing, :sulf_guia, :sulf_re,
                        :cal_con, :cal_ing, :cal_guia,
                        :hip_con, :hip_ing, :hip_guia,
                        :clo_con, :clo_bal, :clo_bdg, :clo_guia, :clo_egre,
                        :prod, :ini, :ing, :con, :egr, :fin, :obs, :usuario_id)
            """), {
                'fecha': datetime(anio, mes, 1).date(),
                'mes': mes,
                'anio': anio,
                'sulf_con': round(random.uniform(1000, 3000), 2),
                'sulf_ing': round(random.uniform(2000, 4000), 2),
                'sulf_guia': f"GUIA-{random.randint(1000, 9999)}",
                'sulf_re': round(random.uniform(500, 1500), 2),
                'cal_con': random.randint(100, 300),
                'cal_ing': random.randint(200, 400),
                'cal_guia': f"GUIA-{random.randint(1000, 9999)}",
                'hip_con': round(random.uniform(50, 150), 2),
                'hip_ing': round(random.uniform(100, 200), 2),
                'hip_guia': f"GUIA-{random.randint(1000, 9999)}",
                'clo_con': round(random.uniform(200, 500), 2),
                'clo_bal': round(random.uniform(300, 600), 2),
                'clo_bdg': round(random.uniform(100, 300), 2),
                'clo_guia': f"GUIA-{random.randint(1000, 9999)}",
                'clo_egre': round(random.uniform(50, 150), 2),
                'prod': round(random.uniform(1000, 2000), 2),
                'ini': round(random.uniform(500, 1000), 2),
                'ing': round(random.uniform(2000, 4000), 2),
                'con': round(random.uniform(1500, 3000), 2),
                'egr': round(random.uniform(100, 300), 2),
                'fin': round(random.uniform(500, 1500), 2),
                'obs': f"Consumo mes {mes}/{anio}",
                'usuario_id': 1
            })
        
        db.commit()
        print(f"✅ Insertados0 registros
   - Monitoreo Fisicoquímico: 10 registros
   - Control de Cloro: 10 registros
   - Producción de Filtros: 10 registros
   - Químicos: 4 registros
   - Consumo Diario: 10 registros
   - Consumo Mensual: 2 registros
   
   TOTAL: ción de Filtros: 180 registros
   - Químicos: 4 registros
   - Consumo Diario: 240 registros
   - Consumo Mensual: 2 registros
   
   TOTAL: 756 registros
        """)
        
    except Exception as e:
        print(f"❌ Error durante el seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
