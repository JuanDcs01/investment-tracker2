# 🚀 Quick Start - Investment Tracker

Guía rápida para poner en marcha la aplicación en 5 minutos.

## Requisitos Previos

- Python 3.8+
- MySQL 5.7+
- 10 minutos de tu tiempo

## Instalación Rápida

### 1. Descomprimir el Proyecto

```bash
tar -xzf investment-tracker-complete.tar.gz
cd investment-tracker
```

### 2. Configurar Base de Datos

```sql
-- Conectar a MySQL
mysql -u root -p

-- Ejecutar estos comandos
CREATE DATABASE investment_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'investment_user'@'localhost' IDENTIFIED BY 'tu_contraseña';
GRANT ALL PRIVILEGES ON investment_tracker.* TO 'investment_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Configurar Aplicación

```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar .env (usar tu editor favorito)
nano .env
```

Configurar estas líneas en `.env`:

```
DB_USER=investment_user
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_NAME=investment_tracker
SECRET_KEY=genera-una-clave-secreta-aqui
```

### 4. Instalar y Ejecutar

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
python run.py init-db

# (Opcional) Crear datos de prueba
python create_sample_data.py

# Ejecutar aplicación
python run.py
```

### 5. Abrir en Navegador

Ir a: **http://localhost:5000**

## Primeros Pasos

### Agregar tu Primer Instrumento

1. Clic en **"Agregar Instrumento"**
2. Ingresa:
   - Símbolo: `AAPL`
   - Tipo: `Stock`
3. Clic en **"Agregar"**

### Registrar una Transacción

1. Clic en el ícono de lápiz (✏️) del instrumento
2. Completa:
   - Tipo: `Compra`
   - Cantidad: `10`
   - Precio: `150.00`
   - Comisión: `5.00`
   - Fecha: (hoy)
3. Clic en **"Registrar Transacción"**

¡Listo! Ya verás tu instrumento con todos los datos actualizados en el dashboard.

## Comandos Útiles

```bash
# Inicializar DB
python run.py init-db

# Resetear DB (¡borra todos los datos!)
python run.py reset-db

# Crear datos de prueba
python create_sample_data.py

# Ejecutar en modo debug
FLASK_ENV=development python run.py
```

## Problemas Comunes

### Error de Conexión a MySQL

```bash
# Verifica que MySQL esté corriendo
sudo systemctl status mysql  # Linux
brew services list           # Mac

# Verifica credenciales en .env
```

### Puerto 5000 en Uso

```bash
# Usa otro puerto
flask run --port 5001
```

### Símbolo no Encontrado

- Verifica el símbolo en Yahoo Finance
- Para cryptos: usa `BTC`, `ETH` (sin -USD)
- Verifica tu conexión a internet

## Símbolos para Probar

### Stocks (Acciones)

- `AAPL` - Apple
- `MSFT` - Microsoft
- `GOOGL` - Google
- `TSLA` - Tesla

### ETFs

- `SPY` - S&P 500
- `QQQ` - Nasdaq 100
- `VOO` - Vanguard S&P 500
- `IWM` - Russell 2000

### Criptomonedas (sin -USD)

- `BTC` - Bitcoin
- `ETH` - Ethereum
- `SOL` - Solana
- `ADA` - Cardano

## Próximos Pasos

1. Lee el **README.md** para funcionalidades completas
2. Consulta **INSTALLATION.md** para configuración avanzada
3. Revisa **ARCHITECTURE.md** para entender la estructura

## ¿Necesitas Ayuda?

- Revisa los logs en la consola
- Busca en **INSTALLATION.md** sección "Solución de Problemas"
- Los ejemplos de datos están en `create_sample_data.py`

## Script de Instalación Automática (Linux/Mac)

Si prefieres instalación automatizada:

```bash
chmod +x setup.sh
./setup.sh
```

---

**¡Disfruta Investment Tracker!** 📈💰
