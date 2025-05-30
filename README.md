# Servicio de Compilador

Servicio de compilación basado en FastAPI que proporciona una API REST para procesar y compilar código.

## Tecnologías Utilizadas

- Python 3.10
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.2
- Matplotlib 3.8.2
- Pandas 2.1.3

## Requisitos

- Docker
- Docker Compose

## Instalación y Ejecución

1. Clonar el repositorio:
```bash
git clone https://github.com/yksogeid/service-compilador.git
cd service-compilador
```

2. Iniciar el servicio con Docker Compose:
```bash
docker-compose up -d
```

El servicio estará disponible en `http://localhost:8069`

## Estructura del Proyecto

- `api_service.py`: Punto de entrada de la aplicación FastAPI
- `requirements.txt`: Dependencias del proyecto
- `Dockerfile`: Configuración para la construcción de la imagen Docker
- `docker-compose.yml`: Configuración para orquestar el servicio

## Configuración

El servicio se ejecuta en el puerto 8069 por defecto. Puedes modificar esta configuración en el archivo `docker-compose.yml`.

## Desarrollo

Para desarrollo local sin Docker:

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar el servidor de desarrollo:
```bash
python api_service.py
```