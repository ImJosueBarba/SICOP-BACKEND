-- ==================================================================
-- SICOP - Sistema de Control de Procesos de Potabilización
-- Script de creación completa de Base de Datos
-- Planta de Tratamiento de Agua "La Esperanza"
-- ==================================================================
-- Generado basándose en los modelos SQLAlchemy del proyecto
-- Fecha: Generado automáticamente
-- ==================================================================

-- Crear la base de datos (ejecutar como superusuario)
-- DROP DATABASE IF EXISTS planta_esperanza;
-- CREATE DATABASE planta_esperanza WITH ENCODING 'UTF8' LC_COLLATE 'es_ES.UTF-8' LC_CTYPE 'es_ES.UTF-8';

-- ==================================================================
-- TABLA 1: ROLES
-- Sistema de roles jerárquico con 4 niveles y 8 roles
-- ==================================================================
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    nivel_jerarquia INTEGER NOT NULL,
    categoria VARCHAR(20) NOT NULL,
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_roles_codigo ON roles(codigo);
CREATE INDEX IF NOT EXISTS idx_roles_nivel ON roles(nivel_jerarquia);
CREATE INDEX IF NOT EXISTS idx_roles_categoria ON roles(categoria);
CREATE INDEX IF NOT EXISTS idx_roles_activo ON roles(activo);

COMMENT ON TABLE roles IS 'Catálogo de roles del sistema con jerarquía y categorías';
COMMENT ON COLUMN roles.codigo IS 'Código único del rol para uso en código';
COMMENT ON COLUMN roles.nombre IS 'Nombre descriptivo del rol';
COMMENT ON COLUMN roles.nivel_jerarquia IS 'Nivel jerárquico: 1=más alto, 4=más bajo';
COMMENT ON COLUMN roles.categoria IS 'Categoría del rol: ADMINISTRADOR, JEFATURA, SUPERVISOR, OPERADOR';

-- Insertar los 8 roles predefinidos
INSERT INTO roles (codigo, nombre, nivel_jerarquia, categoria, descripcion) VALUES
('COORD_GENERAL', 'Coordinación General', 1, 'ADMINISTRADOR', 'Administrador principal del sistema'),
('JEF_OPERACION', 'Jefatura de Operación, Producción y Mantenimiento', 2, 'JEFATURA', 'Responsable de operaciones de la planta'),
('GEST_AMBIENTAL', 'Gestión Ambiental y Calidad', 3, 'SUPERVISOR', 'Supervisor de gestión ambiental y control de calidad'),
('ASIST_TECNICO', 'Asistente Técnico', 3, 'SUPERVISOR', 'Asistente técnico de operaciones'),
('SUPERVISOR_TEC', 'Supervisor Técnico', 3, 'SUPERVISOR', 'Supervisor técnico de campo'),
('OP_CAPTACION', 'Operador de Captación', 4, 'OPERADOR', 'Operador en área de captación'),
('OP_PLANTA', 'Operador de Planta', 4, 'OPERADOR', 'Operador en planta de tratamiento'),
('OP_VERGEL', 'Operador de Vergel', 4, 'OPERADOR', 'Operador en área de Vergel')
ON CONFLICT (codigo) DO NOTHING;

-- ==================================================================
-- TABLA 2: USUARIOS
-- Usuarios del sistema con autenticación JWT
-- ==================================================================

