"""
Evaluador de modelos ML.

Proporciona análisis detallado del rendimiento del modelo.
"""

from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error
)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from ..utils.logger import MLLogger

logger = MLLogger.get_training_logger()


class ModelEvaluator:
    """
    Evaluador de modelos para análisis de rendimiento.
    
    Proporciona:
    - Cálculo de múltiples métricas
    - Análisis de residuos
    - Reportes visuales
    - Comparación de modelos
    """
    
    @staticmethod
    def calculate_metrics(
        y_true: pd.DataFrame,
        y_pred: pd.DataFrame,
        target_names: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calcula métricas de regresión para cada target.
        
        Args:
            y_true: Valores reales
            y_pred: Valores predichos
            target_names: Nombres de targets (opcional)
            
        Returns:
            Diccionario con métricas por target
        """
        if target_names is None:
            target_names = [f"target_{i}" for i in range(y_true.shape[1])]
        
        metrics_per_target = {}
        
        for i, target_name in enumerate(target_names):
            y_t = y_true.iloc[:, i] if isinstance(y_true, pd.DataFrame) else y_true[:, i]
            y_p = y_pred[:, i]
            
            mae = mean_absolute_error(y_t, y_p)
            rmse = np.sqrt(mean_squared_error(y_t, y_p))
            r2 = r2_score(y_t, y_p)
            
            # MAPE manual (evitar división por cero)
            mape = np.mean(np.abs((y_t - y_p) / (y_t + 1e-10))) * 100
            
            metrics_per_target[target_name] = {
                'MAE': mae,
                'RMSE': rmse,
                'R2': r2,
                'MAPE': mape
            }
            
            logger.info(f"{target_name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}, "
                       f"R²: {r2:.4f}, MAPE: {mape:.2f}%")
        
        # Métricas agregadas (promedio)
        metrics_per_target['average'] = {
            'MAE': np.mean([m['MAE'] for m in metrics_per_target.values() if isinstance(m, dict)]),
            'RMSE': np.mean([m['RMSE'] for m in metrics_per_target.values() if isinstance(m, dict)]),
            'R2': np.mean([m['R2'] for m in metrics_per_target.values() if isinstance(m, dict)]),
            'MAPE': np.mean([m['MAPE'] for m in metrics_per_target.values() if isinstance(m, dict)])
        }
        
        return metrics_per_target
    
    @staticmethod
    def analyze_residuals(
        y_true: pd.DataFrame,
        y_pred: pd.DataFrame
    ) -> Dict[str, pd.DataFrame]:
        """
        Analiza residuos de predicción.
        
        Args:
            y_true: Valores reales
            y_pred: Valores predichos
            
        Returns:
            Diccionario con análisis de residuos
        """
        residuals = {}
        
        for i in range(y_true.shape[1]):
            y_t = y_true.iloc[:, i] if isinstance(y_true, pd.DataFrame) else y_true[:, i]
            y_p = y_pred[:, i]
            
            resid = y_t - y_p
            
            analysis = pd.DataFrame({
                'residual': resid,
                'predicted': y_p,
                'actual': y_t,
                'abs_residual': np.abs(resid),
                'pct_error': (resid / (y_t + 1e-10)) * 100
            })
            
            target_name = y_true.columns[i] if isinstance(y_true, pd.DataFrame) else f"target_{i}"
            residuals[target_name] = analysis
        
        return residuals
    
    @staticmethod
    def generate_comparison_report(
        scores: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Genera reporte comparativo de modelos.
        
        Args:
            scores: Diccionario con scores de múltiples modelos
            
        Returns:
            DataFrame con comparación
        """
        comparison_data = []
        
        for model_name, metrics in scores.items():
            row = {'Model': model_name}
            row.update(metrics)
            comparison_data.append(row)
        
        df_comparison = pd.DataFrame(comparison_data)
        
        # Ordenar por métrica principal
        if 'rmse' in df_comparison.columns:
            df_comparison = df_comparison.sort_values('rmse')
        elif 'mae' in df_comparison.columns:
            df_comparison = df_comparison.sort_values('mae')
        
        return df_comparison
    
    @staticmethod
    def check_thresholds(
        metrics: Dict[str, float],
        min_r2: float = 0.70,
        max_mape: float = 15.0
    ) -> Tuple[bool, List[str]]:
        """
        Verifica si el modelo cumple umbrales de aceptación.
        
        Args:
            metrics: Métricas del modelo
            min_r2: R² mínimo aceptable
            max_mape: MAPE máximo aceptable
            
        Returns:
            Tupla (cumple_umbrales, lista_advertencias)
        """
        warnings = []
        passes = True
        
        r2 = metrics.get('r2', 0)
        mape = metrics.get('mape', 100)
        
        if r2 < min_r2:
            warnings.append(f"R² bajo: {r2:.4f} < {min_r2}")
            passes = False
        
        if mape > max_mape:
            warnings.append(f"MAPE alto: {mape:.2f}% > {max_mape}%")
            passes = False
        
        if passes:
            logger.info("✓ Modelo cumple todos los umbrales de aceptación")
        else:
            logger.warning("✗ Modelo NO cumple umbrales:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
        
        return passes, warnings
    
    @staticmethod
    def plot_predictions_vs_actual(
        y_true: pd.DataFrame,
        y_pred: pd.DataFrame,
        target_names: List[str],
        save_path: Optional[Path] = None
    ) -> None:
        """
        Genera gráficos de predicciones vs valores reales.
        
        Args:
            y_true: Valores reales
            y_pred: Valores predichos
            target_names: Nombres de targets
            save_path: Ruta para guardar gráfico (opcional)
        """
        n_targets = len(target_names)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        for i, target_name in enumerate(target_names[:4]):  # Max 4 targets
            if i >= len(axes):
                break
            
            y_t = y_true.iloc[:, i] if isinstance(y_true, pd.DataFrame) else y_true[:, i]
            y_p = y_pred[:, i]
            
            axes[i].scatter(y_t, y_p, alpha=0.5)
            
            # Línea perfecta de predicción
            min_val = min(y_t.min(), y_p.min())
            max_val = max(y_t.max(), y_p.max())
            axes[i].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
            
            axes[i].set_xlabel('Valor Real')
            axes[i].set_ylabel('Valor Predicho')
            axes[i].set_title(f'{target_name}')
            axes[i].grid(True, alpha=0.3)
            
            # Calcular R²
            r2 = r2_score(y_t, y_p)
            axes[i].text(0.05, 0.95, f'R² = {r2:.4f}',
                        transform=axes[i].transAxes,
                        verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráfico guardado en: {save_path}")
        else:
            plt.show()
        
        plt.close()
