"""
Script de instalación automatizada del backend.

Instala todas las dependencias y configura el entorno.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(command, description):
    """Ejecuta un comando y muestra el resultado."""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"✅ {description} - COMPLETADO")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {e}")
        print(f"Output: {e.output}")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Verifica la versión de Python."""
    print("\n" + "="*70)
    print("🐍 Verificando versión de Python")
    print("="*70)
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 11):
        print("❌ ERROR: Se requiere Python 3.11 o superior")
        return False
    
    print("✅ Versión de Python correcta")
    return True


def create_env_file():
    """Crea archivo .env si no existe."""
    print("\n" + "="*70)
    print("📄 Verificando archivo .env")
    print("="*70)
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("✅ Archivo .env ya existe")
        return True
    
    if env_example_path.exists():
        # Copiar .env.example a .env
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ Archivo .env creado desde .env.example")
        return True
    
    # Crear .env básico
    default_env = """# Database
DATABASE_URL=sqlite:///./planta_esperanza.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
"""
    
    with open(env_path, 'w') as f:
        f.write(default_env)
    
    print("✅ Archivo .env creado con valores por defecto")
    print("⚠️  IMPORTANTE: Actualiza SECRET_KEY antes de usar en producción")
    return True


def create_directories():
    """Crea directorios necesarios."""
    print("\n" + "="*70)
    print("📁 Creando directorios")
    print("="*70)
    
    directories = [
        "uploads",
        "logs",
        "ml/trained_models",
        "ml/data",
        "ml/reports"
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"  ✓ {directory} (ya existe)")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {directory} (creado)")
    
    return True


def main():
    """Función principal de instalación."""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  Instalación Automatizada - Backend SICOP".center(68) + "║")
    print("║" + "  Planta de Tratamiento de Agua 'La Esperanza'".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"\n📍 Directorio de trabajo: {Path.cwd()}")
    
    # Paso 1: Verificar Python
    if not check_python_version():
        print("\n❌ INSTALACIÓN CANCELADA")
        return 1
    
    # Paso 2: Instalar/actualizar pip
    if not run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Actualizando pip"
    ):
        print("⚠️  Advertencia: No se pudo actualizar pip, continuando...")
    
    # Paso 3: Instalar dependencias
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Instalando dependencias de requirements.txt"
    ):
        print("\n❌ ERROR: No se pudieron instalar las dependencias")
        return 1
    
    # Paso 4: Crear archivo .env
    if not create_env_file():
        print("\n❌ ERROR: No se pudo crear archivo .env")
        return 1
    
    # Paso 5: Crear directorios
    if not create_directories():
        print("\n❌ ERROR: No se pudieron crear directorios")
        return 1
    
    # Paso 6: Verificar instalación de ML
    print("\n" + "="*70)
    print("🤖 Verificando instalación de Machine Learning")
    print("="*70)
    
    try:
        import pandas
        import numpy
        import sklearn
        import xgboost
        import lightgbm
        print("✅ Librerías ML instaladas correctamente")
        print(f"  - pandas: {pandas.__version__}")
        print(f"  - numpy: {numpy.__version__}")
        print(f"  - scikit-learn: {sklearn.__version__}")
        print(f"  - xgboost: {xgboost.__version__}")
        print(f"  - lightgbm: {lightgbm.__version__}")
    except ImportError as e:
        print(f"⚠️  Advertencia: {e}")
        print("   Ejecute: pip install -r requirements.txt")
    
    # Resumen
    print("\n" + "="*70)
    print("✅ INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("="*70)
    print("\n📋 Próximos pasos:")
    print("  1. Revisar/actualizar archivo .env con tus configuraciones")
    print("  2. Inicializar base de datos: python init_database.py")
    print("  3. Insertar datos de prueba (opcional): python insert_test_data.py")
    print("  4. Generar datos ML (opcional): python generate_ml_data.py")
    print("  5. Entrenar modelo ML (opcional): python train_ml_model.py")
    print("  6. Iniciar servidor: python -m uvicorn main:app --reload")
    print("\n" + "="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