-- Crear enum para compatibilidad (legacy)
DO $$ BEGIN
    CREATE TYPE userole AS ENUM ('ADMINISTRADOR', 'OPERADOR');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE,
    fecha_contratacion DATE,
    
    -- Autenticación
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    
    -- Sistema de roles nuevo
    rol_id INTEGER NOT NULL REFERENCES roles(id),
    
    -- Legacy (mantener por compatibilidad)
    rol userole,
    rol_antiguo VARCHAR(20),
    
    -- Foto de perfil
    foto_perfil VARCHAR(500),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol_id ON usuarios(rol_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_login ON usuarios(username, activo);

COMMENT ON TABLE usuarios IS 'Usuarios del sistema con autenticación y roles';
COMMENT ON COLUMN usuarios.hashed_password IS 'Contraseña hasheada con bcrypt';

-- ==================================================================
-- TABLA 3: QUIMICOS
-- Catálogo de químicos utilizados en la planta
-- ==================================================================
CREATE TABLE IF NOT EXISTS quimicos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    peso_por_unidad NUMERIC(10, 2),
    stock_minimo INTEGER,
    stock_actual INTEGER DEFAULT 0,
    proveedor VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_quimicos_codigo ON quimicos(codigo);
CREATE INDEX IF NOT EXISTS idx_quimicos_tipo ON quimicos(tipo);
CREATE INDEX IF NOT EXISTS idx_quimicos_activo ON quimicos(activo);

COMMENT ON TABLE quimicos IS 'Catálogo de químicos: Sulfato, Cal, Hipoclorito, etc.';

-- Insertar químicos predefinidos
INSERT INTO quimicos (codigo, nombre, tipo, unidad_medida, peso_por_unidad, stock_minimo) VALUES
('SULFATO_AL', 'Sulfato de Aluminio', 'COAGULANTE', 'SACOS', 25.00, 50),
('CAL_VIVA', 'Cal Viva (Óxido de Calcio)', 'REGULADOR_PH', 'SACOS', 25.00, 50),
('FLOERGEL', 'Floergel (Floculante)', 'FLOCULANTE', 'SACOS', 25.00, 20),
('HIPOCLORITO_CA', 'Hipoclorito de Calcio', 'DESINFECTANTE', 'TAMBORES', 45.00, 10),
('CLORO_GAS', 'Gas Licuado de Cloro', 'DESINFECTANTE', 'CILINDROS', 907.00, 5),
('CLORO_LIBRE', 'Cloro Libre', 'DESINFECTANTE', 'UNIDADES', 1.00, 100)
ON CONFLICT (codigo) DO NOTHING;

-- ==================================================================
-- TABLA 4: FILTROS
-- Catálogo de los 6 filtros de la planta
-- ==================================================================
CREATE TABLE IF NOT EXISTS filtros (
    id SERIAL PRIMARY KEY,
    numero INTEGER UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    capacidad_maxima NUMERIC(10, 2),
    altura_maxima NUMERIC(10, 2),
    fecha_instalacion DATE,
    estado VARCHAR(20) DEFAULT 'OPERATIVO',
    ultima_limpieza DATE,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_filtros_numero ON filtros(numero);
CREATE INDEX IF NOT EXISTS idx_filtros_estado ON filtros(estado);

COMMENT ON TABLE filtros IS 'Catálogo de los 6 filtros de la planta';
COMMENT ON COLUMN filtros.estado IS 'OPERATIVO, MANTENIMIENTO, FUERA_SERVICIO';

-- Insertar los 6 filtros
INSERT INTO filtros (numero, nombre, estado) VALUES
(1, 'Filtro 1', 'OPERATIVO'),
(2, 'Filtro 2', 'OPERATIVO'),
(3, 'Filtro 3', 'OPERATIVO'),
(4, 'Filtro 4', 'OPERATIVO'),
(5, 'Filtro 5', 'OPERATIVO'),
(6, 'Filtro 6', 'OPERATIVO')
ON CONFLICT (numero) DO NOTHING;

-- ==================================================================
-- TABLA 5: CONTROL_OPERACION (Matriz 2)
-- Control horario de operación del sistema de coagulación-floculación
-- ==================================================================
CREATE TABLE IF NOT EXISTS control_operacion (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    
    -- Turbedad
    turbedad_ac NUMERIC(10, 2),
    turbedad_at NUMERIC(10, 2),
    
    -- Color
    color VARCHAR(50),
    
    -- pH
    ph_ac NUMERIC(4, 2),
    ph_sulf NUMERIC(4, 2),
    ph_at NUMERIC(4, 2),
    
    -- Dosis Químicos
    dosis_sulfato NUMERIC(10, 3),
    dosis_cal NUMERIC(10, 3),
    dosis_floergel NUMERIC(10, 3),
    
    -- Factor de Forma
    ff NUMERIC(10, 2),
    
    -- Clarificación
    clarificacion_is NUMERIC(10, 2),
    clarificacion_cs NUMERIC(10, 2),
    clarificacion_fs NUMERIC(10, 2),
    
    -- Presión
    presion_psi NUMERIC(10, 2),
    presion_pre NUMERIC(10, 2),
    presion_pos NUMERIC(10, 2),
    presion_total NUMERIC(10, 2),
    
    -- Cloración
    cloro_residual NUMERIC(10, 2),
    
    observaciones TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_fecha_hora_operacion UNIQUE (fecha, hora)
);

CREATE INDEX IF NOT EXISTS idx_control_operacion_fecha ON control_operacion(fecha);
CREATE INDEX IF NOT EXISTS idx_control_operacion_hora ON control_operacion(hora);
CREATE INDEX IF NOT EXISTS idx_control_operacion_usuario_id ON control_operacion(usuario_id);

COMMENT ON TABLE control_operacion IS 'Matriz 2: Control horario de operación (24 registros/día)';

-- ==================================================================
-- TABLA 6: PRODUCCION_FILTROS (Matriz 3)
-- Control horario de producción por cada uno de los 6 filtros
-- ==================================================================
CREATE TABLE IF NOT EXISTS produccion_filtros (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    
    -- Filtro 1
    filtro1_h NUMERIC(10, 2),
    filtro1_q NUMERIC(10, 2),
    
    -- Filtro 2
    filtro2_h NUMERIC(10, 2),
    filtro2_q NUMERIC(10, 2),
    
    -- Filtro 3
    filtro3_h NUMERIC(10, 2),
    filtro3_q NUMERIC(10, 2),
    
    -- Filtro 4
    filtro4_h NUMERIC(10, 2),
    filtro4_q NUMERIC(10, 2),
    
    -- Filtro 5
    filtro5_h NUMERIC(10, 2),
    filtro5_q NUMERIC(10, 2),
    
    -- Filtro 6
    filtro6_h NUMERIC(10, 2),
    filtro6_q NUMERIC(10, 2),
    
    -- Total
    caudal_total NUMERIC(10, 2),
    
    observaciones TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_fecha_hora_produccion UNIQUE (fecha, hora)
);

CREATE INDEX IF NOT EXISTS idx_produccion_filtros_fecha ON produccion_filtros(fecha);
CREATE INDEX IF NOT EXISTS idx_produccion_filtros_usuario_id ON produccion_filtros(usuario_id);

COMMENT ON TABLE produccion_filtros IS 'Matriz 3: Producción horaria por filtro (24 registros/día)';
COMMENT ON COLUMN produccion_filtros.filtro1_h IS 'Altura en cm';
COMMENT ON COLUMN produccion_filtros.filtro1_q IS 'Caudal en l/s';

-- ==================================================================
-- TABLA 7: CONTROL_CONSUMO_DIARIO_QUIMICOS (Matriz 4)
-- Control diario detallado del consumo de químicos
-- ==================================================================
CREATE TABLE IF NOT EXISTS control_consumo_diario_quimicos (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    quimico_id INTEGER REFERENCES quimicos(id),
    
    -- Bodega
    bodega_ingresa INTEGER,
    bodega_egresa INTEGER,
    bodega_stock INTEGER,
    
    -- Tanque N1
    tanque1_hora TIME,
    tanque1_lectura_inicial NUMERIC(10, 2),
    tanque1_lectura_final NUMERIC(10, 2),
    tanque1_consumo NUMERIC(10, 2),
    
    -- Tanque N2 (solo para sulfato de aluminio)
    tanque2_hora TIME,
    tanque2_lectura_inicial NUMERIC(10, 2),
    tanque2_lectura_final NUMERIC(10, 2),
    tanque2_consumo NUMERIC(10, 2),
    
    -- Total
    total_consumo NUMERIC(10, 2),
    
    observaciones TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_consumo_diario_fecha ON control_consumo_diario_quimicos(fecha);
CREATE INDEX IF NOT EXISTS idx_consumo_diario_quimico_id ON control_consumo_diario_quimicos(quimico_id);
CREATE INDEX IF NOT EXISTS idx_consumo_diario_usuario_id ON control_consumo_diario_quimicos(usuario_id);

COMMENT ON TABLE control_consumo_diario_quimicos IS 'Matriz 4: Control diario de consumo de químicos con lecturas de tanques';

-- ==================================================================
-- TABLA 8: CONTROL_CLORO_LIBRE (Matriz 5)
-- Control de inventario de cloro libre (entradas/salidas)
-- ==================================================================
CREATE TABLE IF NOT EXISTS control_cloro_libre (
    id SERIAL PRIMARY KEY,
    fecha_mes DATE NOT NULL,
    documento_soporte VARCHAR(100),
    proveedor_solicitante VARCHAR(100),
    codigo VARCHAR(50),
    especificacion VARCHAR(200),
    
    -- Movimientos
    cantidad_entra INTEGER DEFAULT 0,
    cantidad_sale INTEGER DEFAULT 0,
    cantidad_saldo INTEGER,
    
    observaciones TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cloro_libre_fecha ON control_cloro_libre(fecha_mes);
CREATE INDEX IF NOT EXISTS idx_cloro_libre_codigo ON control_cloro_libre(codigo);
CREATE INDEX IF NOT EXISTS idx_cloro_libre_usuario_id ON control_cloro_libre(usuario_id);

COMMENT ON TABLE control_cloro_libre IS 'Matriz 5: Inventario de cloro libre con trazabilidad';

-- ==================================================================
-- TABLA 9: MONITOREO_FISICOQUIMICO (Matriz 6)
-- Reporte diario de monitoreo fisicoquímico complementario
-- ==================================================================
CREATE TABLE IF NOT EXISTS monitoreo_fisicoquimico (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    usuario_id INTEGER REFERENCES usuarios(id),
    lugar_agua_cruda VARCHAR(200),
    lugar_agua_tratada VARCHAR(200),
    
    muestra_numero INTEGER NOT NULL,
    hora TIME NOT NULL,
    
    -- Agua Cruda
    ac_ph NUMERIC(4, 2),
    ac_ce NUMERIC(10, 2),
    ac_tds NUMERIC(10, 2),
    ac_salinidad NUMERIC(10, 3),
    ac_temperatura NUMERIC(5, 2),
    
    -- Agua Tratada
    at_ph NUMERIC(4, 2),
    at_ce NUMERIC(10, 2),
    at_tds NUMERIC(10, 2),
    at_salinidad NUMERIC(10, 3),
    at_temperatura NUMERIC(5, 2),
    
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_fecha_muestra UNIQUE (fecha, muestra_numero),
    CONSTRAINT check_muestra_numero CHECK (muestra_numero >= 1 AND muestra_numero <= 3)
);

CREATE INDEX IF NOT EXISTS idx_monitoreo_fecha ON monitoreo_fisicoquimico(fecha);
CREATE INDEX IF NOT EXISTS idx_monitoreo_usuario_id ON monitoreo_fisicoquimico(usuario_id);

COMMENT ON TABLE monitoreo_fisicoquimico IS 'Matriz 6: Monitoreo fisicoquímico (3 muestras/día: 9:00, 12:00, 18:00)';
COMMENT ON COLUMN monitoreo_fisicoquimico.ac_ce IS 'Conductividad eléctrica en μS/cm';
COMMENT ON COLUMN monitoreo_fisicoquimico.ac_tds IS 'Sólidos disueltos totales en ppm';

-- ==================================================================
-- TABLA 10: CONSUMO_QUIMICOS_MENSUAL (Matriz 1)
-- Registro mensual consolidado de consumo de químicos
-- ==================================================================
CREATE TABLE IF NOT EXISTS consumo_quimicos_mensual (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    mes INTEGER NOT NULL,
    anio INTEGER NOT NULL,
    
    -- Sulfato de Aluminio
    sulfato_con NUMERIC(10, 2),
    sulfato_ing NUMERIC(10, 2),
    sulfato_guia VARCHAR(50),
    sulfato_re NUMERIC(10, 2),
    
    -- Cal
    cal_con INTEGER,
    cal_ing INTEGER,
    cal_guia VARCHAR(50),
    
    -- Hipoclorito de Calcio
    hipoclorito_con NUMERIC(10, 2),
    hipoclorito_ing NUMERIC(10, 2),
    hipoclorito_guia VARCHAR(50),
    
    -- Gas Licuado de Cloro
    cloro_gas_con NUMERIC(10, 2),
    cloro_gas_ing_bal NUMERIC(10, 2),
    cloro_gas_ing_bdg NUMERIC(10, 2),
    cloro_gas_guia VARCHAR(50),
    cloro_gas_egre NUMERIC(10, 2),
    
    -- Producción
    produccion_m3_dia NUMERIC(10, 2),
    
    -- Resumen mensual
    inicio_mes_kg NUMERIC(10, 2),
    ingreso_mes_kg NUMERIC(10, 2),
    consumo_mes_kg NUMERIC(10, 2),
    egreso_mes_kg NUMERIC(10, 2),
    fin_mes_kg NUMERIC(10, 2),
    
    observaciones TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_mes_anio UNIQUE (mes, anio),
    CONSTRAINT check_mes_valido CHECK (mes >= 1 AND mes <= 12)
);

CREATE INDEX IF NOT EXISTS idx_consumo_mensual_fecha ON consumo_quimicos_mensual(fecha);
CREATE INDEX IF NOT EXISTS idx_consumo_mensual_mes_anio ON consumo_quimicos_mensual(mes, anio);
CREATE INDEX IF NOT EXISTS idx_consumo_mensual_usuario_id ON consumo_quimicos_mensual(usuario_id);

COMMENT ON TABLE consumo_quimicos_mensual IS 'Matriz 1: Consolidado mensual de consumo de químicos';

-- ==================================================================
-- TABLA 11: LOGS_AUDITORIA
-- Registro de auditoría de todas las operaciones del sistema
-- ==================================================================
CREATE TABLE IF NOT EXISTS logs_auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    usuario_nombre VARCHAR(200),
    accion VARCHAR(50) NOT NULL,
    entidad VARCHAR(100),
    entidad_id INTEGER,
    detalles TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_logs_usuario_id ON logs_auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_logs_accion ON logs_auditoria(accion);
CREATE INDEX IF NOT EXISTS idx_logs_entidad ON logs_auditoria(entidad);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs_auditoria(created_at);

COMMENT ON TABLE logs_auditoria IS 'Registro de auditoría: LOGIN, LOGOUT, CREATE, UPDATE, DELETE';

-- ==================================================================
-- USUARIOS POR DEFECTO
-- Contraseñas se actualizan vía Python después de ejecutar este script
-- ==================================================================

-- Usuario Administrador
INSERT INTO usuarios (
    nombre, apellido, email, telefono, activo,
    username, hashed_password, rol_id, rol, fecha_contratacion
) VALUES (
    'Administrador', 'Sistema', 'admin@esperanza.com', NULL, TRUE,
    'admin', 'temp_hash_to_be_updated_by_python',
    (SELECT id FROM roles WHERE codigo = 'COORD_GENERAL'),
    'ADMINISTRADOR', CURRENT_DATE
) ON CONFLICT (username) DO UPDATE SET
    rol_id = (SELECT id FROM roles WHERE codigo = 'COORD_GENERAL'),
    activo = TRUE;

-- Usuario Operador de ejemplo
INSERT INTO usuarios (
    nombre, apellido, email, telefono, activo,
    username, hashed_password, rol_id, rol, fecha_contratacion
) VALUES (
    'Juan', 'Pérez', 'juan.perez@esperanza.com', '555-0123', TRUE,
    'jperez', 'temp_hash_to_be_updated_by_python',
    (SELECT id FROM roles WHERE codigo = 'OP_PLANTA'),
    'OPERADOR', CURRENT_DATE
) ON CONFLICT (username) DO UPDATE SET
    rol_id = (SELECT id FROM roles WHERE codigo = 'OP_PLANTA'),
    activo = TRUE;

-- ==================================================================
-- FUNCIÓN TRIGGER: Actualizar updated_at automáticamente
-- ==================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger a todas las tablas con updated_at
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN 
        SELECT table_name 
        FROM information_schema.columns 
        WHERE column_name = 'updated_at' 
        AND table_schema = 'public'
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%I_updated_at ON %I;
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        ', t, t, t, t);
    END LOOP;
END $$;

-- ==================================================================
-- VERIFICACIÓN FINAL
-- ==================================================================
SELECT 'Base de datos SICOP creada exitosamente' AS resultado;

SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columnas
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Verificar usuarios creados
SELECT username, nombre, apellido, 
       (SELECT nombre FROM roles r WHERE r.id = u.rol_id) as rol
FROM usuarios u;

-- ==================================================================
-- IMPORTANTE: DESPUÉS DE EJECUTAR ESTE SCRIPT
-- ==================================================================
-- Ejecutar el siguiente comando Python para actualizar contraseñas:
--
-- cd backend
-- python update_passwords.py
--
-- O ejecutar directamente:
-- python -c "
-- from core.database import SessionLocal
-- from core.security import get_password_hash
-- from models.usuario import Usuario
-- 
-- db = SessionLocal()
-- admin = db.query(Usuario).filter(Usuario.username == 'admin').first()
-- if admin: admin.hashed_password = get_password_hash('admin123')
-- jperez = db.query(Usuario).filter(Usuario.username == 'jperez').first()
-- if jperez: jperez.hashed_password = get_password_hash('operador123')
-- db.commit()
-- db.close()
-- print('Contraseñas actualizadas')
-- "
--
-- Credenciales finales:
-- admin / admin123
-- jperez / operador123
-- ==================================================================
