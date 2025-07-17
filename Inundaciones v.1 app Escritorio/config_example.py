# Configuración de Ejemplo para el Sistema de Monitoreo de Nivel de Agua
# =====================================================================
# 
# Copia este archivo como 'config.py' y modifica los valores según tu configuración

# Configuración de ThingSpeak
# ---------------------------
CHANNEL_ID = 3000780                    # ID de tu canal en ThingSpeak
READ_API_KEY = "TU_READ_API_KEY"        # API key de lectura (obtener desde ThingSpeak)
WRITE_API_KEY = "TU_WRITE_API_KEY"      # API key de escritura (obtener desde ThingSpeak)

# Configuración del Hardware
# --------------------------
NIVEL_MAXIMO_CM = 4.0                   # Nivel máximo del tubo en centímetros
ALTURA_SENSOR_ULTRA = 45.0              # Altura del sensor ultrasónico al suelo
UMBRAL_ALERTA_CM = 10.0                 # Umbral para activar alertas

# Configuración del Sistema
# -------------------------
UPDATE_INTERVAL = 15                    # Intervalo de actualización en segundos
AUTO_START = False                      # Iniciar automáticamente con Windows
DETAILED_LOGS = True                    # Logs detallados del sistema
AUTO_EXPORT = False                     # Exportación automática de datos

# Configuración de WiFi (para referencia del ESP32)
# -------------------------------------------------
WIFI_SSID = "Karen"                     # Nombre de tu red WiFi
WIFI_PASSWORD = "Karen8318"             # Contraseña de tu red WiFi

# Configuración de Pines ESP32 (para referencia)
# ----------------------------------------------
SENSOR_ANALOGICO = 34                   # Pin del sensor resistivo
TRIG_PIN = 26                          # Pin TRIG del sensor ultrasónico
ECHO_PIN = 25                          # Pin ECHO del sensor ultrasónico
PIN_ALERTA = 27                        # Pin de la alarma (LED/Buzzer)

# Configuración de Alertas
# ------------------------
ALERTA_EMAIL = "tu-email@ejemplo.com"   # Email para notificaciones (opcional)
ALERTA_SONORA = True                    # Activar alertas sonoras
ALERTA_VISUAL = True                    # Activar alertas visuales

# Configuración de Exportación
# ----------------------------
EXPORT_FORMAT = "CSV"                   # Formato de exportación (CSV, JSON)
EXPORT_INTERVAL = 3600                  # Intervalo de exportación automática (segundos)
EXPORT_PATH = "./data/"                 # Carpeta para archivos exportados

# Configuración de Gráficos
# -------------------------
GRAFICO_TIEMPO_REAL = True             # Mostrar gráfico en tiempo real
GRAFICO_HISTORICO = True               # Mostrar gráfico histórico
GRAFICO_PUNTOS_MAX = 50                # Número máximo de puntos en gráfico
GRAFICO_ACTUALIZACION_MS = 1000        # Intervalo de actualización del gráfico (ms)

# Configuración de Base de Datos (opcional)
# -----------------------------------------
DB_ENABLED = False                     # Habilitar almacenamiento en base de datos
DB_TYPE = "SQLite"                     # Tipo de base de datos (SQLite, MySQL, PostgreSQL)
DB_PATH = "./data/water_level.db"      # Ruta de la base de datos

# Configuración de Seguridad
# --------------------------
ENCRYPT_DATA = False                   # Encriptar datos sensibles
LOG_SENSITIVE_DATA = False             # Registrar datos sensibles en logs
BACKUP_ENABLED = True                  # Habilitar respaldo automático
BACKUP_INTERVAL = 86400                # Intervalo de respaldo (segundos)

# Configuración de Red
# --------------------
TIMEOUT_REQUESTS = 10                  # Timeout para peticiones HTTP (segundos)
RETRY_ATTEMPTS = 3                     # Número de intentos de reconexión
RETRY_DELAY = 5                        # Delay entre intentos (segundos)

# Configuración de Logs
# ---------------------
LOG_LEVEL = "INFO"                     # Nivel de logging (DEBUG, INFO, WARNING, ERROR)
LOG_FILE = "./logs/system.log"         # Archivo de log
LOG_MAX_SIZE = 10485760                # Tamaño máximo del archivo de log (bytes)
LOG_BACKUP_COUNT = 5                   # Número de archivos de backup

# Configuración de Interfaz
# -------------------------
GUI_THEME = "clam"                     # Tema de la interfaz gráfica
GUI_LANGUAGE = "es"                    # Idioma de la interfaz
GUI_WINDOW_SIZE = "1200x800"           # Tamaño de la ventana principal
GUI_AUTO_HIDE = False                  # Ocultar automáticamente en bandeja del sistema

# Configuración de Notificaciones
# -------------------------------
NOTIFICACIONES_ACTIVAS = True          # Habilitar notificaciones del sistema
NOTIFICACIONES_SONIDO = True           # Sonido en notificaciones
NOTIFICACIONES_DURACION = 5000         # Duración de notificaciones (ms)

# Configuración de Rendimiento
# ----------------------------
CACHE_ENABLED = True                   # Habilitar caché de datos
CACHE_SIZE = 1000                      # Tamaño máximo del caché
CACHE_TTL = 300                        # Tiempo de vida del caché (segundos)
THREAD_POOL_SIZE = 4                   # Tamaño del pool de hilos

# Configuración de Calibración
# ----------------------------
CALIBRACION_AUTOMATICA = False         # Calibración automática de sensores
CALIBRACION_MANUAL = True              # Calibración manual de sensores
FACTOR_CORRECCION_TUBO = 1.0           # Factor de corrección para sensor del tubo
FACTOR_CORRECCION_CALLE = 1.0          # Factor de corrección para sensor de la calle

# Configuración de Mantenimiento
# ------------------------------
MANTENIMIENTO_AUTOMATICO = True        # Mantenimiento automático del sistema
LIMPIAR_LOGS_ANTIGUOS = True           # Limpiar logs antiguos automáticamente
LIMPIAR_DATOS_ANTIGUOS = True          # Limpiar datos antiguos automáticamente
DIAS_RETENCION_DATOS = 30              # Días de retención de datos

# Configuración de Desarrollo
# ---------------------------
DEBUG_MODE = False                     # Modo debug
TEST_MODE = False                      # Modo de pruebas
SIMULACION_DATOS = False               # Simular datos para pruebas
SIMULACION_INTERVAL = 5                # Intervalo de simulación (segundos)

# =====================================================================
# INSTRUCCIONES:
# =====================================================================
# 
# 1. Copia este archivo como 'config.py'
# 2. Modifica los valores según tu configuración
# 3. Asegúrate de que las API keys de ThingSpeak sean correctas
# 4. Ajusta los umbrales según tus necesidades
# 5. Configura la red WiFi si es necesario
# 
# ===================================================================== 