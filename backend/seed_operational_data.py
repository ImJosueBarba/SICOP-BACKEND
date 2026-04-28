"""
Script profesional para insertar datos operativos realistas
Sistema de Gestión de Planta de Tratamiento de Agua "La Esperanza"

Genera datos de control operacional de los últimos 7 días con:
- Variaciones normales de operación
- Algunos eventos anómalos identificables
- Datos consistentes con operación real de planta de tratamiento
"""

import sys
from datetime import datetime, date, time, timedelta
from pathlib import Path
import random
from decimal import Decimal

try:
    from werkzeug.security import generate_password_hash
except ImportError:
    # Fallback si werkzeug no está instalado
    def generate_password_hash(password):
        return password

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models import Base, ControlOperacion, Usuario


class OperationalDataSeeder:
    """Generador profesional de datos operativos"""
    
    # Rangos normales de parámetros operacionales
    NORMAL_RANGES = {
        'turbedad_ac': (5.0, 35.0),      # Agua cruda: 5-35 FTU
        'turbedad_at': (0.1, 0.8),       # Agua tratada: 0.1-0.8 FTU (objetivo < 1 FTU)
        'ph_ac': (6.5, 7.8),             # pH agua cruda
        'ph_sulf': (6.2, 7.0),           # pH con sulfato (baja por acidez)
        'ph_at': (7.0, 8.5),             # pH agua tratada (objetivo 7.0-8.5)
        'dosis_sulfato': (0.5, 3.0),     # l/s
        'dosis_cal': (0.2, 1.5),         # l/s
        'dosis_floergel': (0.1, 0.5),    # l/s
        'ff': (1.5, 3.5),                # Factor de forma
        'clarificacion_is': (100, 500),  # K/Cm³
        'clarificacion_cs': (80, 450),   # K/Cm³
        'clarificacion_fs': (60, 400),   # K/Cm³
        'presion_psi': (20, 45),         # PSI
        'presion_pre': (50, 150),        # Kg/h
        'presion_pos': (40, 120),        # Kg/h
        'cloro_residual': (0.5, 2.0),    # mg/l (objetivo 0.5-2.0)
    }
    
    # Horarios de operación (cada 2 horas)
    OPERATION_HOURS = [
        time(6, 0),   # 6:00 AM
        time(8, 0),   # 8:00 AM
        time(10, 0),  # 10:00 AM
        time(12, 0),  # 12:00 PM
        time(14, 0),  # 2:00 PM
        time(16, 0),  # 4:00 PM
        time(18, 0),  # 6:00 PM
        time(20, 0),  # 8:00 PM
    ]
    
    COLORS = ['Transparente', 'Ligeramente Turbio', 'Turbio Claro', 'Turbio']
    
    def __init__(self, db: Session):
        self.db = db
        self.usuario_operador = self._get_or_create_operator()
        
    def _get_or_create_operator(self) -> Usuario:
        """Obtiene o crea usuario operador para los registros"""
        # Primero intentar encontrar usuario operador
        operador = self.db.query(Usuario).filter(Usuario.username == "operador").first()
        if operador:
            return operador
        
        # Buscar cualquier usuario existente
        operador = self.db.query(Usuario).first()
        if operador:
            print(f"✅ Usando usuario existente: {operador.username}")
            return operador
        
        # No hay usuarios, necesitamos crear uno
        print("⚠️  No hay usuarios en la BD. Creando usuario operador...")
        from models import Rol
        
        # Buscar rol existente
        rol = self.db.query(Rol).filter(Rol.codigo == "OPERADOR").first()
        if not rol:
            # Crear rol con todos los campos requeridos
            rol = Rol(
                codigo="OPERADOR",
                nombre="Operador",
                descripcion="Operador de planta",
                nivel_jerarquia=3,
                categoria="Operativo",
                activo=True
            )
            self.db.add(rol)
            self.db.flush()
            print("✅ Rol Operador creado")
        
        # Crear usuario operador
        operador = Usuario(
            username="operador",
            nombre="Operador",
            apellido="Sistema",
            email="operador@laplanta.com",
            hashed_password=generate_password_hash("operador123"),
            rol_id=rol.id,
            activo=True
        )
        self.db.add(operador)
        self.db.commit()
        print("✅ Usuario operador creado (user: operador, pass: operador123)")
        
        return operador
    
    def _random_in_range(self, param_name: str, anomaly: bool = False) -> Decimal:
        """Genera valor aleatorio dentro del rango normal o anómalo"""
        min_val, max_val = self.NORMAL_RANGES[param_name]
        
        if anomaly:
            # Anomalía: valor fuera del rango normal
            if random.random() > 0.5:
                # Valor alto anómalo
                value = max_val + random.uniform(0.1, 0.3) * (max_val - min_val)
            else:
                # Valor bajo anómalo (si aplica)
                value = max(0, min_val - random.uniform(0.1, 0.2) * (max_val - min_val))
        else:
            # Valor normal con pequeña variación
            value = random.uniform(min_val, max_val)
        
        return Decimal(str(round(value, 2)))
    
    def _generate_correlated_values(self, turbedad_ac: Decimal, is_anomaly: bool = False):
        """Genera valores correlacionados basados en la turbidez del agua cruda"""
        
        # Turbidez tratada debe ser mucho menor que la cruda
        turbedad_ac_float = float(turbedad_ac)
        
        if is_anomaly:
            # Anomalía: agua tratada con alta turbidez (mala filtración)
            turbedad_at = Decimal(str(round(random.uniform(1.2, 2.5), 2)))
        else:
            # Normal: reducción de 95-99% de turbidez
            turbedad_at = Decimal(str(round(turbedad_ac_float * random.uniform(0.01, 0.05), 2)))
            turbedad_at = max(Decimal('0.1'), min(turbedad_at, Decimal('0.8')))
        
        # Dosis de químicos proporcional a la turbidez del agua cruda
        turbidez_factor = turbedad_ac_float / 20.0  # Normalizar sobre 20 FTU
        
        dosis_sulfato = Decimal(str(round(0.5 + turbidez_factor * 2.0 + random.uniform(-0.2, 0.2), 3)))
        dosis_cal = Decimal(str(round(0.3 + turbidez_factor * 1.0 + random.uniform(-0.1, 0.1), 3)))
        dosis_floergel = Decimal(str(round(0.15 + turbidez_factor * 0.3 + random.uniform(-0.05, 0.05), 3)))
        
        # Color correlacionado con turbidez
        if turbedad_ac_float < 10:
            color = 'Transparente'
        elif turbedad_ac_float < 20:
            color = 'Ligeramente Turbio'
        elif turbedad_ac_float < 30:
            color = 'Turbio Claro'
        else:
            color = 'Turbio'
        
        return {
            'turbedad_at': turbedad_at,
            'dosis_sulfato': dosis_sulfato,
            'dosis_cal': dosis_cal,
            'dosis_floergel': dosis_floergel,
            'color': color
        }
    
    def _generate_observation(self, is_anomaly: bool, anomaly_type: str = None) -> str:
        """Genera observación descriptiva"""
        if is_anomaly:
            observations = {
                'turbidez_alta': 'Alta turbidez en agua tratada. Verificar sistema de filtración.',
                'ph_bajo': 'pH fuera de rango normal. Ajustar dosificación de cal.',
                'cloro_bajo': 'Cloro residual bajo. Aumentar dosificación.',
                'presion_alta': 'Presión elevada. Verificar válvulas y filtros.',
            }
            return observations.get(anomaly_type, 'Parámetros fuera de rango normal.')
        
        normal_obs = [
            'Operación normal',
            'Sistema funcionando correctamente',
            'Parámetros dentro de rango',
            'Sin novedad',
            'Operación estable',
        ]
        return random.choice(normal_obs)
    
    def generate_day_data(self, fecha: date, anomaly_probability: float = 0.15):
        """Genera todos los registros de un día"""
        records = []
        
        for hora in self.OPERATION_HOURS:
            # Decidir si este registro tendrá anomalía
            has_anomaly = random.random() < anomaly_probability
            anomaly_type = None
            
            if has_anomaly:
                anomaly_type = random.choice([
                    'turbidez_alta', 'ph_bajo', 'cloro_bajo', 'presion_alta'
                ])
            
            # Generar turbidez de agua cruda (base)
            turbedad_ac = self._random_in_range('turbedad_ac', anomaly=False)
            
            # Generar valores correlacionados
            correlated = self._generate_correlated_values(
                turbedad_ac, 
                is_anomaly=(has_anomaly and anomaly_type == 'turbidez_alta')
            )
            
            # pH
            ph_ac = self._random_in_range('ph_ac', anomaly=False)
            ph_sulf = Decimal(str(round(float(ph_ac) - random.uniform(0.3, 0.8), 2)))
            
            if has_anomaly and anomaly_type == 'ph_bajo':
                ph_at = Decimal(str(round(random.uniform(6.0, 6.8), 2)))
            else:
                ph_at = self._random_in_range('ph_at', anomaly=False)
            
            # Cloro residual
            if has_anomaly and anomaly_type == 'cloro_bajo':
                cloro_residual = Decimal(str(round(random.uniform(0.2, 0.4), 2)))
            else:
                cloro_residual = self._random_in_range('cloro_residual', anomaly=False)
            
            # Presiones
            presion_psi = self._random_in_range('presion_psi', anomaly=(has_anomaly and anomaly_type == 'presion_alta'))
            presion_pre = self._random_in_range('presion_pre', anomaly=(has_anomaly and anomaly_type == 'presion_alta'))
            presion_pos = self._random_in_range('presion_pos', anomaly=False)
            presion_total = Decimal(str(round(float(presion_pre) + float(presion_pos), 2)))
            
            # Crear registro
            record = ControlOperacion(
                fecha=fecha,
                hora=hora,
                turbedad_ac=turbedad_ac,
                turbedad_at=correlated['turbedad_at'],
                color=correlated['color'],
                ph_ac=ph_ac,
                ph_sulf=ph_sulf,
                ph_at=ph_at,
                dosis_sulfato=correlated['dosis_sulfato'],
                dosis_cal=correlated['dosis_cal'],
                dosis_floergel=correlated['dosis_floergel'],
                ff=self._random_in_range('ff', anomaly=False),
                clarificacion_is=self._random_in_range('clarificacion_is', anomaly=False),
                clarificacion_cs=self._random_in_range('clarificacion_cs', anomaly=False),
                clarificacion_fs=self._random_in_range('clarificacion_fs', anomaly=False),
                presion_psi=presion_psi,
                presion_pre=presion_pre,
                presion_pos=presion_pos,
                presion_total=presion_total,
                cloro_residual=cloro_residual,
                observaciones=self._generate_observation(has_anomaly, anomaly_type),
                usuario_id=self.usuario_operador.id,
                created_at=datetime.combine(fecha, hora),
                updated_at=datetime.combine(fecha, hora)
            )
            records.append(record)
        
        return records
    
    def seed_last_n_days(self, days: int = 7):
        """Genera datos de los últimos N días"""
        print(f"\n{'='*70}")
        print(f"🌊 SEED DE DATOS OPERACIONALES - PLANTA LA ESPERANZA")
        print(f"{'='*70}\n")
        
        # Verificar si ya hay datos
        existing_count = self.db.query(ControlOperacion).count()
        if existing_count > 0:
            print(f"⚠️  Ya existen {existing_count} registros en control_operacion")
            response = input("¿Desea eliminarlos y crear nuevos? (s/n): ").lower()
            if response == 's':
                print("🗑️  Eliminando registros existentes...")
                self.db.query(ControlOperacion).delete()
                self.db.commit()
                print("✅ Registros eliminados")
            else:
                print("❌ Operación cancelada")
                return
        
        print(f"📅 Generando datos de los últimos {days} días...")
        print(f"⏰ Registros por día: {len(self.OPERATION_HOURS)}\n")
        
        today = date.today()
        total_records = 0
        anomaly_count = 0
        
        for i in range(days):
            current_date = today - timedelta(days=days - i - 1)
            
            # Variar probabilidad de anomalías (algunos días más problemáticos)
            if i % 3 == 0:  # Cada 3 días más anomalías
                anomaly_prob = 0.25
            else:
                anomaly_prob = 0.10
            
            records = self.generate_day_data(current_date, anomaly_probability=anomaly_prob)
            
            # Contar anomalías
            day_anomalies = sum(1 for r in records if 'fuera de rango' in r.observaciones.lower() 
                               or 'alta turbidez' in r.observaciones.lower()
                               or 'verificar' in r.observaciones.lower())
            
            self.db.bulk_save_objects(records)
            self.db.commit()
            
            total_records += len(records)
            anomaly_count += day_anomalies
            
            print(f"  ✅ {current_date} | {len(records)} registros | {day_anomalies} anomalías")
        
        print(f"\n{'='*70}")
        print(f"✅ SEED COMPLETADO EXITOSAMENTE")
        print(f"{'='*70}")
        print(f"📊 Total registros insertados: {total_records}")
        print(f"⚠️  Registros con anomalías: {anomaly_count}")
        print(f"📈 Tasa de anomalías: {(anomaly_count/total_records*100):.1f}%")
        print(f"📅 Rango de fechas: {today - timedelta(days=days-1)} a {today}")
        print(f"\n🚀 Listo para probar el sistema de ML y detección de anomalías\n")


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🌊 SISTEMA DE SEED DE DATOS OPERACIONALES")
    print("   Planta de Tratamiento La Esperanza")
    print("="*70 + "\n")
    
    # Crear tablas si no existen
    print("🔧 Verificando estructura de base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos lista\n")
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        seeder = OperationalDataSeeder(db)
        
        # Pedir número de días
        try:
            days_input = input("¿Cuántos días de datos desea generar? [7]: ").strip()
            days = int(days_input) if days_input else 7
            days = max(1, min(days, 30))  # Entre 1 y 30 días
        except ValueError:
            days = 7
            print(f"⚠️  Valor inválido, usando valor por defecto: {days} días")
        
        # Generar datos
        seeder.seed_last_n_days(days)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
