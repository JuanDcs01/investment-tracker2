# Investment Tracker

Una aplicación web completa para rastrear y gestionar inversiones en acciones, ETFs y criptomonedas, construida con Flask, SQLAlchemy, yFinance y Bootstrap.

## 🚀 Características

- **Dashboard Interactivo**: Visualiza tu portafolio con métricas en tiempo real
- **Múltiples Instrumentos**: Soporte para Stocks, ETFs y Criptomonedas
- **Gestión de Transacciones**: Registra compras y ventas con comisiones
- **Integración con Yahoo Finance**: Precios actualizados automáticamente
- **Análisis Visual**: Gráficos de distribución por tipo, riesgo e instrumento
- **Métricas Avanzadas**:
  - Total Invertido
  - Valor Actual de Mercado
  - Ganancia del Día
  - Retorno Neto (considerando comisiones)

## 📋 Requisitos Previos

- Python 3.8 o superior
- MySQL 5.7 o superior
- pip (gestor de paquetes de Python)

## 🛠️ Instalación

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd investment-tracker
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

Crear una base de datos MySQL:

```sql
CREATE DATABASE investment_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configurar Variables de Entorno

Copiar el archivo `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_contraseña_mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=investment_tracker
SECRET_KEY=tu-clave-secreta-aqui
```

### 6. Inicializar Base de Datos

```bash
python run.py init-db
```

O usando Flask CLI:

```bash
flask init-db
```

### 7. Ejecutar la Aplicación

```bash
python run.py
```

O:

```bash
flask run
```

La aplicación estará disponible en: `http://localhost:5000`

## 📁 Estructura del Proyecto

```
investment-tracker/
├── app/
│   ├── __init__.py           # Inicialización de la aplicación Flask
│   ├── models/               # Modelos de base de datos
│   │   ├── __init__.py
│   │   ├── instrument.py     # Modelo Instrument
│   │   └── transaction.py    # Modelo Transaction
│   ├── routes/               # Rutas y endpoints
│   │   ├── __init__.py
│   │   └── main_routes.py    # Rutas principales
│   ├── services/             # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── market_service.py     # Integración con Yahoo Finance
│   │   └── portfolio_service.py  # Cálculos de portafolio
│   ├── utils/                # Utilidades
│   │   ├── __init__.py
│   │   └── validators.py     # Validadores de entrada
│   ├── templates/            # Plantillas HTML
│   │   ├── base.html         # Plantilla base
│   │   ├── dashboard.html    # Dashboard principal
│   │   ├── transaction.html  # Registro de transacciones
│   │   └── errors/           # Páginas de error
│   └── static/               # Archivos estáticos
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── config.py                 # Configuración de la aplicación
├── run.py                    # Punto de entrada
├── requirements.txt          # Dependencias
├── .env.example             # Plantilla de variables de entorno
├── .gitignore               # Archivos ignorados por Git
└── README.md                # Este archivo
```

## 🎯 Uso

### Agregar Instrumentos

1. En el dashboard, haz clic en "Agregar Instrumento"
2. Ingresa el símbolo (ej: AAPL, BTC, SPY)
3. Selecciona el tipo (Stock, ETF, Crypto)
4. El sistema verificará que el símbolo existe en Yahoo Finance
5. **Nota**: Para criptomonedas, NO es necesario incluir -USD

### Registrar Transacciones

1. En la tabla de instrumentos, haz clic en el ícono de lápiz
2. Selecciona el tipo de movimiento (Compra o Venta)
3. Ingresa:
   - Cantidad (hasta 12 decimales)
   - Precio (hasta 8 decimales)
   - Comisión del broker
   - Fecha de la transacción
4. El total se calcula automáticamente
5. Haz clic en "Registrar Transacción"

### Visualizar Métricas

El dashboard muestra:

- **Total Invertido**: Suma de todas las compras + comisiones
- **Valor Actual**: Valor de mercado actual del portafolio
- **Ganancia Hoy**: Diferencia vs. cierre anterior
- **Retorno Neto**: Ganancia real considerando comisiones

### Gráficos de Distribución

Tres gráficos de pastel muestran:

