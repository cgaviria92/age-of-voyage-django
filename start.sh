#!/bin/bash

echo "🚢 Iniciando Age of Voyage con configuración automática..."

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

# Limpiar contenedores anteriores si existen
echo "🧹 Limpiando configuración anterior..."
docker-compose down --volumes --remove-orphans >/dev/null 2>&1

# Construir y levantar servicios
echo "🔨 Construyendo servicios..."
docker-compose build --no-cache

echo "🚀 Levantando servicios con configuración automática..."
echo "⚡ Las migraciones y datos iniciales se configurarán automáticamente..."
docker-compose up -d

echo "⏳ Esperando que los servicios estén listos..."
sleep 30

echo ""
echo "🎉 ¡Age of Voyage está listo con configuración automática!"
echo "🌐 Accede al juego en: http://localhost:8000"
echo "👑 Panel de administración: http://localhost:8000/admin"
echo "🔑 Usuario admin: admin, Contraseña: admin123"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs:           docker-compose logs -f"
echo "   Detener juego:      docker-compose down"
echo "   Reiniciar:          docker-compose restart"
echo "   Limpiar todo:       docker-compose down --volumes"
echo ""
echo "⚠️  Si hay problemas, verifica los logs con: docker-compose logs -f web"
