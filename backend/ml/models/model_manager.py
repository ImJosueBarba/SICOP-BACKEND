"""
Gestor de modelos entrenados.

Maneja carga, versionado y selección de modelos en producción.
"""

from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime
import joblib
import json

from ..utils.logger import MLLogger
from ..utils.config_manager import get_config
from ..utils.validation import ModelNotFoundError

logger = MLLogger.get_inference_logger()
config = get_config()


class ModelManager:
    """
    Gestor de modelos ML entrenados.
    
    Responsabilidades:
    - Cargar modelos guardados
    - Gestionar versiones
    - Mantener histórico
    - Proveer metadata
    
    Principios:
    - Single Responsibility: Solo gestión de modelos
    - Dependency Inversion: No depende de implementaciones específicas
    """
    
    def __init__(self, models_dir: Optional[Path] = None):
        """
        Inicializa el gestor de modelos.
        
        Args:
            models_dir: Directorio raíz de modelos (opcional)
        """
        self.models_dir = models_dir or config.models_dir
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_model: Optional[Any] = None
        self.current_preprocessor: Optional[Any] = None
        self.current_metadata: Optional[Dict] = None
        self.model_path: Optional[Path] = None
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        Lista todos los modelos disponibles.
        
        Returns:
            Lista de diccionarios con información de modelos
        """
        models_info = []
        
        if not self.models_dir.exists():
            logger.warning(f"Directorio de modelos no existe: {self.models_dir}")
            return models_info
        
        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir() and (model_dir / "model.pkl").exists():
                metadata_path = model_dir / "metadata.pkl"
                
                info = {
                    'path': str(model_dir),
                    'name': model_dir.name,
                    'created': datetime.fromtimestamp(model_dir.stat().st_ctime).isoformat()
                }
                
                # Cargar metadata si existe
                if metadata_path.exists():
                    try:
                        metadata = joblib.load(metadata_path)
                        info['model_name'] = metadata.get('model_name')
                        info['training_date'] = metadata.get('training_date')
                        info['metrics'] = metadata.get('metrics', {})
                    except Exception as e:
                        logger.warning(f"Error cargando metadata de {model_dir}: {e}")
                
                models_info.append(info)
        
        # Ordenar por fecha de creación (más reciente primero)
        models_info.sort(key=lambda x: x['created'], reverse=True)
        
        logger.info(f"Modelos disponibles: {len(models_info)}")
        return models_info
    
    def get_latest_model_path(self) -> Optional[Path]:
        """
        Obtiene la ruta del modelo más reciente.
        
        Returns:
            Path del modelo o None si no hay modelos
        """
        models = self.list_available_models()
        
        if not models:
            logger.warning("No hay modelos disponibles")
            return None
        
        latest = models[0]  # Ya está ordenado por fecha
        return Path(latest['path'])
    
    def load_model(
        self,
        model_path: Optional[Path] = None,
        version: Optional[str] = None
    ) -> Tuple[Any, Any, Dict]:
        """
        Carga un modelo entrenado con su preprocesador.
        
        Args:
            model_path: Ruta específica del modelo (opcional)
            version: Versión específica (nombre de directorio) (opcional)
            
        Returns:
            Tupla (model, preprocessor, metadata)
            
        Raises:
            ModelNotFoundError: Si no se encuentra el modelo
        """
        # Determinar qué modelo cargar
        if model_path:
            target_path = model_path
        elif version:
            target_path = self.models_dir / version
        else:
            target_path = self.get_latest_model_path()
        
        if not target_path or not target_path.exists():
            raise ModelNotFoundError(
                f"Modelo no encontrado en: {target_path}"
            )
        
        logger.info(f"Cargando modelo desde: {target_path}")
        
        # Cargar modelo
        model_file = target_path / "model.pkl"
        if not model_file.exists():
            raise ModelNotFoundError(f"Archivo de modelo no encontrado: {model_file}")
        
        model = joblib.load(model_file)
        logger.info("Modelo cargado")
        
        # Cargar preprocesador
        from ..data.preprocessor import DataPreprocessor
        preprocessor = DataPreprocessor.load(target_path)
        logger.info("Preprocesador cargado")
        
        # Cargar metadata
        metadata_file = target_path / "metadata.pkl"
        metadata = {}
        if metadata_file.exists():
            metadata = joblib.load(metadata_file)
            logger.info(f"Metadata cargada: modelo '{metadata.get('model_name')}'")
        
        # Actualizar estado interno
        self.current_model = model
        self.current_preprocessor = preprocessor
        self.current_metadata = metadata
        self.model_path = target_path
        
        return model, preprocessor, metadata
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo actualmente cargado.
        
        Returns:
            Diccionario con información del modelo
        """
        if self.current_model is None:
            return {'status': 'no_model_loaded'}
        
        info = {
            'status': 'loaded',
            'path': str(self.model_path),
            'model_name': self.current_metadata.get('model_name', 'unknown'),
            'training_date': self.current_metadata.get('training_date'),
            'metrics': self.current_metadata.get('metrics', {}),
            'feature_count': len(self.current_metadata.get('feature_names', []))
        }
        
        return info
    
    def cleanup_old_models(self, keep_last_n: int = 5) -> int:
        """
        Limpia modelos antiguos, manteniendo solo los N más recientes.
        
        Args:
            keep_last_n: Número de modelos a mantener
            
        Returns:
            Número de modelos eliminados
        """
        models = self.list_available_models()
        
        if len(models) <= keep_last_n:
            logger.info(f"Solo hay {len(models)} modelos, no se eliminará ninguno")
            return 0
        
        models_to_delete = models[keep_last_n:]
        deleted_count = 0
        
        for model_info in models_to_delete:
            try:
                model_path = Path(model_info['path'])
                
                # Eliminar directorio completo
                import shutil
                shutil.rmtree(model_path)
                
                logger.info(f"Modelo eliminado: {model_path.name}")
                deleted_count += 1
            
            except Exception as e:
                logger.error(f"Error eliminando modelo {model_info['path']}: {e}")
        
        logger.info(f"Limpieza completada: {deleted_count} modelos eliminados")
        return deleted_count
    
    def export_model_summary(self, output_path: Path) -> None:
        """
        Exporta resumen de todos los modelos a JSON.
        
        Args:
            output_path: Ruta del archivo JSON de salida
        """
        models = self.list_available_models()
        
        summary = {
            'total_models': len(models),
            'generated_at': datetime.now().isoformat(),
            'models': models
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resumen exportado a: {output_path}")
