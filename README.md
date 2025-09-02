# 🚢 Age of Voyage - Django Naval Adventure Game ⚓

<div align="center">

![Age of Voyage](https://img.shields.io/badge/Age%20of%20Voyage-Naval%20Adventure-blue.svg?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-5.1.1-green.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg?style=for-the-badge)

**Un épico juego naval multijugador inspirado en la Edad de Oro de la Piratería**

🌊 **[Demo Live]** | 📚 **[Documentación]** | 🐛 **[Reportar Bug]** | 🚀 **[Solicitar Feature]**

</div>

---

## 🎮 Sobre Age of Voyage

Age of Voyage es un juego web multijugador ambientado en la Edad de Oro de la Piratería. Los jugadores asumen el rol de capitanes navales que exploran los siete mares, comercian con recursos exóticos, construyen imperios navales y participan en épicas batallas navales.

### ✨ Características Principales

- 🚢 **6 Tipos de Barcos Únicos**: Desde ágiles balandras hasta poderosos navíos de línea
- 🗺️ **120+ Regiones Explorables**: Caribe, Atlántico, Mediterráneo, Pacífico, Ártico y refugios piratas secretos
- 💰 **Sistema de Comercio Dinámico**: Precios fluctuantes, rutas comerciales y mercados especializados
- ⚔️ **Combate Naval Estratégico**: Batallas por turnos con eventos especiales
- 🏗️ **Construcción de Bases**: Astilleros, fortalezas y estructuras económicas
- 👥 **Gremios Multijugador**: Sistemas de alianzas y cooperación
- 🎯 **Sistema de Misiones**: Exploración, comercio, combate y rescates
- 📈 **Progresión de Personaje**: Niveles, habilidades y especializaciones
- 🏆 **Logros y Rankings**: Tablas de clasificación y sistema de reputación

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- Docker y Docker Compose (recomendado)
- PostgreSQL (opcional, incluido en Docker)

### 🐳 Instalación con Docker (Recomendada) - **TOTALMENTE AUTOMÁTICA**

```bash
# Clonar el repositorio
git clone https://github.com/cgaviria92/age-of-voyage-django.git
cd age-of-voyage-django

# ¡Un solo comando lo hace todo!
# En Windows:
start.bat

# En Linux/Mac:
chmod +x start.sh
./start.sh
```

**🎉 ¡Eso es todo! Las migraciones, datos iniciales y configuración se crean automáticamente.**

### 🐍 Instalación Manual - **TAMBIÉN AUTOMÁTICA**

```bash
# Clonar el repositorio
git clone https://github.com/cgaviria92/age-of-voyage-django.git
cd age-of-voyage-django

# Script de configuración automática
python setup.py

# O manualmente:
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py populate_game --no-input
python manage.py runserver
```

---

## 🏗️ Arquitectura del Proyecto

```
age-of-voyage-django/
├── 📁 config/                 # Configuración principal de Django
│   ├── settings.py            # Configuraciones del proyecto
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # Configuración WSGI
├── 📁 apps/                   # Aplicaciones del juego
│   ├── 👤 players/           # Sistema de jugadores y autenticación
│   ├── 🚢 ships/             # Gestión de barcos y flotas
│   ├── 🗺️ exploration/       # Sistema de exploración mundial
│   ├── 💰 trade/             # Sistema de comercio y economía
│   ├── ⚔️ combat/            # Sistema de combate naval
│   ├── 🏗️ buildings/         # Construcción de estructuras
│   ├── 👥 guilds/            # Sistema de gremios
│   ├── 🎯 missions/          # Sistema de misiones
│   └── 📬 notifications/     # Sistema de notificaciones
├── 📁 static/                # Archivos estáticos (CSS, JS, imágenes)
├── 📁 templates/             # Plantillas HTML
├── 🐳 docker-compose.yml     # Configuración de Docker
├── 📋 requirements.txt       # Dependencias de Python
└── 📖 README.md              # Este archivo
```

---

## 🎯 Mecánicas de Juego

### 🚢 Sistema Naval

| Tipo de Barco | Velocidad | Carga | Poder de Fuego | Defensa | Especialización |
|---------------|-----------|-------|----------------|---------|----------------|
| **Balandra** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | Exploración rápida |
| **Corsario** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Ataque sorpresa |
| **Fragata** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Combate versátil |
| **Galeón** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Máxima capacidad |
| **Bergantín** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Comercio equilibrado |
| **Navío de Línea** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Supremacía naval |

### 🗺️ Regiones del Mundo

- **🏝️ Caribe (30 regiones)**: Islas tropicales, puertos piratas, aguas cristalinas
- **🌊 Atlántico (25 regiones)**: Rutas comerciales europeas, islas atlánticas
- **🏛️ Mediterráneo (20 regiones)**: Puertos históricos, ciudades-estado comerciales
- **🌅 Pacífico (25 regiones)**: Territorios inexplorados, islas exóticas
- **❄️ Ártico (15 regiones)**: Rutas peligrosas, expediciones extremas
- **🏴‍☠️ Refugios Piratas (5 regiones)**: Bases secretas, tesoros legendarios

### 💰 Sistema Económico

- **Recursos Comerciales**: 29 tipos diferentes desde especias hasta contrabando
- **Precios Dinámicos**: Fluctuaciones basadas en oferta, demanda y eventos
- **Rutas Comerciales**: Conexiones entre regiones con diferentes niveles de riesgo
- **Mercados Especializados**: Cada región tiene especialidades y preferencias

### ⚔️ Combate Naval

- **Sistema por Turnos**: Estrategia táctica en batallas navales
- **Acciones de Combate**: Cañonazos, embestidas, abordajes, reparaciones
- **Eventos Especiales**: Tormentas, refuerzos, sabotajes durante el combate
- **PvP y PvE**: Combate contra jugadores y flotas piratas NPC

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.1.1**: Framework web principal
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y manejo de sesiones
- **Celery**: Tareas asíncronas

### Frontend
- **HTML5 + CSS3**: Estructura y estilos
- **JavaScript**: Interactividad del cliente
- **Bootstrap**: Framework CSS responsivo

### DevOps
- **Docker**: Containerización
- **Docker Compose**: Orquestación de servicios
- **Gunicorn**: Servidor WSGI para producción
- **WhiteNoise**: Servicio de archivos estáticos

---

## 🚀 Comandos Útiles

### 🐳 Con Docker (Totalmente Automático)
```bash
# Iniciar todo automáticamente
start.bat          # Windows
./start.sh          # Linux/Mac

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Limpiar todo y empezar de cero
docker-compose down --volumes
```

### 🐍 Desarrollo Local (También Automático)
```bash
# Configuración automática completa
python setup.py

# Comandos manuales si los necesitas
python manage.py makemigrations  # Crear migraciones
python manage.py migrate         # Aplicar migraciones
python manage.py populate_game   # Poblar datos iniciales
python manage.py runserver       # Servidor de desarrollo
python manage.py createsuperuser # Crear usuario admin adicional
```

### ⚡ Características de Configuración Automática

- ✅ **Migraciones Automáticas**: Se crean y aplican al iniciar
- ✅ **Datos Iniciales**: 120+ regiones, 6 barcos, 29 recursos poblados automáticamente
- ✅ **Usuario Admin**: Creado automáticamente (admin/admin123)
- ✅ **Healthchecks**: Los servicios esperan a que la BD esté lista
- ✅ **Detección Inteligente**: No duplica datos si ya existen
- ✅ **Archivos Estáticos**: Recopilados automáticamente
- ✅ **Zero Configuration**: Funciona inmediatamente después del primer comando

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor:

1. 🍴 Fork el proyecto
2. 🌿 Crea una branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push a la branch (`git push origin feature/AmazingFeature`)
5. 🔄 Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

<div align="center">

**⚓ ¡Zarpa hacia la aventura en Age of Voyage! ⚓**

*"El mar llama, y yo debo ir."* - Proverbio de Marinero

![Barcos](https://img.shields.io/badge/Barcos-6%20Tipos-blue.svg)
![Regiones](https://img.shields.io/badge/Regiones-120+-green.svg)
![Recursos](https://img.shields.io/badge/Recursos-29%20Tipos-orange.svg)
![Misiones](https://img.shields.io/badge/Misiones-Infinitas-red.svg)

</div>
