-- ==================================================================
-- SETUP COMPLETO DE BASE DE DATOS - PLANTA LA ESPERANZA
-- ==================================================================
-- Este script incluye toda la configuración necesaria:
-- 1. Migración de operadores a usuarios
-- 2. Creación de usuarios por defecto (admin y operador)
-- 3. Optimización con índices
-- 4. Constraint de administrador único
--
-- IMPORTANTE: Las contraseñas se actualizarán automáticamente por Python
-- Los hashes aquí son temporales y serán reemplazados
-- ==================================================================

BEGIN;

-- ==================================================================
-- PARTE 1: MIGRACIÓN DE OPERADORES A USUARIOS
-- ==================================================================

-- 1. Renombrar la tabla
ALTER TABLE operadores RENAME TO usuarios;

-- 2. Actualizar el enum de roles
ALTER TABLE usuarios ALTER COLUMN rol DROP DEFAULT;
ALTER TABLE usuarios ALTER COLUMN rol TYPE VARCHAR(20);

-- Eliminar el tipo enum antiguo y crear el nuevo
DROP TYPE IF EXISTS userole CASCADE;
CREATE TYPE userole AS ENUM ('ADMINISTRADOR', 'OPERADOR');

-- Aplicar el nuevo tipo
ALTER TABLE usuarios ALTER COLUMN rol TYPE userole USING rol::text::userole;
ALTER TABLE usuarios ALTER COLUMN rol SET DEFAULT 'OPERADOR'::userole;
ALTER TABLE usuarios ALTER COLUMN rol SET NOT NULL;

-- 3. Actualizar las columnas de referencia en otras tablas

-- Control de Operación
ALTER TABLE control_operacion 
    DROP CONSTRAINT IF EXISTS control_operacion_operador_id_fkey;

ALTER TABLE control_operacion 
    RENAME COLUMN operador_id TO usuario_id;

ALTER TABLE control_operacion 
    ADD CONSTRAINT control_operacion_usuario_id_fkey 
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

-- Producción de Filtros
ALTER TABLE produccion_filtros 
    DROP CONSTRAINT IF EXISTS produccion_filtros_operador_id_fkey;

ALTER TABLE produccion_filtros 
    RENAME COLUMN operador_id TO usuario_id;

ALTER TABLE produccion_filtros 
    ADD CONSTRAINT produccion_filtros_usuario_id_fkey 
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

-- Control Consumo Diario
ALTER TABLE control_consumo_diario_quimicos 
    DROP CONSTRAINT IF EXISTS control_consumo_diario_quimicos_operador_id_fkey;

ALTER TABLE control_consumo_diario_quimicos 
    RENAME COLUMN operador_id TO usuario_id;

ALTER TABLE control_consumo_diario_quimicos 
    ADD CONSTRAINT control_consumo_diario_quimicos_usuario_id_fkey 
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

-- Control Cloro Libre
ALTER TABLE control_cloro_libre 
    DROP CONSTRAINT IF EXISTS control_cloro_libre_operador_id_fkey;

ALTER TABLE control_cloro_libre 
    RENAME COLUMN operador_id TO usuario_id;

ALTER TABLE control_cloro_libre 
    ADD CONSTRAINT control_cloro_libre_usuario_id_fkey 
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

-- Monitoreo Fisicoquímico
ALTER TABLE monitoreo_fisicoquimico 
    DROP CONSTRAINT IF EXISTS monitoreo_fisicoquimico_operador_id_fkey;

ALTER TABLE monitoreo_fisicoquimico 
    RENAME COLUMN operador_id TO usuario_id;

ALTER TABLE monitoreo_fisicoquimico 
    ADD CONSTRAINT monitoreo_fisicoquimico_usuario_id_fkey 
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

-- Consumo Químicos Mensual
ALTER TABLE consumo_quimicos_mensual 
    DROP CONSTRAINT IF EXISTS consumo_quimicos_mensual_operador_id_fkey;

ALTER TABLE consumo_quimicos_mensual 
    RENAME COLUMN operador_id TO usuario_id;

ALTER TABLE consumo_quimicos_mensual 
    ADD CONSTRAINT consumo_quimicos_mensual_usuario_id_fkey 
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

-- 4. Actualizar los roles existentes (si hay datos)
UPDATE usuarios SET rol = 'ADMINISTRADOR'::userole WHERE rol::text = 'ADMIN';
UPDATE usuarios SET rol = 'OPERADOR'::userole WHERE rol::text IN ('OPERADOR', 'VISUALIZADOR');

-- ==================================================================
-- PARTE 2: OPTIMIZACIÓN CON ÍNDICES
-- ==================================================================

-- Índices en tabla usuarios
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);
CREATE INDEX IF NOT EXISTS idx_usuarios_login ON usuarios(username, activo);

