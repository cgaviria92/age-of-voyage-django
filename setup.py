#!/usr/bin/env python
"""
Script de configuración automática para desarrollo local
Ejecuta migraciones y pobla datos automáticamente
"""
import os
import sys
import subprocess
import time

def run_command(command, description):
    """Ejecutar comando y mostrar progreso"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Error en {description}")
            print(f"   {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False

def main():
    print("🚢 Configurando Age of Voyage automáticamente...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        print("❌ Error: No se encontró manage.py. Ejecuta desde el directorio raíz del proyecto.")
        sys.exit(1)
    
    print("✅ Directorio del proyecto encontrado")
    
    # Verificar Python y dependencias
    if not run_command("python --version", "Verificando Python"):
        sys.exit(1)
    
    # Instalar dependencias si es necesario
    print("📦 Verificando dependencias...")
    run_command("pip install -r requirements.txt", "Instalando dependencias")
    
    # Crear migraciones automáticamente
    run_command("python manage.py makemigrations", "Creando migraciones")
    
    # Aplicar migraciones
    run_command("python manage.py migrate", "Aplicando migraciones")
    
    # Poblar datos iniciales
    run_command("python manage.py populate_game --no-input", "Poblando datos iniciales")
    
    # Recopilar archivos estáticos
    run_command("python manage.py collectstatic --no-input", "Recopilando archivos estáticos")
    
    print("\n🎉 ¡Age of Voyage configurado exitosamente!")
    print("🌐 Para iniciar el servidor ejecuta: python manage.py runserver")
    print("👑 Panel admin: http://localhost:8000/admin (admin/admin123)")
    print("\n🚀 ¿Quieres iniciar el servidor ahora? (y/N): ", end="")
    
    choice = input().lower()
    if choice == 'y':
        print("🚀 Iniciando servidor de desarrollo...")
        os.system("python manage.py runserver")

if __name__ == "__main__":
    main()
