import sys, os
from datetime import datetime, timedelta
import random
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def init_db():
    from core.database import SessionLocal
    return SessionLocal()

if __name__ == "__main__":
    try:
        from models.control_operacion import ControlOperacion
        from models.monitoreo_fisicoquimico import MonitoreoFisicoquimico
        from models.produccion_filtro import ProduccionFiltro
        from models.control_consumo_diario import ControlConsumoDiario
        from models.consumo_quimico_mensual import ConsumoQuimicoMensual
        from models.control_cloro_libre import ControlCloroLibre
        from models.quimico import Quimico
        print("✅ Modelos importados")
    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    db = init_db()
    
    try:
        print("🌱 Iniciando seed...")
        from sqlalchemy import text
        db.execute(text("DELETE FROM control_operacion"))
        db.execute(text("DELETE FROM monitoreo_fisicoquimico"))
        db.execute(text("DELETE FROM produccion_filtros"))
        db.execute(text("DELETE FROM control_consumo_diario_quimicos"))
        db.execute(text("DELETE FROM consumo_quimicos_mensual"))
        db.execute(text("DELETE FROM control_cloro_libre"))
        db.execute(text("DELETE FROM quimicos"))
        db.commit()
        print("✅ Datos eliminados")
        
        # 10 registros de Control de Operación
        print(" Insertando Control de Operación...")
        fecha_inicio = datetime.now() - timedelta(days=10)
        
        for i in range(10):
            fecha = fecha_inicio + timedelta(days=i)
            hora = f"{6 + (i % 3) * 6:02d}:00:00"
            
            db.execute(text("""
                INSERT INTO control_operacion 
                (fecha, hora, turbedad_ac, turbedad_at, color, 
                 ph_ac, ph_sulf, ph_at,
                 dosis_sulfato, dosis_cal, dosis_floergel, ff,
                 clarificacion_is, clarificacion_cs, clarificacion_fs,
                 presion_psi, presion_pre, presion_pos, presion_total,
                 cloro_residual, observaciones, usuario_id)
                VALUES (:fecha, :hora, :turb_ac, :turb_at, :color,
                        :ph_ac, :ph_sulf, :ph_at,
                        :sulfato, :cal, :floergel, :ff,
                        :clar_is, :clar_cs, :clar_fs,
                        :psi, :pre, :pos, :total,
                        :cloro, :obs, :usuario_id)
            """), {
                'fecha': fecha.date(),
                'hora': hora,
                'turb_ac': round(random.uniform(5.0, 12.0), 2),
                'turb_at': round(random.uniform(0.3, 0.9), 2),
                'color': random.choice(["Claro", "Turbio", "Normal"]),
                'ph_ac': round(random.uniform(6.5, 7.5), 2),
                'ph_sulf': round(random.uniform(6.0, 7.0), 2),
                'ph_at': round(random.uniform(6.8, 7.3), 2),
                'sulfato': round(random.uniform(0.5, 2.5), 3),
                'cal': round(random.uniform(0.3, 1.5), 3),
                'floergel': round(random.uniform(0.1, 0.8), 3),
                'ff': round(random.uniform(1.0, 3.0), 2),
                'clar_is': round(random.uniform(100, 300), 2),
                'clar_cs': round(random.uniform(80, 250), 2),
                'clar_fs': round(random.uniform(50, 200), 2),
                'psi': round(random.uniform(15.0, 30.0), 2),
                'pre': round(random.uniform(200, 400), 2),
                'pos': round(random.uniform(150, 350), 2),
                'total': round(random.uniform(350, 750), 2),
                'cloro': round(random.uniform(0.5, 1.5), 2),
                'obs': f"Registro {i+1} - Operación normal",
                'usuario_id': 1
            })
        
        db.commit()
        print("✅ Control Operación: 10 registros")

        # Químicos
        print("🧪 Insertando químicos...")
        quimicos = [
            ("SUL-001", "Sulfato de Aluminio", "SULFATO_ALUMINIO", "KG", 25.0, 500, 5000),
            ("CAL-001", "Cal Hidratada", "CAL", "SACOS", 20.0, 50, 300),
            ("FLO-001", "Floergel", "POLIMERO", "KG", 1.0, 20, 150),
            ("CLO-001", "Cloro Gas", "CLORO_GAS", "KG", 45.0, 50, 450),
        ]
        
        for codigo, nombre, tipo, unidad, peso, stock_min, stock_actual in quimicos:
            db.execute(text("""
                INSERT INTO quimicos 
                (codigo, nombre, tipo, unidad_medida, peso_por_unidad, 
                 stock_minimo, stock_actual, proveedor, activo)
                VALUES (:codigo, :nombre, :tipo, :unidad, :peso, 
                        :stock_min, :stock_actual, :prov, :activo)
            """), {
                'codigo': codigo,
                'nombre': nombre,
                'tipo': tipo,
                'unidad': unidad,
                'peso': peso,
                'stock_min': stock_min,
                'stock_actual': stock_actual,
                'prov': "Químicos SA",
                'activo': True
            })
        
        db.commit()
        print("✅ Químicos: 4 registros")
        
        # Guardar IDs de químicos para usarlos después
        quimico_ids = {}
        result = db.execute(text("SELECT id, codigo FROM quimicos"))
        for row in result:
            quimico_ids[row[1]] = row[0]

        # Monitoreo Fisicoquímico - 10 registros
        print("🔬 Insertando Monitoreo Fisicoquímico...")
        fecha_inicio = datetime.now() - timedelta(days=10)
        count = 0
        for i in range(4):
            fecha = fecha_inicio + timedelta(days=i)
            for muestra in range(1, 4):
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
                    'lugar_ac': "Bocatoma Principal",
                    'lugar_at': "Salida Planta",
                    'ac_ph': round(random.uniform(6.8, 7.5), 2),
                    'ac_ce': round(random.uniform(150, 450), 2),
                    'ac_tds': round(random.uniform(80, 280), 2),
                    'ac_sal': round(random.uniform(0.15, 0.45), 3),
                    'ac_temp': round(random.uniform(16, 21), 2),
                    'at_ph': round(random.uniform(6.9, 7.3), 2),
                    'at_ce': round(random.uniform(120, 380), 2),
                    'at_tds': round(random.uniform(60, 230), 2),
                    'at_sal': round(random.uniform(0.08, 0.35), 3),
                    'at_temp': round(random.uniform(17, 22), 2),
                    'obs': f"Muestra {muestra} - Parámetros normales",
                    'usuario_id': 1
                })
                count += 1
        
        db.commit()
        print("✅ Monitoreo Fisicoquímico: 10 registros")
        
        # Producción de Filtros - 10 registros
        print("🔧 Insertando Producción de Filtros...")
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
                'f1h': round(random.uniform(85, 115), 2),
                'f1q': round(random.uniform(8, 14), 2),
                'f2h': round(random.uniform(85, 115), 2),
                'f2q': round(random.uniform(8, 14), 2),
                'f3h': round(random.uniform(85, 115), 2),
                'f3q': round(random.uniform(8, 14), 2),
                'f4h': round(random.uniform(85, 115), 2),
                'f4q': round(random.uniform(8, 14), 2),
                'f5h': round(random.uniform(85, 115), 2),
                'f5q': round(random.uniform(8, 14), 2),
                'f6h': round(random.uniform(85, 115), 2),
                'f6q': round(random.uniform(8, 14), 2),
                'total': round(random.uniform(55, 75), 2),
                'obs': f"Registro {i+1} - Todos los filtros operando",
                'usuario_id': 1
            })
        
        db.commit()
        print("✅ Producción Filtros: 10 registros")
        
        # Consumo Diario - 10 registros
        print("📋 Insertando Consumo Diario...")
        fecha_inicio = datetime.now() - timedelta(days=10)
        for i in range(10):
            fecha = fecha_inicio + timedelta(days=i)
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
                'b_ing': 100 if i % 5 == 0 else 0,
                'b_egr': 20 + (i * 3),
                'b_stock': 500 - (i * 15),
                't1_hora': "08:00:00",
                't1_ini': 120.0,
                't1_fin': round(120 - (15 + i), 2),
                't1_con': round(15 + i, 2),
                't2_hora': "16:00:00" if codigo == "SUL-001" else None,
                't2_ini': 110.0 if codigo == "SUL-001" else None,
                't2_fin': round(110 - (12 + i), 2) if codigo == "SUL-001" else None,
                't2_con': round(12 + i, 2) if codigo == "SUL-001" else None,
                'total': round(27 + (i * 2), 2) if codigo == "SUL-001" else round(15 + i, 2),
                'obs': f"Consumo día {i+1}",
                'usuario_id': 1
            })
        
        db.commit()
        print("✅ Consumo Diario: 10 registros")
        
        # Consumo Mensual - 2 registros
        print("📊 Insertando Consumo Mensual...")
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
                'sulf_con': round(1500 + (mes * 200), 2),
                'sulf_ing': round(2500 + (mes * 100), 2),
                'sulf_guia': f"GUIA-SUL-{mes}-2026",
                'sulf_re': round(800 + (mes * 50), 2),
                'cal_con': 180 + (mes * 20),
                'cal_ing': 250 + (mes * 30),
                'cal_guia': f"GUIA-CAL-{mes}-2026",
                'hip_con': round(85 + (mes * 10), 2),
                'hip_ing': round(120 + (mes * 15), 2),
                'hip_guia': f"GUIA-HIP-{mes}-2026",
                'clo_con': round(280 + (mes * 30), 2),
                'clo_bal': round(380 + (mes * 40), 2),
                'clo_bdg': round(150 + (mes * 20), 2),
                'clo_guia': f"GUIA-CLO-{mes}-2026",
                'clo_egre': round(75 + (mes * 10), 2),
                'prod': round(1400 + (mes * 100), 2),
                'ini': round(650 + (mes * 50), 2),
                'ing': round(2800 + (mes * 200), 2),
                'con': round(2100 + (mes * 150), 2),
                'egr': round(180 + (mes * 20), 2),
                'fin': round(750 + (mes * 60), 2),
                'obs': f"Resumen {mes}/2026",
                'usuario_id': 1
            })
        
        db.commit()
        print("✅ Consumo Mensual: 2 registros")
        
        # Control de Cloro - 10 registros
        print("💧 Insertando Control de Cloro...")
        codigos_cloro = ["CLO-001", "CLO-002", "HIP-001", "HIP-002"]
        proveedores = ["Quimicos SA", "Distribuidora Norte", "Cloro Tech"]
        
        fecha_inicio = datetime.now() - timedelta(days=10)
        for i in range(10):
            fecha = fecha_inicio + timedelta(days=i)
            codigo = codigos_cloro[i % 4]
            db.execute(text("""
                INSERT INTO control_cloro_libre 
                (fecha_mes, documento_soporte, proveedor_solicitante, codigo, especificacion,
                 cantidad_entra, cantidad_sale, cantidad_saldo, observaciones, usuario_id)
                VALUES (:fecha, :doc, :prov, :codigo, :espec, :entra, :sale, :saldo, :obs, :usuario_id)
            """), {
                'fecha': fecha.date(),
                'doc': f"FAC-2026-{1000 + i}",
                'prov': proveedores[i % 3],
                'codigo': codigo,
                'espec': "Cloro gas 99.5%" if "CLO" in codigo else "Hipoclorito de calcio 65%",
                'entra': 80 if i % 4 == 0 else 0,
                'sale': 12 + (i * 2),
                'saldo': 450 - (i * 18),
                'obs': f"Movimiento día {i+1}",
                'usuario_id': 1
            })
        
        db.commit()
        print("✅ Control Cloro: 10 registros")

        print("\n✨ ¡Seed completado!")
        print("""
📈 Resumen total:
   - Control Operación: 10 registros
   - Químicos: 4 registros
   - Monitoreo Fisicoquímico: 10 registros
   - Producción Filtros: 10 registros
   - Consumo Diario: 10 registros
   - Consumo Mensual: 2 registros
   - Control Cloro: 10 registros
   
   TOTAL: 56 registros
        """)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
