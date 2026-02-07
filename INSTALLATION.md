# Guía de Instalación Detallada - Investment Tracker

Esta guía proporciona instrucciones paso a paso para instalar y configurar Investment Tracker.

## Requisitos del Sistema

### Software Requerido

1. **Python 3.8 o superior**
   - Descargar: https://www.python.org/downloads/
   - Verificar instalación: `python3 --version`

2. **MySQL 5.7 o superior**
   - Descargar: https://dev.mysql.com/downloads/mysql/
   - Verificar instalación: `mysql --version`

3. **pip** (Gestor de paquetes de Python)
   - Generalmente viene con Python
   - Verificar: `pip --version`

4. **Git** (Opcional, para clonar el repositorio)
   - Descargar: https://git-scm.com/downloads

## Instalación Paso a Paso

### Opción 1: Instalación Automática (Linux/Mac)

```bash
# 1. Clonar o descargar el proyecto
git clone <repository-url>
cd investment-tracker

# 2. Ejecutar script de instalación
chmod +x setup.sh
./setup.sh

# 3. Seguir las instrucciones en pantalla
```

### Opción 2: Instalación Manual

#### Paso 1: Preparar el Entorno

```bash
# Navegar al directorio del proyecto
cd investment-tracker

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# Actualizar pip
pip install --upgrade pip
```

#### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:

- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Migrate 4.0.5
- PyMySQL 1.1.0
- yfinance 0.2.33
- python-dotenv 1.0.0
- Y otras dependencias

#### Paso 3: Configurar Base de Datos MySQL

**3a. Crear Base de Datos**

```bash
# Conectar a MySQL
mysql -u root -p

# Ejecutar en el prompt de MySQL:
CREATE DATABASE investment_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Crear usuario (opcional, recomendado para producción)
CREATE USER 'investment_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON investment_tracker.* TO 'investment_user'@'localhost';
FLUSH PRIVILEGES;

# Salir
EXIT;
```

**O usar el script SQL:**

```bash
mysql -u root -p < database_init.sql
```

**3b. Configurar Variables de Entorno**

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tu editor favorito
nano .env
# o
vim .env
# o
code .env
```

Configurar las siguientes variables:

```
# Credenciales de MySQL
DB_USER=investment_user
DB_PASSWORD=tu_contraseña_segura
DB_HOST=localhost
DB_PORT=3306
DB_NAME=investment_tracker

# Flask
FLASK_APP=run.py
FLASK_ENV=development

# Generar una clave secreta (en Python):
# import secrets; print(secrets.token_hex(32))
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
```

#### Paso 4: Inicializar las Tablas

```bash
# Método 1: Usando el comando personalizado
python run.py init-db

# Método 2: Usando Flask CLI
flask init-db

# Método 3: Usando Flask-Migrate (si prefieres migraciones)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### Paso 5: (Opcional) Crear Datos de Prueba

```bash
python create_sample_data.py
```

Esto creará:

- 6 instrumentos de ejemplo (AAPL, MSFT, SPY, QQQ, BTC, ETH)
- Varias transacciones de prueba
- Datos listos para explorar la aplicación

#### Paso 6: Ejecutar la Aplicación

```bash
# Método 1: Usar run.py
python run.py

# Método 2: Usar Flask
flask run

# Método 3: Especificar host y puerto
python run.py --host 0.0.0.0 --port 5000
```

La aplicación estará disponible en: `http://localhost:5000`

## Verificación de la Instalación

### Verificar Base de Datos

```sql
-- Conectar a MySQL
mysql -u investment_user -p investment_tracker

-- Verificar tablas
SHOW TABLES;

-- Debería mostrar:
-- +-----------------------------+
-- | Tables_in_investment_tracker|
-- +-----------------------------+
-- | instruments                 |
-- | transactions                |
-- +-----------------------------+

-- Ver estructura
DESCRIBE instruments;
DESCRIBE transactions;
```

### Verificar la Aplicación

1. **Abrir en Navegador**: `http://localhost:5000`
2. **Verificar Dashboard**: Debería cargar sin errores
3. **Agregar Instrumento**: Intenta agregar AAPL (stock)
4. **Ver Logs**: Revisa la consola para errores

## Solución de Problemas Comunes

### Error: "No module named 'app'"

**Causa**: El entorno virtual no está activado o las dependencias no están instaladas.

**Solución**:

```bash
source venv/bin/activate  # Activar entorno virtual
pip install -r requirements.txt  # Reinstalar dependencias
```

### Error: "Access denied for user"

**Causa**: Credenciales incorrectas en .env

**Solución**:

1. Verificar usuario y contraseña en MySQL
2. Actualizar .env con credenciales correctas
3. Asegurar que el usuario tiene permisos en la base de datos

### Error: "Unknown database 'investment_tracker'"

**Causa**: La base de datos no existe

**Solución**:

```bash
mysql -u root -p -e "CREATE DATABASE investment_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Error: "Table 'instruments' doesn't exist"

**Causa**: Las tablas no han sido creadas

**Solución**:

```bash
python run.py init-db
```

### Error al Conectar con Yahoo Finance

**Causa**: Problemas de red o símbolo inválido

**Solución**:

1. Verificar conexión a internet
2. Probar con símbolos conocidos: AAPL, MSFT, BTC
3. Para cryptos, usar solo el símbolo base (BTC, no BTC-USD)

### Puerto 5000 ya en uso

**Causa**: Otro proceso está usando el puerto

**Solución**:

```bash
# Encontrar el proceso
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Usar otro puerto
flask run --port 5001
```

## Configuración Avanzada

### Usar PostgreSQL en lugar de MySQL

1. Instalar psycopg2:

```bash
pip install psycopg2-binary
```

2. Modificar config.py:

```python
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

### Configurar para Producción

1. **Cambiar modo**:

```
FLASK_ENV=production
```

2. **Generar SECRET_KEY segura**:

```python
import secrets
print(secrets.token_hex(32))
```

3. **Usar servidor WSGI**:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

4. **Configurar Nginx** (ejemplo):

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Habilitar HTTPS

1. **Obtener certificado SSL** (Let's Encrypt):

```bash
sudo certbot --nginx -d tu-dominio.com
```

2. **Configurar Flask**:

```python
if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Para desarrollo
```

## Actualización de la Aplicación

```bash
# Activar entorno virtual
source venv/bin/activate

# Actualizar código (si usas Git)
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Ejecutar migraciones (si las hay)
flask db upgrade

# Reiniciar aplicación
```

## Backup y Restauración

### Backup de Base de Datos

```bash
mysqldump -u investment_user -p investment_tracker > backup_$(date +%Y%m%d).sql
```

### Restaurar Base de Datos

```bash
mysql -u investment_user -p investment_tracker < backup_20240101.sql
```

## Recursos Adicionales

- **Documentación Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Bootstrap**: https://getbootstrap.com/docs/
- **yFinance**: https://pypi.org/project/yfinance/

## Soporte

Si encuentras problemas:

1. Revisa los logs en la consola
2. Verifica el archivo README.md
3. Revisa esta guía de instalación
4. Crea un issue en GitHub con:
   - Descripción del problema
   - Logs de error
   - Pasos para reproducir
   - Tu entorno (OS, versión Python, etc.)
