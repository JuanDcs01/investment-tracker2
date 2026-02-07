# Investment Tracker - Estructura del Proyecto

```
investment-tracker/
│
├── 📁 app/                          # Paquete principal de la aplicación
│   ├── 📄 __init__.py              # Factory pattern, configuración de Flask
│   │
│   ├── 📁 models/                   # 🗄️ Capa de Datos (Modelos SQLAlchemy)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 instrument.py        # Modelo Instrument (stocks, ETFs, cryptos)
│   │   └── 📄 transaction.py       # Modelo Transaction (compras/ventas)
│   │
│   ├── 📁 routes/                   # 🛣️ Capa de Control (Endpoints)
│   │   ├── 📄 __init__.py
│   │   └── 📄 main_routes.py       # Todas las rutas de la aplicación
│   │
│   ├── 📁 services/                 # ⚙️ Capa de Lógica de Negocio
│   │   ├── 📄 __init__.py
│   │   ├── 📄 market_service.py    # Integración con Yahoo Finance API
│   │   └── 📄 portfolio_service.py # Cálculos de portafolio y métricas
│   │
│   ├── 📁 utils/                    # 🔧 Utilidades
│   │   ├── 📄 __init__.py
│   │   └── 📄 validators.py        # Validadores de entrada de datos
│   │
│   ├── 📁 templates/                # 🎨 Plantillas HTML (Jinja2)
│   │   ├── 📄 base.html            # Template base con Bootstrap
│   │   ├── 📄 dashboard.html       # Vista principal del dashboard
│   │   ├── 📄 transaction.html     # Página de registro de transacciones
│   │   └── 📁 errors/              # Páginas de error personalizadas
│   │       ├── 📄 404.html
│   │       └── 📄 500.html
│   │
│   └── 📁 static/                   # 🌐 Archivos Estáticos
│       ├── 📁 css/
│       │   └── 📄 style.css        # Estilos personalizados
│       └── 📁 js/
│           └── 📄 main.js          # JavaScript principal
│
├── 📄 config.py                     # ⚙️ Configuraciones (dev, prod)
├── 📄 run.py                        # 🚀 Punto de entrada principal
│
├── 📋 requirements.txt              # 📦 Dependencias de producción
├── 📋 requirements-dev.txt          # 🛠️ Dependencias de desarrollo
│
├── 📄 .env.example                 # 🔐 Plantilla de variables de entorno
├── 📄 .gitignore                   # 🚫 Archivos ignorados por Git
│
├── 📄 setup.sh                      # 🔧 Script de instalación automática
├── 📄 database_init.sql            # 🗃️ Script SQL de inicialización
├── 📄 create_sample_data.py        # 📊 Script para datos de prueba
│
├── 📖 README.md                    # Documentación principal
├── 📖 QUICKSTART.md                # Guía de inicio rápido
├── 📖 INSTALLATION.md              # Guía de instalación detallada
└── 📖 ARCHITECTURE.md              # Documentación de arquitectura

```

## Descripción de Archivos Principales

### 🎯 Archivos de Configuración

| Archivo                | Descripción                                            |
| ---------------------- | ------------------------------------------------------ |
| `config.py`            | Configuraciones de la aplicación (DB, Flask, etc.)     |
| `.env`                 | Variables de entorno (credenciales, no incluir en Git) |
| `.env.example`         | Plantilla para crear tu archivo .env                   |
| `requirements.txt`     | Dependencias necesarias para correr la app             |
| `requirements-dev.txt` | Herramientas adicionales para desarrollo               |

### 🚀 Archivos de Ejecución

| Archivo                 | Descripción                                    |
| ----------------------- | ---------------------------------------------- |
| `run.py`                | Punto de entrada, ejecutar con `python run.py` |
| `setup.sh`              | Script bash para instalación automatizada      |
| `database_init.sql`     | Script SQL para crear la base de datos         |
| `create_sample_data.py` | Genera datos de prueba                         |

### 🏗️ Estructura de la Aplicación (`app/`)

#### Models (Modelos de Datos)

- `instrument.py`: Define la tabla de instrumentos financieros
- `transaction.py`: Define la tabla de transacciones

#### Routes (Rutas/Controladores)

- `main_routes.py`: Todos los endpoints HTTP de la aplicación

#### Services (Servicios de Negocio)

- `market_service.py`: Comunicación con Yahoo Finance
- `portfolio_service.py`: Cálculos de métricas y análisis

#### Utils (Utilidades)

- `validators.py`: Validación de datos de entrada

#### Templates (Vistas HTML)

