"""
Script de entrenamiento rápido de modelo ML.

Ejecuta el pipeline completo de entrenamiento con configuración por defecto.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from ml.data.repository import PlantDataRepository
from ml.data.preprocessor import DataPreprocessor
from ml.features.feature_engineer import FeatureEngineer
from ml.models.trainer import ChemicalConsumptionTrainer
from ml.models.evaluator import ModelEvaluator
from ml.utils.logger import MLLogger
from ml.utils.config_manager import get_config
from ml.utils.validation import InsufficientDataError

logger = MLLogger.get_training_logger()
config = get_config()


def main():
    """
    Pipeline completo de entrenamiento.
    """
    print("=" * 80)
    print("Sistema ML - Optimización de Consumo de Químicos")
    print("Planta de Tratamiento de Agua 'La Esperanza'")
    print("="  * 80)
    print()
    
    try:
        # 1. Conectar a base de datos
        print("📊 Paso 1: Conectando a base de datos...")
        db: Session = SessionLocal()
        
        # 2. Obtener datos históricos
        print("📊 Paso 2: Extrayendo datos históricos...")
        repository = PlantDataRepository(db)
        
        # Obtener estadísticas
        stats = repository.get_data_statistics()
        print(f"   ├─ Registros operativos: {stats['total_operational_records']}")
        print(f"   ├─ Registros de consumo: {stats['total_consumption_records']}")
        print(f"   └─ Rango de fechas: {stats['date_range']['start']} a {stats['date_range']['end']}")
        
        # Obtener dataset combinado
        end_date = date.today()
        start_date = end_date - timedelta(days=180)  # Últimos 6 meses
        
        print(f"\n   Obteniendo datos desde {start_date} hasta {end_date}...")
        df = repository.get_combined_dataset(start_date=start_date, end_date=end_date)
        print(f"   ✓ Dataset obtenido: {len(df)} registros, {df.shape[1]} columnas")
        
        # 3. Feature Engineering
        print("\n🔧 Paso 3: Aplicando Feature Engineering...")
        df_engineered = FeatureEngineer.engineer_features(
            df,
            create_ratios=True,
            create_deltas=True,
            create_interactions=True,
            create_temporal=True,
            create_rolling=False,  # Opcional: más costoso
            create_lags=False  # Opcional: más costoso
        )
        print(f"   ✓ Features creadas: {df_engineered.shape[1]} columnas totales")
        
        # 4. Preprocesamiento
        print("\n🧹 Paso 4: Preprocesando datos...")
        preprocessor = DataPreprocessor(scaling_method=config.scaling_method)
        
        target_columns = config.target_variables
        print(f"   Variables objetivo: {target_columns}")
        
        X, y = preprocessor.prepare_dataset(
            df_engineered,
            target_columns=target_columns,
            handle_outliers_flag=True,
            scale=True
        )
        print(f"   ✓ Datos preparados: X{X.shape}, y{y.shape}")
        
        # 5. Entrenamiento
        print("\n🤖 Paso 5: Entrenando modelos...")
        print(f"   Modelos habilitados: {config.enabled_models}")
        
        trainer = ChemicalConsumptionTrainer()
        
        # Split data
        X_train, X_val, X_test, y_train, y_val, y_test = trainer.split_data(X, y)
        print(f"   ├─ Train: {X_train.shape}")
        print(f"   ├─ Validation: {X_val.shape}")
        print(f"   └─ Test: {X_test.shape}")
        
        # Train all models
        print("\n   Entrenando modelos (esto puede tardar varios minutos)...")
        scores = trainer.train_all_models(
            X_train, y_train,
            X_val, y_val,
            perform_cv=True
        )
        
        # 6. Selección del mejor modelo
        print("\n🏆 Paso 6: Seleccionando mejor modelo...")
        best_name, best_model = trainer.select_best_model()
        best_metrics = scores[best_name]
        
        print(f"   ✓ Mejor modelo: {best_name}")
        print(f"   └─ Métricas:")
        print(f"      ├─ MAE: {best_metrics['mae']:.2f}")
        print(f"      ├─ RMSE: {best_metrics['rmse']:.2f}")
        print(f"      ├─ R²: {best_metrics['r2']:.4f}")
        print(f"      └─ MAPE: {best_metrics.get('mape', 0):.2f}%")
        
        # 7. Feature Importance
        print("\n📈 Paso 7: Analizando importancia de features...")
        importance = trainer.extract_feature_importance(
            feature_names=preprocessor.feature_names,
            top_n=10
        )
        
        if not importance.empty:
            print("   Top 10 features más importantes:")
            for idx, row in importance.head(10).iterrows():
                print(f"      {idx+1}. {row['feature']}: {row['importance']:.4f}")
        
        # 8. Evaluación en test set
        print("\n✅ Paso 8: Evaluando en test set...")
        y_test_pred = best_model.predict(X_test)
        test_metrics = ModelEvaluator.calculate_metrics(
            y_test, y_test_pred,
            target_names=target_columns
        )
        
        print("   Métricas por químico:")
        for chemical, metrics in test_metrics.items():
            if chemical != 'average' and isinstance(metrics, dict):
                print(f"   └─ {chemical}:")
                print(f"      ├─ MAE: {metrics['MAE']:.2f} kg")
                print(f"      ├─ RMSE: {metrics['RMSE']:.2f} kg")
                print(f"      ├─ R²: {metrics['R2']:.4f}")
                print(f"      └─ MAPE: {metrics.get('MAPE', 0):.2f}%")
        
        # 9. Verificar umbrales
        print("\n🎯 Paso 9: Verificando umbrales de aceptación...")
        avg_metrics = test_metrics.get('average', {})
        passes, warnings = ModelEvaluator.check_thresholds(
            avg_metrics,
            min_r2=config.min_r2_score,
            max_mape=15.0
        )
        
        if passes:
            print("   ✓ El modelo cumple todos los umbrales de calidad")
        else:
            print("   ⚠ Advertencias:")
            for warning in warnings:
                print(f"      - {warning}")
        
        # 10. Guardar modelo
        print("\n💾 Paso 10: Guardando modelo...")
        model_path = trainer.save_model(preprocessor)
        print(f"   ✓ Modelo guardado en: {model_path}")
        
        # Resumen final
        print("\n" + "=" * 80)
        print("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print(f"Modelo: {best_name}")
        print(f"R² Score: {avg_metrics.get('R2', 0):.4f}")
        print(f"RMSE: {avg_metrics.get('RMSE', 0):.2f} kg")
        print(f"Ruta: {model_path}")
        print("\nEl modelo está listo para uso en producción.")
        print("Para cargar el modelo en la API, ejecute: python -m uvicorn main:app --reload")
        print("=" * 80)
        
    except InsufficientDataError as e:
        logger.error(f"Datos insuficientes: {e}")
        print(f"\n❌ ERROR: {e}")
        print("\nAsegúrese de tener al menos 90 días de datos en la base de datos.")
        print("Puede insertar datos de prueba ejecutando: python insert_test_data.py")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error en entrenamiento: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}")
        print("\nRevise los logs en logs/ml_training.log para más detalles.")
        sys.exit(1)
    
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    main()
