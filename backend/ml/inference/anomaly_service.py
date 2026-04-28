"""
Servicio de detección de anomalías en parámetros operativos.

Identifica valores anormales que pueden indicar problemas en el proceso.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path

from ..domain.entities import AnomalyResult
from ..utils.logger import MLLogger
from ..utils.config_manager import get_config
from ..utils.validation import DataValidator

logger = MLLogger.get_anomaly_logger()
config = get_config()


class AnomalyDetectorService:
    """
    Servicio de detección de anomalías en datos operativos.
    
    Utiliza Isolation Forest para identificar patrones anormales
    en parámetros fisicoquímicos y operativos.
    
    Arquitectura:
    - Strategy Pattern: Diferentes algoritmos de detección
    - Facade: Interfaz simplificada para detección
    """
    
    def __init__(self):
        """Inicializa el detector."""
        self.detector: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns: List[str] = []
        self.thresholds: Dict[str, Dict] = {}
        self._is_trained = False
        
        #Cargar umbrales de configuración
        self._load_thresholds()
    
    def _load_thresholds(self) -> None:
        """Carga umbrales de detección desde configuración."""
        self.thresholds = config.get('anomaly_detection.thresholds', {})
        logger.info(f"Umbrales cargados: {len(self.thresholds)} parámetros")
    
    def train_detector(
        self,
        df: pd.DataFrame,
        contamination: float = 0.05
    ) -> None:
        """
        Entrena el detector de anomalías con datos históricos normales.
        
        Args:
            df: DataFrame con datos históricos
            contamination: Proporción esperada de anomalías (0-0.5)
        """
        logger.info("Entrenando detector de anomalías")
        
        # Seleccionar columnas relevantes
        self.feature_columns = [
            'turbedad_ac', 'turbedad_at', 'ph_ac', 'ph_at',
            'temperatura_ac', 'cloro_residual', 'presion_total'
        ]
        
        # Filtrar columnas disponibles
        available_cols = [col for col in self.feature_columns if col in df.columns]
        
        if not available_cols:
            raise ValueError("No hay columnas válidas para entrenamiento")
        
        self.feature_columns = available_cols
        
        # Preparar datos
        X = df[self.feature_columns].copy()
        
        # Manejar valores faltantes
        X = X.fillna(X.median())
        
        # Escalar features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Entrenar Isolation Forest
        self.detector = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        
        self.detector.fit(X_scaled)
        self._is_trained = True
        
        logger.info(f"Detector entrenado con {len(X)} muestras")
        logger.info(f"Features utilizadas: {self.feature_columns}")
    
    def detect_anomalies(
        self,
        df: pd.DataFrame,
        use_model: bool = True,
        use_thresholds: bool = True
    ) -> pd.DataFrame:
        """
        Detecta anomalías en un DataFrame de datos.
        
        Args:
            df: DataFrame con datos a analizar
            use_model: Usar modelo ML para detección
            use_thresholds: Usar umbrales definidos
            
        Returns:
            DataFrame con columnas adicionales de detección
        """
        logger.info(f"Analizando anomalías en {len(df)} registros")
        
        df_result = df.copy()
        df_result['is_anomaly'] = False
        df_result['anomaly_score'] = 0.0
        df_result['anomaly_reason'] = ""
        df_result['severity'] = "normal"
        
        # Detección basada en modelo ML
        if use_model and self._is_trained:
            df_result = self._detect_with_model(df_result)
        
        # Detección basada en umbrales
        if use_thresholds:
            df_result = self._detect_with_thresholds(df_result)
        
        # Clasificar severidad
        df_result = self._classify_severity(df_result)
        
        anomaly_count = df_result['is_anomaly'].sum()
        logger.info(f"Anomalías detectadas: {anomaly_count} ({anomaly_count/len(df)*100:.1f}%)")
        
        return df_result
    
    def _detect_with_model(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta anomalías usando Isolation Forest.
        
        Args:
            df: DataFrame con datos
            
        Returns:
            DataFrame con detecciones del modelo
        """
        if not self._is_trained:
            logger.warning("Detector no entrenado, saltando detección por modelo")
            return df
        
        # Preparar features
        available_cols = [col for col in self.feature_columns if col in df.columns]
        
        if not available_cols:
            return df
        
        X = df[available_cols].copy()
        X = X.fillna(X.median())
        
        try:
            X_scaled = self.scaler.transform(X)
            
            # Predecir (-1 = anomalía, 1 = normal)
            predictions = self.detector.predict(X_scaled)
            scores = self.detector.score_samples(X_scaled)
            
            # Marcar anomalías
            is_anomaly_model = predictions == -1
            df.loc[is_anomaly_model, 'is_anomaly'] = True
            df['anomaly_score'] = scores
            
            # Agregar razón
            df.loc[is_anomaly_model, 'anomaly_reason'] += "Patrón anormal detectado por ML; "
        
        except Exception as e:
            logger.error(f"Error en detección ML: {e}")
        
        return df
    
    def _detect_with_thresholds(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta anomalías usando umbrales definidos.
        
        Args:
            df: DataFrame con datos
            
        Returns:
            DataFrame con detecciones por umbrales
        """
        for param, thresholds in self.thresholds.items():
            if param not in df.columns:
                continue
            
            min_val = thresholds.get('min')
            max_val = thresholds.get('max')
            critical_min = thresholds.get('critical_min')
            critical_max = thresholds.get('critical_max')
            
            # Detectar valores fuera de rango normal
            if min_val is not None:
                mask = df[param] < min_val
                df.loc[mask, 'is_anomaly'] = True
                df.loc[mask, 'anomaly_reason'] += f"{param} < {min_val}; "
            
            if max_val is not None:
                mask = df[param] > max_val
                df.loc[mask, 'is_anomaly'] = True
                df.loc[mask, 'anomaly_reason'] += f"{param} > {max_val}; "
            
            # Detectar valores críticos
            if critical_min is not None:
                mask = df[param] < critical_min
                df.loc[mask, 'severity'] = "critico"
                df.loc[mask, 'anomaly_reason'] += f"{param} CRÍTICO < {critical_min}; "
            
            if critical_max is not None:
                mask = df[param] > critical_max
                df.loc[mask, 'severity'] = "critico"
                df.loc[mask, 'anomaly_reason'] += f"{param} CRÍTICO > {critical_max}; "
        
        return df
    
    def _classify_severity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clasifica severidad de anomalías basado en score.
        
        Args:
            df: DataFrame con anomalías detectadas
            
        Returns:
            DataFrame con severidad clasificada
        """
        # Solo para anomalías detectadas por modelo
        mask_anomaly = df['is_anomaly'] & (df['severity'] == "normal")
        
        if mask_anomaly.any():
            scores = df.loc[mask_anomaly, 'anomaly_score']
            
            # Clasificar por rangos de score
            # Isolation Forest: scores más negativos = más anómalos
            df.loc[mask_anomaly & (scores < -0.3), 'severity'] = "critico"
            df.loc[mask_anomaly & (scores >= -0.3) & (scores < -0.1), 'severity'] = "sospechoso"
        
        return df
    
    def analyze_operational_data(
        self,
        df: pd.DataFrame,
        fecha_column: str = 'fecha',
        hora_column: str = 'hora'
    ) -> List[AnomalyResult]:
        """
        Analiza datos operativos y genera lista de anomalías.
        
        Args:
            df: DataFrame con datos operativos
            fecha_column: Nombre de columna de fecha
            hora_column: Nombre de columna de hora
            
        Returns:
            Lista de AnomalyResult
        """
        logger.info("Analizando datos operativos para anomalías")
        
        # Detectar anomalías
        df_analyzed = self.detect_anomalies(df)
        
        # Filtrar solo anomalías
        df_anomalies = df_analyzed[df_analyzed['is_anomaly']].copy()
        
        # Convertir a AnomalyResult
        results = []
        
        for _, row in df_anomalies.iterrows():
            # Identificar parámetro principal anómalo
            parametro = "desconocido"
            valor = 0.0
            
            # Extraer del anomaly_reason
            reason = row.get('anomaly_reason', '')
            if 'turbedad_ac' in reason:
                parametro = 'turbedad_ac'
                valor = row.get('turbedad_ac', 0)
            elif 'ph_ac' in reason:
                parametro = 'ph_ac'
                valor = row.get('ph_ac', 0)
            elif 'cloro_residual' in reason:
                parametro = 'cloro_residual'
                valor = row.get('cloro_residual', 0)
            
            result = AnomalyResult(
                fecha=row[fecha_column] if fecha_column in row else date.today(),
                hora=row[hora_column] if hora_column in row else datetime.now().time(),
                parametro=parametro,
                valor=float(valor),
                es_anomalia=True,
                severidad=row.get('severity', 'sospechoso'),
                anomaly_score=float(row.get('anomaly_score', 0)),
                explicacion=reason.strip('; ')
            )
            
            results.append(result)
        
        logger.info(f"Anomalías encontradas: {len(results)}")
        
        return results
    
    def save_detector(self, path: Path) -> None:
        """
        Guarda el detector entrenado.
        
        Args:
            path: Directorio donde guardar
        """
        if not self._is_trained:
            raise ValueError("Detector no entrenado")
        
        path.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.detector, path / "anomaly_detector.pkl")
        joblib.dump(self.scaler, path / "anomaly_scaler.pkl")
        joblib.dump(self.feature_columns, path / "anomaly_features.pkl")
        
        logger.info(f"Detector guardado en {path}")
    
    @classmethod
    def load_detector(cls, path: Path) -> 'AnomalyDetectorService':
        """
        Carga un detector guardado.
        
        Args:
            path: Directorio donde está guardado
            
        Returns:
            Instancia de AnomalyDetectorService
        """
        service = cls()
        
        detector_file = path / "anomaly_detector.pkl"
        if detector_file.exists():
            service.detector = joblib.load(detector_file)
            service.scaler = joblib.load(path / "anomaly_scaler.pkl")
            service.feature_columns = joblib.load(path / "anomaly_features.pkl")
            service._is_trained = True
            logger.info("Detector cargado")
        
        return service
