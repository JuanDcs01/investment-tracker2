# Arquitectura del Proyecto - Investment Tracker

Este documento describe la arquitectura, patrones de diseño y decisiones técnicas implementadas en Investment Tracker.

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura de Capas](#arquitectura-de-capas)
3. [Patrones de Diseño](#patrones-de-diseño)
4. [Estructura de Directorios](#estructura-de-directorios)
5. [Flujo de Datos](#flujo-de-datos)
6. [Base de Datos](#base-de-datos)
7. [Servicios](#servicios)
8. [Validaciones](#validaciones)
9. [Seguridad](#seguridad)
10. [Escalabilidad](#escalabilidad)

## Visión General

Investment Tracker es una aplicación web MVC (Model-View-Controller) construida con Flask que sigue principios de arquitectura limpia y separación de responsabilidades.

### Tecnologías Principales

- **Backend**: Flask 3.0, SQLAlchemy
- **Base de Datos**: MySQL 5.7+
- **Frontend**: Bootstrap 5.3, Chart.js 4.4
- **API Externa**: Yahoo Finance (yfinance)

### Principios Arquitectónicos

1. **Separation of Concerns**: Cada capa tiene responsabilidades bien definidas
2. **DRY (Don't Repeat Yourself)**: Código reutilizable en servicios y utilidades
3. **SOLID Principles**: Especialmente Single Responsibility y Dependency Inversion
4. **Factory Pattern**: Para la creación de la aplicación Flask
5. **Service Layer**: Lógica de negocio separada de controladores

## Arquitectura de Capas

```
┌─────────────────────────────────────────────────────┐
│                  Presentation Layer                  │
│              (Templates + Static Files)              │
├─────────────────────────────────────────────────────┤
│                  Controller Layer                    │
│                  (Routes/Blueprints)                 │
├─────────────────────────────────────────────────────┤
│                   Service Layer                      │
│         (Business Logic + External APIs)             │
├─────────────────────────────────────────────────────┤
│                  Persistence Layer                   │
│              (Models + SQLAlchemy ORM)               │
├─────────────────────────────────────────────────────┤
│                    Database Layer                    │
│                   (MySQL Database)                   │
└─────────────────────────────────────────────────────┘
```

### 1. Presentation Layer (Capa de Presentación)

**Responsabilidad**: Renderizar la interfaz de usuario

**Componentes**:

- Templates HTML (Jinja2)
- Archivos CSS y JavaScript
- Bootstrap components
- Chart.js visualizations

**Ubicación**: `app/templates/`, `app/static/`

### 2. Controller Layer (Capa de Control)

**Responsabilidad**: Manejar requests HTTP y coordinar respuestas

**Componentes**:

- Blueprints de Flask
- Rutas (endpoints)
- Manejo de formularios
- Respuestas JSON para AJAX

**Ubicación**: `app/routes/`

**Ejemplo**:

```python
@bp.route('/add-instrument', methods=['POST'])
def add_instrument():
    # 1. Validar entrada
    # 2. Llamar a servicios
    # 3. Retornar respuesta
```

### 3. Service Layer (Capa de Servicio)

**Responsabilidad**: Implementar lógica de negocio

**Componentes**:

- `MarketService`: Integración con Yahoo Finance
- `PortfolioService`: Cálculos de portafolio

**Ubicación**: `app/services/`

**Ventajas**:

- Lógica reutilizable
- Fácil de testear
- Independiente de Flask
- Permite cambiar implementaciones

### 4. Persistence Layer (Capa de Persistencia)

**Responsabilidad**: Definir estructura de datos y acceso a BD

**Componentes**:

- Modelos SQLAlchemy
- Relaciones entre entidades
- Métodos de instancia

**Ubicación**: `app/models/`

### 5. Database Layer

**Responsabilidad**: Almacenamiento persistente

**Tecnología**: MySQL con InnoDB

## Patrones de Diseño

### 1. Application Factory Pattern

**Ubicación**: `app/__init__.py`

**Propósito**: Crear múltiples instancias de la app con diferentes configuraciones

```python
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # ... inicialización
    return app
```

**Beneficios**:

- Testing más fácil
- Múltiples configuraciones (dev, prod)
- Mejor organización del código

### 2. Blueprint Pattern

**Ubicación**: `app/routes/main_routes.py`

**Propósito**: Modularizar rutas y vistas

```python
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # ...
```

**Beneficios**:

- Aplicación modular
- Fácil agregar nuevos módulos
- Namespacing de rutas

### 3. Service Layer Pattern

**Ubicación**: `app/services/`

**Propósito**: Separar lógica de negocio de controladores

```python
class PortfolioService:
    @staticmethod
    def calculate_portfolio_metrics(instruments):
        # Lógica compleja aquí
```

**Beneficios**:

- Reutilización de código
- Testeo unitario más fácil
- Cambios no afectan controladores

### 4. Repository Pattern (Implícito)

**Ubicación**: Métodos en modelos

**Propósito**: Abstraer acceso a datos

```python
class Instrument(db.Model):
    def update_metrics(self):
        # Acceso a datos encapsulado
```

### 5. Validator Pattern

**Ubicación**: `app/utils/validators.py`

**Propósito**: Validación consistente de datos

```python
class Validator:
    @staticmethod
    def validate_symbol(symbol):
        # Validación centralizada
```

## Estructura de Directorios

```
investment-tracker/
│
├── app/                          # Paquete principal de la aplicación
│   ├── __init__.py              # Application factory
│   │
│   ├── models/                   # Capa de persistencia
│   │   ├── __init__.py
│   │   ├── instrument.py        # Modelo Instrument
│   │   └── transaction.py       # Modelo Transaction
│   │
│   ├── routes/                   # Capa de control
│   │   ├── __init__.py
│   │   └── main_routes.py       # Rutas principales
│   │
│   ├── services/                 # Capa de servicio
│   │   ├── __init__.py
│   │   ├── market_service.py    # Integración Yahoo Finance
│   │   └── portfolio_service.py # Lógica de portafolio
│   │
│   ├── utils/                    # Utilidades
│   │   ├── __init__.py
│   │   └── validators.py        # Validadores
│   │
│   ├── templates/                # Plantillas HTML
│   │   ├── base.html            # Template base
│   │   ├── dashboard.html       # Vista principal
│   │   ├── transaction.html     # Registro de movimientos
│   │   └── errors/              # Páginas de error
│   │       ├── 404.html
│   │       └── 500.html
│   │
│   └── static/                   # Archivos estáticos
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
│
├── config.py                     # Configuraciones
├── run.py                        # Punto de entrada
├── requirements.txt              # Dependencias
├── .env.example                 # Template de variables de entorno
├── setup.sh                      # Script de instalación
├── create_sample_data.py        # Script de datos de prueba
├── database_init.sql            # Script SQL inicial
├── README.md                    # Documentación principal
├── INSTALLATION.md              # Guía de instalación
└── ARCHITECTURE.md              # Este archivo
```

## Flujo de Datos

### Ejemplo: Agregar Instrumento

```
1. Usuario hace clic en "Agregar Instrumento"
   ↓
2. Frontend envía POST a /add-instrument
   ↓
3. Controller (main_routes.py):
   - Recibe datos del formulario
   - Llama a Validator.validate_symbol()
   - Llama a Validator.validate_instrument_type()
   ↓
4. Service Layer (market_service.py):
   - MarketService.verify_symbol()
   - Consulta Yahoo Finance API
   ↓
5. Persistence Layer (models/instrument.py):
   - Crea instancia de Instrument
   - db.session.add(instrument)
   - db.session.commit()
   ↓
6. Database Layer:
   - INSERT en tabla instruments
   ↓
7. Controller retorna JSON response
   ↓
8. Frontend muestra resultado y recarga página
```

### Ejemplo: Calcular Métricas del Portfolio

```
1. Usuario accede al dashboard (GET /)
   ↓
2. Controller:
   - Obtiene todos los instrumentos
   - Llama a PortfolioService.calculate_portfolio_metrics()
   ↓
3. Service Layer:
   - Para cada instrumento:
     * Llama a MarketService.get_current_price()
     * Llama a MarketService.get_previous_close()
   - Calcula métricas agregadas
   ↓
4. Service retorna diccionario con métricas
   ↓
5. Controller pasa datos a template
   ↓
6. Template renderiza con Jinja2
   ↓
7. Frontend muestra dashboard con gráficos (Chart.js)
```

## Base de Datos

### Esquema de Entidades

```
┌─────────────────────┐
│    Instruments      │
├─────────────────────┤
│ id (PK)             │
│ symbol              │
│ instrument_type     │
│ quantity            │
│ average_purchase_price│
│ total_cost          │
│ total_commission    │
│ created_at          │
│ updated_at          │
└─────────────────────┘
          │
          │ 1:N
          │
          ▼
┌─────────────────────┐
│   Transactions      │
├─────────────────────┤
│ id (PK)             │
│ instrument_id (FK)  │
│ transaction_type    │
│ quantity            │
│ price               │
│ commission          │
│ total_paid          │
│ transaction_date    │
│ created_at          │
└─────────────────────┘
```

### Decisiones de Diseño

#### 1. Precision Numérica

- **Cantidad**: `DECIMAL(20, 12)` - Soporta cryptos con muchos decimales
- **Precio**: `DECIMAL(20, 8)` - Soporta precios precisos de cryptos
- **Dinero**: `DECIMAL(20, 2)` - Precisión estándar para currency

**Razón**: Evitar errores de punto flotante en cálculos financieros

#### 2. Cascade Delete

```python
FOREIGN KEY (instrument_id) REFERENCES instruments(id) ON DELETE CASCADE
```

**Razón**: Al eliminar un instrumento, se eliminan sus transacciones automáticamente

#### 3. Indexes

```sql
INDEX idx_symbol (symbol)
INDEX idx_symbol_type (symbol, instrument_type)
INDEX idx_instrument_id (instrument_id)
```

**Razón**: Optimizar consultas frecuentes

#### 4. ENUM Types

```sql
instrument_type ENUM('stock', 'etf', 'crypto')
transaction_type ENUM('buy', 'sell')
```

**Razón**: Validación a nivel de BD y mejor rendimiento

## Servicios

### MarketService

**Responsabilidades**:

- Verificar símbolos en Yahoo Finance
- Obtener precios actuales
- Obtener precios de cierre anterior
- Cache de datos (5 minutos)

**Métodos Principales**:

```python
verify_symbol(symbol, instrument_type) -> bool
get_current_price(symbol, instrument_type) -> float
get_previous_close(symbol, instrument_type) -> float
get_batch_prices(symbols_data) -> dict
```

**Cache Strategy**:

- Cache en memoria con timestamp
- TTL de 5 minutos
- Reduce llamadas a API externa

### PortfolioService

**Responsabilidades**:

- Calcular métricas del portafolio
- Calcular métricas por instrumento
- Generar datos para gráficos

**Métodos Principales**:

```python
calculate_portfolio_metrics(instruments) -> dict
calculate_instrument_metrics(instrument) -> dict
get_portfolio_distribution(instruments) -> dict
```

**Cálculos Clave**:

1. **Total Invertido**: Suma de `total_cost` de todos los instrumentos
2. **Valor Actual**: Suma de `quantity * current_price`
3. **Ganancia Hoy**: Diferencia vs. precio de cierre anterior
4. **Retorno Neto**: `current_value - total_cost` (incluye comisiones)

## Validaciones

### Niveles de Validación

#### 1. Frontend (JavaScript)

```javascript
// Validación inmediata
input.addEventListener("input", function () {
  if (!isValid(this.value)) {
    this.classList.add("is-invalid");
  }
});
```

**Propósito**: Feedback inmediato al usuario

#### 2. Backend (Python Validators)

```python
is_valid, error, value = Validator.validate_quantity(quantity_str)
if not is_valid:
    return error_response(error)
```

**Propósito**: Seguridad y validación definitiva

#### 3. Database (Constraints)

```sql
quantity DECIMAL(20, 12) NOT NULL
CHECK (quantity >= 0)
```

**Propósito**: Integridad de datos

### Tipos de Validación

1. **Tipo de Datos**: Strings, números, fechas
2. **Rangos**: Min/max values, longitud
3. **Formato**: Regex para símbolos
4. **Lógica de Negocio**: No vender más de lo que se posee
5. **Existencia**: Verificar en Yahoo Finance

## Seguridad

### Implementaciones de Seguridad

#### 1. SQL Injection Protection

**Método**: SQLAlchemy ORM con prepared statements

```python
# Seguro - usa parámetros
instrument = Instrument.query.filter_by(symbol=symbol).first()

# NO hacer - vulnerable
db.session.execute(f"SELECT * FROM instruments WHERE symbol = '{symbol}'")
```

#### 2. XSS Protection

**Método**: Jinja2 auto-escaping

```html
<!-- Seguro - Jinja2 escapa automáticamente -->
<td>{{ inst.symbol }}</td>

<!-- NO hacer - vulnerable -->
<td>${unsafe_html}</td>
```

#### 3. CSRF Protection

**Pendiente de Implementar**: Flask-WTF

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

#### 4. Environment Variables

**Método**: python-dotenv

```python
# Seguro - no en código
SECRET_KEY = os.getenv('SECRET_KEY')

# NO hacer - vulnerable
SECRET_KEY = 'mi-clave-secreta'
```

#### 5. Input Validation

**Método**: Validators centralizados

```python
# Todos los inputs validados
is_valid, error, value = Validator.validate_price(price_str)
```

## Escalabilidad

### Estrategias de Escalabilidad

#### 1. Horizontal Scaling

**Actual**: Aplicación stateless
**Futuro**: Múltiples instancias con load balancer

```
┌────────────────┐
│ Load Balancer  │
└────────┬───────┘
         │
    ┌────┴────┬────────┬────────┐
    │         │        │        │
┌───▼───┐ ┌───▼───┐ ┌──▼───┐ ┌──▼───┐
│ App 1 │ │ App 2 │ │ App 3│ │ App N│
└───────┘ └───────┘ └──────┘ └──────┘
```

#### 2. Database Optimization

**Actual**:

- Indexes en columnas frecuentes
- Consultas optimizadas

**Futuro**:

- Read replicas para consultas
- Write master para modificaciones
- Connection pooling

#### 3. Caching

**Actual**:

- Cache en memoria para precios (5 min)

**Futuro**:

- Redis para cache distribuido
- Cache de sesiones
- Cache de resultados de queries

```python
# Ejemplo con Redis
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.memoize(timeout=300)
def get_current_price(symbol):
    # ...
```

#### 4. Asynchronous Tasks

**Futuro**: Celery para tareas pesadas

```python
# Ejemplo con Celery
@celery.task
def update_all_prices():
    for instrument in Instrument.query.all():
        fetch_current_price(instrument.symbol)
```

#### 5. API Rate Limiting

**Futuro**: Flask-Limiter

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/refresh-prices')
@limiter.limit("10 per minute")
def refresh_prices():
    # ...
```

### Métricas y Monitoreo

**Recomendaciones**:

1. Application Performance Monitoring (APM)
2. Database query performance
3. API response times
4. Error rates
5. User metrics

**Herramientas Sugeridas**:

- New Relic / DataDog (APM)
- Sentry (Error tracking)
- Prometheus + Grafana (Métricas)

## Testing Strategy

### Tipos de Tests (Pendiente)

#### 1. Unit Tests

```python
# tests/test_validators.py
def test_validate_quantity():
    is_valid, error, value = Validator.validate_quantity("10.5")
    assert is_valid == True
    assert value == Decimal("10.5")
```

#### 2. Integration Tests

```python
# tests/test_services.py
def test_market_service():
    price = MarketService.get_current_price("AAPL", "stock")
    assert price > 0
```

#### 3. End-to-End Tests

```python
# tests/test_routes.py
def test_add_instrument(client):
    response = client.post('/add-instrument', data={
        'symbol': 'AAPL',
        'instrument_type': 'stock'
    })
    assert response.status_code == 200
```

## Mejoras Futuras

### Corto Plazo

1. [ ] Implementar CSRF protection
2. [ ] Agregar tests unitarios
3. [ ] Logging estructurado
4. [ ] Documentación de API

### Mediano Plazo

1. [ ] Autenticación de usuarios
2. [ ] Múltiples portafolios por usuario
3. [ ] Exportar reportes (PDF, Excel)
4. [ ] Gráficos de rendimiento histórico
5. [ ] Alertas de precio

### Largo Plazo

1. [ ] API REST pública
2. [ ] Aplicación móvil
3. [ ] Machine learning para predicciones
4. [ ] Integración con brokers
5. [ ] Trading automatizado

## Conclusión

La arquitectura de Investment Tracker está diseñada para ser:

- **Mantenible**: Código organizado y bien documentado
- **Escalable**: Fácil agregar nuevas funcionalidades
- **Segura**: Validaciones en múltiples niveles
- **Testeable**: Separación de responsabilidades
- **Performante**: Caching y optimizaciones

El proyecto sigue best practices de desarrollo web y está listo para evolucionar según las necesidades del negocio.
