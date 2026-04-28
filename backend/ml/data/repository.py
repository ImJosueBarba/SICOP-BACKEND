"""
Repositorio para acceso a datos operativos de la planta.

Implementa el patrón Repository para abstraer el acceso a datos
y permitir sustitución de la fuente de datos si es necesario.
"""

from typing import Optional, List
from datetime import date, datetime, time
from decimal import Decimal
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract

# Imports de modelos SQLAlchemy (del proyecto existente)
from models.control_operacion import ControlOperacion
from models.consumo_quimico_mensual import ConsumoQuimicoMensual
from models.monitoreo_fisicoquimico import MonitoreoFisicoquimico
from models.produccion_filtro import ProduccionFiltro

from ..domain.entities import OperationalData, ChemicalConsumption
from ..utils.logger import MLLogger
from ..utils.validation import DataValidator, InsufficientDataError


logger = MLLogger.get_training_logger()


class PlantDataRepository:
    """
    Repositorio para acceder a datos históricos de la planta.
    
    Proporciona métodos para extraer, combinar y preparar datos
    de múltiples tablas para entrenamiento de modelos ML.
    
    Principios aplicados:
    - Single Responsibility: Solo acceso a datos
    - Dependency Inversion: Depende de abstracciones (Session)
    - Interface Segregation: Métodos específicos por necesidad
    """
    
    def __init__(self, db_session: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.
        
        Args:
            db_session: Sesión de SQLAlchemy
        """
        self.db = db_session
    
    def get_operational_data(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Obtiene datos de control de operación.
        
        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            limit: Número máximo de registros (opcional)
            
        Returns:
            DataFrame con datos operativos
            
        Raises:
            InsufficientDataError: Si no hay suficientes datos
        """
        logger.info(f"Obteniendo datos operativos desde {start_date} hasta {end_date}")
        
        query = self.db.query(ControlOperacion)
        
        if start_date:
            query = query.filter(ControlOperacion.fecha >= start_date)
        if end_date:
            query = query.filter(ControlOperacion.fecha <= end_date)
        
        query = query.order_by(ControlOperacion.fecha, ControlOperacion.hora)
        
        if limit:
            query = query.limit(limit)
        
        results = query.all()
        
        if not results:
            raise InsufficientDataError(
                "No se encontraron datos operativos en el rango especificado"
            )
        
        # Convertir a DataFrame
        data = []
        for record in results:
            data.append({
                'fecha': record.fecha,
                'hora': record.hora,
                'turbedad_ac': float(record.turbedad_ac) if record.turbedad_ac else None,
                'turbedad_at': float(record.turbedad_at) if record.turbedad_at else None,
                'ph_ac': float(record.ph_ac) if record.ph_ac else None,
                'ph_sulfato': float(record.ph_sulf) if record.ph_sulf else None,
                'ph_at': float(record.ph_at) if record.ph_at else None,
                'dosis_sulfato': float(record.dosis_sulfato) if record.dosis_sulfato else None,
                'dosis_cal': float(record.dosis_cal) if record.dosis_cal else None,
                'dosis_floergel': float(record.dosis_floergel) if record.dosis_floergel else None,
                'presion_total': float(record.presion_total) if record.presion_total else None,
                'cloro_residual': float(record.cloro_residual) if record.cloro_residual else None,
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Datos operativos obtenidos: {len(df)} registros")
        
        return df
    
    def get_physicochemical_data(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Obtiene datos de monitoreo fisicoquímico.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            DataFrame con datos fisicoquímicos
        """
        logger.info("Obteniendo datos fisicoquímicos")
        
        query = self.db.query(MonitoreoFisicoquimico)
        
        if start_date:
            query = query.filter(MonitoreoFisicoquimico.fecha >= start_date)
        if end_date:
            query = query.filter(MonitoreoFisicoquimico.fecha <= end_date)
        
        query = query.order_by(MonitoreoFisicoquimico.fecha, MonitoreoFisicoquimico.hora)
        results = query.all()
        
        if not results:
            logger.warning("No se encontraron datos fisicoquímicos")
            return pd.DataFrame()
        
        data = []
        for record in results:
            data.append({
                'fecha': record.fecha,
                'hora': record.hora,
                'muestra_numero': record.muestra_numero,
                'temperatura_ac': float(record.ac_temperatura) if record.ac_temperatura else None,
                'temperatura_at': float(record.at_temperatura) if record.at_temperatura else None,
                'conductividad_ac': float(record.ac_ce) if record.ac_ce else None,
                'conductividad_at': float(record.at_ce) if record.at_ce else None,
                'tds_ac': float(record.ac_tds) if record.ac_tds else None,
                'tds_at': float(record.at_tds) if record.at_tds else None,
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Datos fisicoquímicos obtenidos: {len(df)} registros")
        
        return df
    
    def get_chemical_consumption(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Obtiene datos de consumo mensual de químicos.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            DataFrame con consumo de químicos
            
        Raises:
            InsufficientDataError: Si no hay suficientes datos
        """
        logger.info("Obteniendo datos de consumo de químicos")
        
        query = self.db.query(ConsumoQuimicoMensual)
        
        if start_date:
            query = query.filter(ConsumoQuimicoMensual.fecha >= start_date)
        if end_date:
            query = query.filter(ConsumoQuimicoMensual.fecha <= end_date)
        
        query = query.order_by(ConsumoQuimicoMensual.anio, ConsumoQuimicoMensual.mes)
        results = query.all()
        
        if not results:
            raise InsufficientDataError(
                "No se encontraron datos de consumo de químicos"
            )
        
        data = []
        for record in results:
            data.append({
                'fecha': record.fecha,
                'mes': record.mes,
                'anio': record.anio,
                'sulfato_consumo_kg': float(record.sulfato_con) if record.sulfato_con else None,
                'cal_consumo_kg': float(record.cal_con) if record.cal_con else None,
                'hipoclorito_consumo_kg': float(record.hipoclorito_con) if record.hipoclorito_con else None,
                'cloro_gas_consumo_kg': float(record.cloro_gas_con) if record.cloro_gas_con else None,
                'produccion_m3': float(record.produccion_m3_dia) if record.produccion_m3_dia else None,
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Consumo de químicos obtenido: {len(df)} registros (meses)")
        
        return df
    
    def get_production_data(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Obtiene datos de producción de filtros.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            DataFrame con datos de producción
        """
        logger.info("Obteniendo datos de producción")
        
        query = self.db.query(ProduccionFiltro)
        
        if start_date:
            query = query.filter(ProduccionFiltro.fecha >= start_date)
        if end_date:
            query = query.filter(ProduccionFiltro.fecha <= end_date)
        
        query = query.order_by(ProduccionFiltro.fecha)
        results = query.all()
        
        if not results:
            logger.warning("No se encontraron datos de producción")
            return pd.DataFrame()
        
        data = []
        for record in results:
            data.append({
                'fecha': record.fecha,
                'caudal_total': float(record.caudal_total) if record.caudal_total else None,
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Datos de producción obtenidos: {len(df)} registros")
        
        return df
    
    def get_combined_dataset(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_samples: int = 90
    ) -> pd.DataFrame:
        """
        Obtiene dataset combinado para entrenamiento de modelos.
        
        Combina datos de diferentes tablas:
        - Control de operación (features principales)
        - Monitoreo fisicoquímico (temperatura, conductividad)
        - Producción (caudal)
        - Consumo de químicos (targets)
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            min_samples: Mínimo de muestras requeridas
            
        Returns:
            DataFrame combinado con features y targets
            
        Raises:
            InsufficientDataError: Si no hay suficientes datos
        """
        logger.info("Construyendo dataset combinado para ML")
        
        # 1. Obtener datos operativos (base)
        df_operational = self.get_operational_data(start_date, end_date)
        
        # 2. Obtener datos fisicoquímicos
        df_physico = self.get_physicochemical_data(start_date, end_date)
        
        # 3. Obtener producción
        df_production = self.get_production_data(start_date, end_date)
        
        # 4. Combinar operational + fisicoquímico (por fecha)
        if not df_physico.empty:
            # Agrupar fisicoquímico por fecha (promedio diario)
            df_physico_daily = df_physico.groupby('fecha').agg({
                'temperatura_ac': 'mean',
                'temperatura_at': 'mean',
                'conductividad_ac': 'mean',
                'conductividad_at': 'mean',
                'tds_ac': 'mean',
                'tds_at': 'mean',
            }).reset_index()
            
            df_operational = df_operational.merge(
                df_physico_daily,
                on='fecha',
                how='left'
            )
        
        # 5. Combinar con producción (caudal)
        if not df_production.empty:
            df_operational = df_operational.merge(
                df_production,
                on='fecha',
                how='left'
            )
        
        # 6. Agregar datos de consumo mensual
        df_consumption = self.get_chemical_consumption(start_date, end_date)
        
        # Crear columna año-mes para merge
        df_operational['anio'] = pd.to_datetime(df_operational['fecha']).dt.year
        df_operational['mes'] = pd.to_datetime(df_operational['fecha']).dt.month
        
        # Merge con consumo mensual
        df_combined = df_operational.merge(
            df_consumption[['anio', 'mes', 'sulfato_consumo_kg', 'cal_consumo_kg',
                           'hipoclorito_consumo_kg', 'cloro_gas_consumo_kg']],
            on=['anio', 'mes'],
            how='left'
        )
        
        # 7. Validar cantidad de datos
        if len(df_combined) < min_samples:
            raise InsufficientDataError(
                f"Datos insuficientes: {len(df_combined)} registros, "
                f"mínimo requerido: {min_samples}"
            )
        
        logger.info(f"Dataset combinado creado: {len(df_combined)} registros, "
                   f"{df_combined.shape[1]} columnas")
        
        return df_combined
    
    def get_data_statistics(self) -> dict:
        """
        Obtiene estadísticas generales de los datos disponibles.
        
        Returns:
            Diccionario con estadísticas
        """
        stats = {}
        
        # Contar registros por tabla
        stats['total_operational_records'] = self.db.query(ControlOperacion).count()
        stats['total_consumption_records'] = self.db.query(ConsumoQuimicoMensual).count()
        stats['total_physicochemical_records'] = self.db.query(MonitoreoFisicoquimico).count()
        
        # Rango de fechas
        min_date = self.db.query(func.min(ControlOperacion.fecha)).scalar()
        max_date = self.db.query(func.max(ControlOperacion.fecha)).scalar()
        
        stats['date_range'] = {
            'start': min_date.isoformat() if min_date else None,
            'end': max_date.isoformat() if max_date else None,
            'days': (max_date - min_date).days if min_date and max_date else 0
        }
        
        return stats
