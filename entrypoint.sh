#!/bin/bash

echo "🚢 Iniciando Age of Voyage con configuración automática..."

# Función para esperar a que la base de datos esté lista
wait_for_db() {
    echo "⏳ Esperando conexión a la base de datos..."
    while ! python -c "
import os, psycopg2
try:
    psycopg2.connect(
        host='db',
        port=5432,
        user=os.environ.get('POSTGRES_USER', 'ageofvoyage'), 
        password=os.environ.get('POSTGRES_PASSWORD', 'password123'),
        database=os.environ.get('POSTGRES_DB', 'ageofvoyage_db')
    ).close()
    print('Database ready')
except:
    exit(1)
" >/dev/null 2>&1; do
        echo "🔄 Base de datos no disponible, esperando..."
        sleep 2
    done
    echo "✅ Base de datos lista!"
}

# Función para ejecutar migraciones
run_migrations() {
    echo "📊 Creando migraciones automáticamente..."
    python manage.py makemigrations --no-input
    
    echo "📊 Aplicando migraciones..."
    python manage.py migrate --no-input
    
    echo "✅ Migraciones completadas!"
}

# Función para poblar datos iniciales
populate_data() {
    echo "🎮 Verificando y poblando datos iniciales..."
    python manage.py populate_game --no-input
    echo "✅ Datos iniciales verificados!"
}

# Función para recopilar archivos estáticos
collect_static() {
    echo "🎨 Recopilando archivos estáticos..."
    python manage.py collectstatic --no-input --clear
    echo "✅ Archivos estáticos listos!"
}

# Ejecutar todo el proceso de configuración
main() {
    wait_for_db
    run_migrations
    populate_data
    collect_static
    
    echo "🎉 ¡Age of Voyage configurado completamente!"
    echo "🚀 Iniciando servidor..."
    
    # Iniciar servidor
    exec python manage.py runserver 0.0.0.0:8000
}

# Ejecutar función principal
main
