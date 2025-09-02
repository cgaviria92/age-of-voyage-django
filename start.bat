@echo off
echo 🚢 Iniciando Age of Voyage...

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

REM Construir y levantar servicios
echo 🔨 Construyendo servicios...
docker-compose build

echo 🚀 Levantando servicios...
docker-compose up -d

echo ⏳ Esperando que la base de datos esté lista...
timeout /t 10 /nobreak >nul

echo 📊 Ejecutando migraciones...
docker-compose exec web python manage.py migrate

echo 🎮 Poblando datos iniciales del juego...
docker-compose exec web python manage.py populate_game

echo.
echo 🎉 ¡Age of Voyage está listo!
echo 🌐 Accede al juego en: http://localhost:8000
echo 👑 Panel de administración: http://localhost:8000/admin
echo 🔑 Usuario admin: admin, Contraseña: admin123
echo.
echo Para detener el juego: docker-compose down
echo Para ver logs: docker-compose logs -f
pause
