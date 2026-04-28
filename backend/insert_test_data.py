"""
Script para insertar datos de prueba en la base de datos
"""
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models.control_operacion import ControlOperacion
from models.monitoreo_fisicoquimico import MonitoreoFisicoquimico
from models.control_cloro_libre import ControlCloroLibre
from models.produccion_filtro import ProduccionFiltro
from models.consumo_quimico_mensual import ConsumoQuimicoMensual
from models.control_consumo_diario import ControlConsumoDiario
from models.quimico import Quimico

def insert_test_data():
    db = SessionLocal()
    try:
        print("🔄 Limpiando datos anteriores...")
        # Eliminar datos existentes en orden inverso por las relaciones
        db.query(ControlConsumoDiario).delete()
        db.query(ConsumoQuimicoMensual).delete()
        db.query(ProduccionFiltro).delete()
        db.query(ControlCloroLibre).delete()
        db.query(MonitoreoFisicoquimico).delete()
        db.query(ControlOperacion).delete()
        db.query(Quimico).delete()
        db.commit()
        print("✅ Datos anteriores eliminados")
        
        print("\n🔄 Insertando datos de prueba...")
        
        # 1. Insertar Químicos (Reactivos)
        print("\n📦 Insertando Químicos...")
        quimicos = [
            Quimico(codigo="QUI-001", nombre="Sulfato de Aluminio", tipo="SULFATO_ALUMINIO", unidad_medida="KG", 
                   peso_por_unidad=25.0, stock_actual=500, stock_minimo=100, proveedor="QuimiPro S.A.", activo=True),
            Quimico(codigo="QUI-002", nombre="Cal Hidratada", tipo="CAL", unidad_medida="SACOS", 
                   peso_por_unidad=25.0, stock_actual=80, stock_minimo=20, proveedor="Minerales del Sur", activo=True),
            Quimico(codigo="QUI-003", nombre="Hipoclorito de Calcio", tipo="HIPOCLORITO", unidad_medida="KG", 
                   peso_por_unidad=50.0, stock_actual=200, stock_minimo=50, proveedor="QuimiPro S.A.", activo=True),
            Quimico(codigo="QUI-004", nombre="Cloro Gas", tipo="CLORO_GAS", unidad_medida="BALONES", 
                   peso_por_unidad=68.0, stock_actual=10, stock_minimo=3, proveedor="Gases Industriales", activo=True),
            Quimico(codigo="QUI-005", nombre="Floculante Floergel", tipo="FLOCULANTE", unidad_medida="KG", 
                   peso_por_unidad=25.0, stock_actual=150, stock_minimo=30, proveedor="QuimiPro S.A.", activo=True)
        ]
        db.add_all(quimicos)
        db.commit()
        print(f"✅ {len(quimicos)} químicos insertados")
        
        # 2. Insertar Control de Operación
        print("\n⚙️ Insertando Control de Operación...")
        hoy = date.today()
        operaciones = []
        for i in range(5):
            fecha = hoy - timedelta(days=i)
            operaciones.append(ControlOperacion(
                fecha=fecha,
                hora=time(7+i, 0),  # Convertir a objeto time
                turbedad_ac=12.5 + i,
                turbedad_at=0.8 + (i*0.1),
                color="Claro",
                ph_ac=7.2 + (i*0.1),
                ph_sulf=6.8 + (i*0.1),
                ph_at=7.5 + (i*0.1),
                dosis_sulfato=35.0 + i,
                dosis_cal=12.0 + i,
                dosis_floergel=0.5 + (i*0.1),
                ff=15.0 + i,
                clarificacion_is=8.0 + i,
                clarificacion_cs=6.0 + i,
                clarificacion_fs=4.0 + i,
                presion_psi=45.0 + i,
                presion_pre=42.0 + i,
                presion_pos=38.0 + i,
                presion_total=125.0 + i,
                cloro_residual=0.8 + (i*0.1),
                observaciones=f"Operación normal día {i+1}" if i % 2 == 0 else None,
                usuario_id=1
            ))
        db.add_all(operaciones)
        db.commit()
        print(f"✅ {len(operaciones)} registros de control de operación insertados")
        
        # 3. Insertar Monitoreo Fisicoquímico
        print("\n🔬 Insertando Monitoreo Fisicoquímico...")
        monitoreos = []
        for i in range(5):
            fecha = hoy - timedelta(days=i)
            muestra_num = (i % 3) + 1  # Alternar entre 1, 2, 3
            monitoreos.append(MonitoreoFisicoquimico(
                fecha=fecha,
                muestra_numero=muestra_num,
                hora=time(8+i, 30),
                lugar_agua_cruda="Toma Principal",
                lugar_agua_tratada="Salida Planta",
                ac_ph=7.3 + (i*0.1),
                ac_ce=450.0 + (i*10),
                ac_tds=280.0 + (i*5),
                ac_salinidad=0.22 + (i*0.01),
                ac_temperatura=18.5 + (i*0.5),
                at_ph=7.6 + (i*0.1),
                at_ce=420.0 + (i*10),
                at_tds=260.0 + (i*5),
                at_salinidad=0.20 + (i*0.01),
                at_temperatura=18.0 + (i*0.5),
                observaciones=f"Muestra {i+1} - Parámetros normales",
                usuario_id=1
            ))
        db.add_all(monitoreos)
        db.commit()
        print(f"✅ {len(monitoreos)} registros de monitoreo fisicoquímico insertados")
        
        # 4. Insertar Control de Cloro Libre
        print("\n💧 Insertando Control de Cloro Libre...")
        controles_cloro = []
        for i in range(5):
            fecha = hoy - timedelta(days=i*7)
            controles_cloro.append(ControlCloroLibre(
                fecha_mes=fecha,
                documento_soporte=f"DOC-2026-{100+i}",
                proveedor_solicitante="QuimiPro S.A." if i % 2 == 0 else "Operaciones Planta",
                codigo=f"CLO-{2026}{i+1:03d}",
                especificacion=f"Cloro al {i*10+60}% - Grado industrial",
                cantidad_entra=100.0 + (i*20) if i % 2 == 0 else None,
                cantidad_sale=50.0 + (i*10) if i % 2 == 1 else None,
                cantidad_saldo=500.0 + (i*15),
                observaciones=f"Ingreso de {i+1} cilindros" if i % 2 == 0 else f"Consumo operación día {i+1}",
                usuario_id=1
            ))
        db.add_all(controles_cloro)
        db.commit()
        print(f"✅ {len(controles_cloro)} registros de control de cloro insertados")
        
        # 5. Insertar Producción de Filtros
        print("\n🔧 Insertando Producción de Filtros...")
        producciones = []
        for i in range(5):
            fecha = hoy - timedelta(days=i)
            producciones.append(ProduccionFiltro(
                fecha=fecha,
                hora=time(9+i, 0),
                filtro1_h=150.0 + i,
                filtro1_q=8.5 + (i*0.2),
                filtro2_h=148.0 + i,
                filtro2_q=8.3 + (i*0.2),
                filtro3_h=152.0 + i,
                filtro3_q=8.7 + (i*0.2),
                filtro4_h=149.0 + i,
                filtro4_q=8.4 + (i*0.2),
                filtro5_h=151.0 + i,
                filtro5_q=8.6 + (i*0.2),
                filtro6_h=150.0 + i,
                filtro6_q=8.5 + (i*0.2),
                caudal_total=51.0 + i,
                observaciones=f"Todos los filtros operando normalmente - Día {i+1}",
                usuario_id=1
            ))
        db.add_all(producciones)
        db.commit()
        print(f"✅ {len(producciones)} registros de producción de filtros insertados")
        
        # 6. Insertar Consumo Químico Mensual
        print("\n📊 Insertando Consumo Químico Mensual...")
        consumos_mensual = []
        for i in range(5):
            # Retroceder i meses desde el mes actual
            fecha_mes = date(2026, 2, 1) - timedelta(days=30*i)  # Aproximación
            # Ajustar al primer día del mes correspondiente
            fecha_mes = date(fecha_mes.year, fecha_mes.month, 1)
            consumos_mensual.append(ConsumoQuimicoMensual(
                fecha=fecha_mes,
                mes=fecha_mes.month,
                anio=fecha_mes.year,
                sulfato_con=1200.0 + (i*100),
                sulfato_ing=1500.0 + (i*150),
                sulfato_guia=f"GS-{fecha_mes.year}-{fecha_mes.month:02d}-{i+1:03d}",
                sulfato_re=300.0 + (i*50),
                cal_con=80.0 + (i*10),
                cal_ing=100.0 + (i*15),
                cal_guia=f"GC-{fecha_mes.year}-{fecha_mes.month:02d}-{i+1:03d}",
                hipoclorito_con=250.0 + (i*25),
                hipoclorito_ing=300.0 + (i*30),
                hipoclorito_guia=f"GH-{fecha_mes.year}-{fecha_mes.month:02d}-{i+1:03d}",
                cloro_gas_con=500.0 + (i*50),
                cloro_gas_ing_bal=8 + i,
                cloro_gas_ing_bdg=2 + i,
                cloro_gas_guia=f"GCL-{fecha_mes.year}-{fecha_mes.month:02d}-{i+1:03d}",
                cloro_gas_egre=6 + i,
                observaciones=f"Consumo mes {fecha_mes.month}/{fecha_mes.year}",
                usuario_id=1
            ))
        db.add_all(consumos_mensual)
        db.commit()
        print(f"✅ {len(consumos_mensual)} registros de consumo mensual insertados")
        
        # 7. Insertar Consumo Diario
        print("\n📅 Insertando Consumo Diario...")
        # Primero obtenemos los IDs de los químicos insertados
        quimicos_db = db.query(Quimico).limit(4).all()
        consumos_diario = []
        for i in range(5):
            fecha = hoy - timedelta(days=i)
            quimico_idx = i % len(quimicos_db)
            consumos_diario.append(ControlConsumoDiario(
                fecha=fecha,
                quimico_id=quimicos_db[quimico_idx].id,
                bodega_ingresa=100.0 + (i*20) if i % 2 == 0 else None,
                bodega_egresa=50.0 + (i*10),
                bodega_stock=500.0 + (i*25),
                tanque1_hora=time(7+i, 0),
                tanque1_lectura_inicial=180.0 + i,
                tanque1_lectura_final=160.0 + i,
                tanque1_consumo=20.0 + i,
                tanque2_hora=time(14+i, 0) if i % 2 == 0 else None,
                tanque2_lectura_inicial=175.0 + i if i % 2 == 0 else None,
                tanque2_lectura_final=155.0 + i if i % 2 == 0 else None,
                tanque2_consumo=20.0 + i if i % 2 == 0 else None,
                total_consumo=(20.0 + i) * (2 if i % 2 == 0 else 1),
                observaciones=f"Consumo día {i+1} - {quimicos_db[quimico_idx].nombre}",
                usuario_id=1
            ))
        db.add_all(consumos_diario)
        db.commit()
        print(f"✅ {len(consumos_diario)} registros de consumo diario insertados")
        
        print("\n" + "="*60)
        print("✅ TODOS LOS DATOS DE PRUEBA HAN SIDO INSERTADOS")
        print("="*60)
        print(f"📦 Químicos: {len(quimicos)}")
        print(f"⚙️  Control Operación: {len(operaciones)}")
        print(f"🔬 Monitoreo Fisicoquímico: {len(monitoreos)}")
        print(f"💧 Control Cloro: {len(controles_cloro)}")
        print(f"🔧 Producción Filtros: {len(producciones)}")
        print(f"📊 Consumo Mensual: {len(consumos_mensual)}")
        print(f"📅 Consumo Diario: {len(consumos_diario)}")
        print(f"📈 TOTAL: {len(quimicos) + len(operaciones) + len(monitoreos) + len(controles_cloro) + len(producciones) + len(consumos_mensual) + len(consumos_diario)} registros")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_data()
