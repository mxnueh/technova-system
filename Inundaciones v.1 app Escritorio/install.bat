@echo off
echo ========================================
echo Sistema de Monitoreo de Nivel de Agua
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.7 o superior desde https://python.org
    pause
    exit /b 1
)

echo Python encontrado. Instalando dependencias...
echo.

echo Instalando requests...
pip install requests

echo Instalando matplotlib...
pip install matplotlib

echo Instalando numpy...
pip install numpy

echo.
echo ========================================
echo Instalacion completada exitosamente!
echo ========================================
echo.
echo Para configurar el sistema, ejecuta:
echo python setup.py
echo.
echo Para ejecutar el programa principal:
echo python water_level_monitor.py
echo.
pause 