1. **Por Tipo**: Stock, ETF, Crypto
2. **Por Riesgo**:
   - Medio: ETFs
   - Alto: Stocks y Cryptos
3. **Por Instrumento**: Top 10 instrumentos

## 🔧 Comandos Flask CLI

```bash
# Inicializar base de datos
flask init-db

# Resetear base de datos (¡elimina todos los datos!)
flask reset-db

# Abrir shell interactivo
flask shell

# Ejecutar migraciones (si usas Flask-Migrate)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🧪 Validaciones Implementadas

### Símbolos

- 1-20 caracteres
- Solo alfanuméricos y guiones
- Verificación en Yahoo Finance

### Cantidades

- Máximo 12 decimales
- Positivas y mayores que cero
- Validación de inventario en ventas

### Precios

- Máximo 8 decimales
- Mayores que cero

### Comisiones

- Máximo 2 decimales
- No negativas

### Fechas

- Formato YYYY-MM-DD
- No futuras

## 🛡️ Seguridad

- Validación de entrada en servidor
- Protección contra SQL injection (SQLAlchemy ORM)
- Sanitización de datos de usuario
- Variables de entorno para credenciales
- Gestión de errores con logging

## 📊 API Endpoints

### Frontend Routes

- `GET /` - Dashboard principal
- `POST /add-instrument` - Agregar instrumento
- `POST /delete-instrument/<id>` - Eliminar instrumento
- `GET /transaction/<id>` - Ver transacciones
- `POST /transaction/<id>` - Registrar transacción

### API Routes

- `POST /api/refresh-prices` - Actualizar precios de mercado

## 🔄 Actualización de Precios

Los precios se actualizan:

- Automáticamente al cargar el dashboard
- Cache de 5 minutos para optimizar requests
- Manualmente con el botón "Actualizar Precios"

## 🐛 Solución de Problemas

### Error de conexión a MySQL

```bash
# Verificar que MySQL esté corriendo
mysql -u root -p

# Verificar credenciales en .env
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
```

### Error al agregar símbolo

- Verifica que el símbolo existe en Yahoo Finance
- Para cryptos, usa el símbolo base (BTC, ETH, no BTC-USD)
- Revisa la conexión a internet

### Precios no se actualizan

```bash
# Limpiar cache manualmente en Flask shell
flask shell
>>> from app.services import MarketService
>>> MarketService.clear_cache()
```

## 📝 Desarrollo

### Agregar Nuevos Modelos

1. Crear archivo en `app/models/`
2. Definir modelo con SQLAlchemy
3. Importar en `app/models/__init__.py`
4. Ejecutar migraciones

### Agregar Nuevas Rutas

1. Crear/editar archivo en `app/routes/`
2. Definir blueprint y rutas
3. Registrar blueprint en `app/__init__.py`

### Agregar Nuevos Servicios

1. Crear archivo en `app/services/`
2. Implementar lógica de negocio
3. Importar en `app/services/__init__.py`

## 🚀 Despliegue en Producción

### Configuración

1. Cambiar `FLASK_ENV=production` en `.env`
2. Generar SECRET_KEY segura:

```python
import secrets
print(secrets.token_hex(32))
```

3. Configurar base de datos de producción
4. Usar servidor WSGI (Gunicorn, uWSGI)

### Ejemplo con Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

### Variables de Entorno Producción

```
FLASK_ENV=production
SECRET_KEY=tu-clave-muy-segura
DB_HOST=tu-servidor-mysql
# ... otras configuraciones
```

## 📚 Tecnologías Utilizadas

- **Backend**: Flask 3.0, SQLAlchemy, PyMySQL
- **Frontend**: Bootstrap 5.3, Chart.js 4.4
- **Datos**: yFinance API
- **Base de Datos**: MySQL 5.7+
- **Validación**: Decimal (Python), Custom Validators

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👥 Autor

Desarrollado con ❤️ usando Flask y Bootstrap

## 🙏 Agradecimientos

- Yahoo Finance por la API de datos de mercado
- Bootstrap por el framework CSS
- Chart.js por las visualizaciones
- Flask y SQLAlchemy por el excelente framework