- `base.html`: Plantilla maestra con navegación
- `dashboard.html`: Dashboard principal con métricas
- `transaction.html`: Formulario de transacciones

#### Static (Recursos Estáticos)

- `css/style.css`: Estilos personalizados
- `js/main.js`: JavaScript de la aplicación

## 📊 Flujo de Datos

```
Usuario
  ↓
Templates (HTML)
  ↓
Routes (Controladores)
  ↓
Services (Lógica de Negocio) ←→ Yahoo Finance API
  ↓
Models (SQLAlchemy ORM)
  ↓
MySQL Database
```

## 🔄 Ciclo de Vida de una Request

1. **Usuario** hace una acción en el navegador
2. **Browser** envía HTTP request
3. **Flask** recibe la request en una ruta
4. **Controller** (routes) valida datos
5. **Service** ejecuta lógica de negocio
6. **Model** interactúa con la base de datos
7. **Response** se envía de vuelta al navegador
8. **Template** renderiza la vista final

## 🗃️ Esquema de Base de Datos

```sql
┌──────────────────────────────┐
│       instruments            │
├──────────────────────────────┤
│ id (PK)                      │
│ symbol (UNIQUE)              │
│ instrument_type              │
│ quantity                     │
│ average_purchase_price       │
│ total_cost                   │
│ total_commission             │
│ created_at                   │
│ updated_at                   │
└──────────────┬───────────────┘
               │
               │ 1:N relationship
               │
               ↓
┌──────────────────────────────┐
│       transactions           │
├──────────────────────────────┤
│ id (PK)                      │
│ instrument_id (FK)           │
│ transaction_type             │
│ quantity                     │
│ price                        │
│ commission                   │
│ total_paid                   │
│ transaction_date             │
│ created_at                   │
└──────────────────────────────┘
```

## 📦 Dependencias Principales

| Paquete    | Versión | Propósito              |
| ---------- | ------- | ---------------------- |
| Flask      | 3.0.0   | Framework web          |
| SQLAlchemy | 3.1.1   | ORM para base de datos |
| PyMySQL    | 1.1.0   | Driver MySQL           |
| yfinance   | 0.2.33  | API de Yahoo Finance   |
| Bootstrap  | 5.3.2   | Framework CSS          |
| Chart.js   | 4.4.1   | Gráficos interactivos  |

## 🎨 Tecnologías Frontend

- **HTML5**: Estructura
- **Bootstrap 5.3**: Diseño responsive
- **JavaScript ES6**: Interactividad
- **Chart.js**: Visualizaciones
- **Bootstrap Icons**: Iconografía

## 🔐 Seguridad

- ✅ SQLAlchemy ORM (previene SQL injection)
- ✅ Jinja2 auto-escaping (previene XSS)
- ✅ Variables de entorno para credenciales
- ✅ Validación en múltiples capas
- ⚠️ CSRF protection (pendiente de implementar)

## 📈 Características Implementadas

- ✅ Dashboard con métricas en tiempo real
- ✅ Soporte para Stocks, ETFs y Cryptos
- ✅ Registro de compras y ventas
- ✅ Cálculo automático de retornos
- ✅ Gráficos de distribución
- ✅ Integración con Yahoo Finance
- ✅ Validación robusta de datos
- ✅ Responsive design
- ✅ Manejo de errores

## 🚀 Siguientes Pasos para Extender

1. **Autenticación**: Agregar usuarios y login
2. **Múltiples Portfolios**: Un usuario, varios portfolios
3. **Reportes**: Exportar a PDF/Excel
4. **Gráficos Históricos**: Evolución del portafolio
5. **Alertas**: Notificaciones de precios
6. **API REST**: Endpoints públicos
7. **Tests**: Cobertura completa

## 📚 Recursos de Documentación

| Documento         | Contenido                     |
| ----------------- | ----------------------------- |
| `README.md`       | Visión general y guía básica  |
| `QUICKSTART.md`   | Instalación en 5 minutos      |
| `INSTALLATION.md` | Guía detallada de instalación |
| `ARCHITECTURE.md` | Diseño técnico y arquitectura |
| Este archivo      | Estructura del proyecto       |

## 🛠️ Comandos Rápidos

```bash
# Instalar
pip install -r requirements.txt

# Inicializar DB
python run.py init-db

# Crear datos de prueba
python create_sample_data.py

# Ejecutar
python run.py

# Acceder
http://localhost:5000
```

---

**Proyecto diseñado con ❤️ siguiendo las mejores prácticas de desarrollo web**
