"""
Script de configuración e instalación del sistema ML.

Verifica dependencias, crea directorios y configura el entorno.
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Imprime encabezado formateado."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_python_version():
    """Verifica la versión de Python."""
    print_header("Verificando versión de Python")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 11):
        print("❌ ERROR: Se requiere Python 3.11 o superior")
        print("   Por favor actualice Python e intente nuevamente")
        return False
    
    print("✓ Versión de Python correcta")
    return True


def check_dependencies():
    """Verifica que las dependencias estén instaladas."""
    print_header("Verificando dependencias")
    
    required_packages = [
        'fastapi',
        'sqlalchemy',
        'pandas',
        'numpy',
        'scikit-learn',
        'xgboost',
        'lightgbm',
        'joblib',
        'pyyaml'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NO INSTALADO")
            missing.append(package)
    
    if missing:
        print(f"\n⚠ Faltan {len(missing)} paquetes")
        print("\nPara instalarlos, ejecute:")
        print("pip install -r requirements.txt")
        print("pip install -r ml_requirements.txt")
        return False
    
    print("\n✓ Todas las dependencias están instaladas")
    return True


def create_directories():
    """Crea los directorios necesarios."""
    print_header("Creando directorios")
    
    directories = [
        "ml/trained_models",
        "ml/data",
        "ml/reports",
        "logs",
        "uploads"
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✓ {directory} (ya existe)")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ {directory} (creado)")
    
    return True


def verify_config():
    """Verifica que el archivo de configuración exista."""
    print_header("Verificando configuración")
    
    config_path = Path("ml/config/ml_config.yaml")
    
    if not config_path.exists():
        print(f"❌ ERROR: Archivo de configuración no encontrado")
        print(f"   Ruta esperada: {config_path.absolute()}")
        return False
    
    print(f"✓ Configuración encontrada: {config_path}")
    
    # Intentar cargar configuración
    try:
        from ml.utils.config_manager import get_config
        config = get_config()
        print(f"✓ Configuración cargada correctamente")
        print(f"   Proyecto: {config.get('project.name')}")
        print(f"   Modelos habilitados: {len(config.enabled_models)}")
        return True
    except Exception as e:
        print(f"❌ ERROR cargando configuración: {e}")
        return False


def verify_database():
    """Verifica conexión a la base de datos."""
    print_header("Verificando base de datos")
    
    try:
        from core.database import SessionLocal
        from ml.data.repository import PlantDataRepository
        
        db = SessionLocal()
        repo = PlantDataRepository(db)
        stats = repo.get_data_statistics()
        
        print(f"✓ Conexión a base de datos exitosa")
        print(f"   Registros operativos: {stats['total_operational_records']}")
        print(f"   Registros de consumo: {stats['total_consumption_records']}")
        
        if stats['total_operational_records'] < 90:
            print(f"\n⚠ ADVERTENCIA: Pocos datos disponibles para entrenamiento")
            print(f"   Se recomienda al menos 90 registros (3 meses)")
            print(f"   Puede insertar datos de prueba con: python insert_test_data.py")
        
        db.close()
        return True
    
    except Exception as e:
        print(f"❌ ERROR: No se pudo conectar a la base de datos")
        print(f"   {e}")
        print(f"\n   Verifique que:")
        print(f"   1. El archivo .env esté configurado correctamente")
        print(f"   2. La base de datos exista")
        
        return False


def test_ml_system():
    """Prueba básica del sistema ML."""
    print_header("Probando sistema ML")
    
    try:
        # Test 1: Importar módulos
        print("Test 1: Importando módulos...")
        from ml.inference.predictor_service import ChemicalConsumptionPredictor
        from ml.inference.anomaly_service import AnomalyDetectorService
        print("✓ Módulos importados correctamente")
        
        # Test 2: Inicializar servicios
        print("\nTest 2: Inicializando servicios...")
        predictor = ChemicalConsumptionPredictor()
        anomaly_detector = AnomalyDetectorService()
        print("✓ Servicios inicializados")
        
        # Test 3: Verificar configuración
        print("\nTest 3: Verificando configuración...")
        from ml.utils.config_manager import get_config
        config = get_config()
        config.ensure_directories()
        print("✓ Configuración verificada")
        
        print("\n✓ Sistema ML funcionando correctamente")
        return True
    
    except Exception as e:
        print(f"❌ ERROR en tests: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal de setup."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Setup - Sistema ML Optimización Consumo de Químicos".center(68) + "║")
    print("║" + "  Planta de Tratamiento de Agua 'La Esperanza'".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)
    
    print(f"\nDirectorio de trabajo: {Path.cwd()}")
    
    # Ejecutar verificaciones
    checks = [
        ("Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Directorios", create_directories),
        ("Configuración", verify_config),
        ("Base de Datos", verify_database),
        ("Sistema ML", test_ml_system)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Error inesperado en {name}: {e}")
            results[name] = False
    
    # Resumen
    print_header("RESUMEN")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nResultado: {passed}/{total} verificaciones pasadas")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("✅ SETUP COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        print("\nPróximos pasos:")
        print("1. Entrenar modelo: python train_ml_model.py")
        print("2. Iniciar API: python -m uvicorn main:app --reload")
        print("3. Documentación: ml/README.md")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("⚠ SETUP INCOMPLETO")
        print("=" * 70)
        print("\nPor favor corrija los errores indicados arriba")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
