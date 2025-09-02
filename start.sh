#!/bin/bash

echo "🚢 Iniciando Age of Voyage..."

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

echo "✅ Docker encontrado"

# Construir y levantar servicios
echo "🔨 Construyendo servicios..."
docker-compose build

echo "🚀 Levantando servicios..."
docker-compose up -d

echo "⏳ Esperando que la base de datos esté lista..."
sleep 10

echo "📊 Ejecutando migraciones..."
docker-compose exec web python manage.py migrate

echo "🎮 Poblando datos iniciales del juego..."
docker-compose exec web python manage.py populate_game

echo "🎉 ¡Age of Voyage está listo!"
echo "🌐 Accede al juego en: http://localhost:8000"
echo "👑 Panel de administración: http://localhost:8000/admin"
echo "🔑 Usuario admin: admin, Contraseña: admin123"
echo ""
echo "Para detener el juego: docker-compose down"
echo "Para ver logs: docker-compose logs -f"
