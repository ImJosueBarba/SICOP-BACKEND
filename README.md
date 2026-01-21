# 🌊 SICOP - Sistema de Control de Procesos de Potabilización

<p align="center">
  <img src="https://img.shields.io/badge/Angular-18+-DD0031?style=for-the-badge&logo=angular&logoColor=white" alt="Angular"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-14+-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
</p>

Sistema integral de gestión y monitoreo para la **Planta de Tratamiento de Agua Potable "La Esperanza"**. Digitaliza los procesos de control operacional, seguimiento de químicos y monitoreo de calidad del agua.

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Matrices de Control](#-matrices-de-control)
- [Sistema de Roles](#-sistema-de-roles)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [API Documentation](#-api-documentation)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías](#-tecnologías)

---

## 📖 Descripción

SICOP es una aplicación web completa tipo SCADA (Supervisory Control and Data Acquisition) simplificado que permite:

- **Registrar datos operacionales** en tiempo real
- **Monitorear la calidad del agua** en cada etapa del tratamiento
- **Controlar el inventario de químicos** utilizados en el proceso
- **Generar reportes** históricos y de seguimiento
- **Auditar todas las operaciones** del sistema

El sistema reemplaza los registros en papel por formularios digitales, mejorando la trazabilidad, reduciendo errores y facilitando la generación de informes.

---

## ✨ Características

### Funcionalidades Principales

| Módulo | Descripción |
|--------|-------------|
| 🔐 **Autenticación JWT** | Login seguro con tokens de acceso |
| 👥 **Gestión de Usuarios** | CRUD completo con sistema de roles jerárquico |
| 📊 **6 Matrices de Control** | Formularios digitales para registro operacional |
| 📈 **Reportes** | Visualización histórica de datos por matriz |
| 🔍 **Auditoría** | Logs de todas las acciones del sistema |
| 💊 **Control de Químicos** | Inventario y consumo de químicos |
| 🔧 **Catálogo de Filtros** | Estado y mantenimiento de 6 filtros |

### Características Técnicas

- ✅ API REST documentada con Swagger/OpenAPI
- ✅ Autenticación basada en JWT
- ✅ Base de datos relacional PostgreSQL
- ✅ Frontend responsive con Angular
- ✅ Contenedorización con Docker
- ✅ Arquitectura modular y escalable

---

## 🏗 Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTE                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Angular 18+ (SPA)                       │    │
│  │  • Componentes Standalone                            │    │
│  │  • Tailwind CSS                                      │    │
│  │  • Guards & Interceptors                             │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         SERVIDOR                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              FastAPI (Python)                        │    │
│  │  • Routers modulares                                 │    │
│  │  • Pydantic schemas                                  │    │
│  │  • SQLAlchemy ORM                                    │    │
│  │  • JWT Authentication                                │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ SQL
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      BASE DE DATOS                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              PostgreSQL 14+                          │    │
│  │  • 11 tablas                                         │    │
│  │  • Índices optimizados                               │    │
│  │  • Triggers automáticos                              │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Matrices de Control

El sistema digitaliza **6 matrices operacionales** utilizadas en la planta:

| # | Matriz | Frecuencia | Descripción |
|---|--------|-----------|-------------|
| 1 | **Consumo Químicos Mensual** | Mensual | Consolidado de consumo de todos los químicos |
| 2 | **Control de Operación** | Horaria (24h) | Turbedad, pH, dosificación, presiones, cloro residual |
| 3 | **Producción por Filtros** | Horaria (24h) | Altura y caudal de los 6 filtros |
| 4 | **Consumo Diario Químicos** | Diaria | Lecturas de tanques y movimientos de bodega |
| 5 | **Inventario Cloro Libre** | Por evento | Entradas, salidas y saldo de cloro |
| 6 | **Monitoreo Fisicoquímico** | 3 veces/día | pH, conductividad, TDS, temperatura |

### Químicos Controlados

- 🧪 Sulfato de Aluminio (Coagulante)
- 🧪 Cal Viva (Regulador pH)
- 🧪 Floergel (Floculante)
- 🧪 Hipoclorito de Calcio (Desinfectante)
- 🧪 Gas Licuado de Cloro (Desinfectante)

---

## 👥 Sistema de Roles

Sistema jerárquico de **8 roles en 4 niveles**:

| Nivel | Categoría | Roles | Permisos |
|-------|-----------|-------|----------|
| 1 | **ADMINISTRADOR** | Coordinación General | Acceso total, gestión de usuarios |
| 2 | **JEFATURA** | Jefatura de Operación | Supervisión general de planta |
| 3 | **SUPERVISOR** | Gestión Ambiental, Asistente Técnico, Supervisor Técnico | Supervisión de área específica |
| 4 | **OPERADOR** | Operador Captación, Operador Planta, Operador Vergel | Registro de datos operacionales |

---

## 🚀 Instalación

### Prerrequisitos

- PostgreSQL 14+
- Python 3.10+
- Node.js 18+
- npm 9+

### Opción 1: Instalación Local

#### 1. Clonar repositorio
```bash
git clone <repository-url>
cd SICOP
```

#### 2. Crear base de datos
```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear BD
CREATE DATABASE planta_esperanza WITH ENCODING 'UTF8';
\q

# Ejecutar script
psql -U postgres -d planta_esperanza -f database/create_database.sql
```

#### 3. Configurar Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env con tu configuración de BD

# Actualizar contraseñas
python update_passwords.py

# Ejecutar
python main.py
```

#### 4. Configurar Frontend
```bash
cd frontend
npm install
npm start
```

### Opción 2: Docker Compose

```bash
docker-compose up --build
```

---

## 💻 Uso

### URLs de Acceso

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:4200 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### Credenciales por Defecto

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | Administrador |
| `jperez` | `operador123` | Operador |

> ⚠️ **Importante**: Cambiar contraseñas en producción

---

## 📚 API Documentation

### Endpoints Principales

```
POST   /api/auth/token          # Login
GET    /api/usuarios            # Listar usuarios
POST   /api/usuarios            # Crear usuario
GET    /api/roles               # Listar roles
GET    /api/control-operacion   # Matriz 2
GET    /api/produccion-filtros  # Matriz 3
GET    /api/consumo-diario      # Matriz 4
GET    /api/control-cloro       # Matriz 5
GET    /api/monitoreo-fisicoquimico  # Matriz 6
GET    /api/consumo-mensual     # Matriz 1
GET    /api/quimicos            # Catálogo químicos
GET    /api/filtros             # Catálogo filtros
GET    /api/logs                # Auditoría
```

Documentación completa en: http://localhost:8000/docs

---

## 📁 Estructura del Proyecto

```
SICOP/
├── 📂 backend/
│   ├── 📂 core/               # Configuración (BD, seguridad)
│   ├── 📂 models/             # Modelos SQLAlchemy (11 modelos)
│   ├── 📂 routers/            # Endpoints API (13 routers)
│   ├── 📂 schemas/            # Schemas Pydantic
│   ├── 📄 main.py             # Punto de entrada FastAPI
│   ├── 📄 requirements.txt    # Dependencias Python
│   └── 📄 Dockerfile
│
├── 📂 frontend/
│   ├── 📂 src/app/
│   │   ├── 📂 auth/           # Autenticación (guard, interceptor)
│   │   ├── 📂 forms/          # 6 formularios de matrices
│   │   ├── 📂 pages/          # Páginas (home, login, admin, reportes)
│   │   ├── 📂 services/       # Servicios HTTP
│   │   ├── 📂 layout/         # Header, sidebar, navbar
│   │   └── 📄 app.routes.ts   # Configuración de rutas
│   ├── 📄 package.json
│   └── 📄 Dockerfile
│
├── 📂 database/
│   └── 📄 create_database.sql # Script creación BD
│
├── 📄 docker-compose.yml
├── 📄 README.md
└── 📄 ANALISIS_MATRICES.md    # Especificación detallada matrices
```

---

## 🛠 Tecnologías

### Backend
- **FastAPI** - Framework web async Python
- **SQLAlchemy** - ORM
- **Pydantic** - Validación de datos
- **python-jose** - JWT tokens
- **bcrypt** - Hash de contraseñas
- **Uvicorn** - Servidor ASGI

### Frontend
- **Angular 18+** - Framework SPA
- **Tailwind CSS** - Framework CSS
- **RxJS** - Programación reactiva

### Base de Datos
- **PostgreSQL 14+** - RDBMS

### DevOps
- **Docker** - Contenedores
- **Docker Compose** - Orquestación
- **Nginx** - Servidor web (producción)

---

## 📄 Documentación Adicional

| Documento | Descripción |
|-----------|-------------|
| [ANALISIS_MATRICES.md](./ANALISIS_MATRICES.md) | Especificación detallada de las 6 matrices |
| [SISTEMA_ROLES_ACTUALIZADO.md](./SISTEMA_ROLES_ACTUALIZADO.md) | Documentación del sistema de roles |
| [MIGRACION_USUARIOS.md](./MIGRACION_USUARIOS.md) | Guía de migración operadores → usuarios |
| [DOCKER_README.md](./DOCKER_README.md) | Guía de uso con Docker |
| [backend/README.md](./backend/README.md) | Documentación del backend |

---

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

## 📝 Licencia

Este proyecto es software propietario desarrollado para la Planta de Tratamiento de Agua "La Esperanza".

---

<p align="center">
  Desarrollado con ❤️ para la gestión eficiente del agua potable
</p>
