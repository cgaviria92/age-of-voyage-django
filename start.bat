@echo off
echo 🚢 Iniciando Age of Voyage con configuración automática...

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado. Por favor instala Docker primero.
    pause
    exit /b 1
)

REM Verificar si Docker Compose está instalado
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no está instalado. Por favor instala Docker Compose primero.
    pause
    exit /b 1
)

echo ✅ Docker encontrado

REM Limpiar contenedores anteriores si existen
echo 🧹 Limpiando configuración anterior...
docker-compose down --volumes --remove-orphans >nul 2>&1

REM Construir y levantar servicios
echo 🔨 Construyendo servicios...
docker-compose build --no-cache

echo 🚀 Levantando servicios con configuración automática...
echo ⚡ Las migraciones y datos iniciales se configurarán automáticamente...
docker-compose up -d

echo ⏳ Esperando que los servicios estén listos...
timeout /t 30 /nobreak >nul

echo.
echo 🎉 ¡Age of Voyage está listo con configuración automática!
echo 🌐 Accede al juego en: http://localhost:8000
echo 👑 Panel de administración: http://localhost:8000/admin
echo 🔑 Usuario admin: admin, Contraseña: admin123
echo.
echo 📋 Comandos útiles:
echo    Ver logs:           docker-compose logs -f
echo    Detener juego:      docker-compose down
echo    Reiniciar:          docker-compose restart
echo    Limpiar todo:       docker-compose down --volumes
echo.
echo ⚠️  Si hay problemas, verifica los logs con: docker-compose logs -f web
pause