-- Índices en tablas de registros
CREATE INDEX IF NOT EXISTS idx_control_operacion_usuario_id ON control_operacion(usuario_id);
CREATE INDEX IF NOT EXISTS idx_produccion_filtros_usuario_id ON produccion_filtros(usuario_id);
CREATE INDEX IF NOT EXISTS idx_control_consumo_usuario_id ON control_consumo_diario_quimicos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_control_cloro_usuario_id ON control_cloro_libre(usuario_id);
CREATE INDEX IF NOT EXISTS idx_monitoreo_fisicoquimico_usuario_id ON monitoreo_fisicoquimico(usuario_id);
CREATE INDEX IF NOT EXISTS idx_consumo_mensual_usuario_id ON consumo_quimicos_mensual(usuario_id);

-- Analizar tabla para optimizar consultas
ANALYZE usuarios;

-- ==================================================================
-- PARTE 3: CONSTRAINT DE ADMINISTRADOR ÚNICO
-- ==================================================================

-- Eliminar constraint anterior si existe
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS single_admin_constraint;
DROP INDEX IF EXISTS idx_single_admin;

-- Crear índice único parcial para asegurar solo un administrador
CREATE UNIQUE INDEX idx_single_admin 
ON usuarios (rol) 
WHERE rol = 'ADMINISTRADOR';

-- ==================================================================
-- PARTE 4: USUARIOS POR DEFECTO
-- ==================================================================

-- Crear usuario administrador
-- Usuario: admin
-- Contraseña: admin123 (será actualizada por Python)
INSERT INTO usuarios (
    nombre, 
    apellido, 
    email, 
    telefono, 
    activo, 
    username, 
    hashed_password, 
    rol, 
    fecha_contratacion,
    created_at,
    updated_at
) VALUES (
    'Administrador',
    'Sistema',
    'admin@esperanza.com',
    NULL,
    TRUE,
    'admin',
    'temp_hash_admin', -- Será actualizado por Python
    'ADMINISTRADOR',
    CURRENT_DATE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    apellido = EXCLUDED.apellido,
    email = EXCLUDED.email,
    activo = EXCLUDED.activo,
    rol = EXCLUDED.rol,
    updated_at = CURRENT_TIMESTAMP;

-- Crear usuario operador de ejemplo
-- Usuario: jperez
-- Contraseña: operador123 (será actualizada por Python)
INSERT INTO usuarios (
    nombre, 
    apellido, 
    email, 
    telefono, 
    activo, 
    username, 
    hashed_password, 
    rol, 
    fecha_contratacion,
    created_at,
    updated_at
) VALUES (
    'Juan',
    'Pérez',
    'juan.perez@esperanza.com',
    '555-0123',
    TRUE,
    'jperez',
    'temp_hash_operador', -- Será actualizado por Python
    'OPERADOR',
    CURRENT_DATE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    apellido = EXCLUDED.apellido,
    email = EXCLUDED.email,
    telefono = EXCLUDED.telefono,
    activo = EXCLUDED.activo,
    rol = EXCLUDED.rol,
    updated_at = CURRENT_TIMESTAMP;

-- ==================================================================
-- PARTE 5: COMENTARIOS Y DOCUMENTACIÓN
-- ==================================================================

COMMENT ON TABLE usuarios IS 'Tabla de usuarios del sistema con roles de Administrador y Operador';
COMMENT ON COLUMN usuarios.rol IS 'Rol del usuario: ADMINISTRADOR o OPERADOR';
COMMENT ON COLUMN usuarios.username IS 'Nombre de usuario único para iniciar sesión';
COMMENT ON COLUMN usuarios.hashed_password IS 'Contraseña hasheada del usuario';
COMMENT ON INDEX idx_single_admin IS 'Asegura que solo puede existir un usuario con rol ADMINISTRADOR';

COMMIT;

-- ==================================================================
-- VERIFICACIÓN FINAL
-- ==================================================================

SELECT 'Setup completado exitosamente' AS resultado;

SELECT 
    username, 
    nombre, 
    apellido, 
    rol, 
    activo,
    email
FROM usuarios 
ORDER BY rol DESC, username;

-- ==================================================================
-- IMPORTANTE: EJECUTAR DESPUÉS DE ESTE SCRIPT
-- ==================================================================
-- Usar Python para actualizar los hashes de contraseñas:
-- 
-- cd backend
-- python -c "from core.database import SessionLocal; from core.security import get_password_hash; from models.usuario import Usuario; db = SessionLocal(); admin = db.query(Usuario).filter(Usuario.username == 'admin').first(); admin.hashed_password = get_password_hash('admin123'); db.commit(); jperez = db.query(Usuario).filter(Usuario.username == 'jperez').first(); jperez.hashed_password = get_password_hash('operador123'); db.commit(); print('Contraseñas actualizadas'); db.close()"
--
-- Credenciales finales:
-- admin / admin123
-- jperez / operador123
-- ==================================================================
