# Sistema de Monitoreo con Traza Distribuida

Este proyecto implementa un sistema de monitoreo básico utilizando Docker Compose, que incluye un microservicio Flask instrumentado con OpenTelemetry para trazas distribuidas, un cliente con servicios de logging y SNMP, un servidor de monitoreo centralizado, y Jaeger para la visualización de trazas.

Es un proyecto cohesivo que demuestra diferentes aspectos del monitoreo y la observabilidad en sistemas distribuidos. Los componentes están conectados a través de la red Docker, pero funcionalmente muestran dos enfoques complementarios:

**Enfoque Tradicional (Syslog + SNMP):**
- Cliente1 envía logs vía rsyslog UDP al monitor
- Monitor puede consultar métricas SNMP del cliente1
- Esto representa monitoreo de infraestructura clásico

**Enfoque Moderno (OpenTelemetry + Jaeger):**
- Flask-app genera trazas distribuidas con OpenTelemetry
- Las trazas se envían a Jaeger para análisis y visualización
- Esto representa observabilidad de aplicaciones modernas

No son dos proyectos separados, sino un sistema integrado que combina ambas aproximaciones. El syslog y SNMP manejan el monitoreo a nivel de sistema/infraestructura, mientras que OpenTelemetry/Jaeger se enfoca en el comportamiento de la aplicación. Ambos contribuyen a una visión completa del estado del sistema.

## Arquitectura

El sistema consta de los siguientes componentes:

- **flask-app**: Microservicio web desarrollado en Python con Flask, instrumentado con OpenTelemetry para generar trazas distribuidas.
- **cliente1**: Cliente que ejecuta servicios de logging (rsyslog) y monitoreo SNMP.
- **monitor**: Servidor central de monitoreo con herramientas para análisis de red y recepción de logs.
- **jaeger**: Sistema de trazas distribuidas para la recolección, almacenamiento y visualización de trazas.

Todos los servicios se ejecutan en una red Docker bridge dedicada llamada `monitoring-net`.

## Servicios Detallados

### Flask App
- **Tecnologías**: Python 3.10, Flask 3.0.0, OpenTelemetry
- **Funcionalidades**:
  - API REST con endpoints básicos (`/`, `/ping`, `/compute`, `/demo`)
  - Interfaz web con templates HTML para navegación y demo interactiva
  - Instrumentación automática de Flask con OpenTelemetry
  - Trazas manuales en operaciones específicas
  - Envío de trazas a Jaeger vía exportador Jaeger (UDP)
- **Puerto expuesto**: 5000

### Cliente1
- **Tecnologías**: Ubuntu 22.04, rsyslog, SNMP
- **Funcionalidades**:
  - Envío de logs al servidor monitor vía UDP (puerto 514)
  - Servicio SNMP para monitoreo
- **Configuración**:
  - rsyslog configurado para enviar todos los logs al monitor
  - SNMP con configuración personalizada

### Monitor
- **Tecnologías**: Ubuntu 22.04, rsyslog, SNMP, tcpdump, net-tools
- **Funcionalidades**:
  - Recepción de logs de clientes vía UDP
  - Herramientas de análisis de red (tcpdump, netstat)
  - Cliente SNMP para consultas
- **Configuración**:
  - rsyslog configurado para recibir logs UDP en puerto 514
  - Logs de cliente1 guardados en `/var/log/cliente1.log`

### Jaeger
- **Imagen**: jaegertracing/all-in-one:1.51
- **Funcionalidades**:
  - Recolección de trazas vía OTLP HTTP (puerto 4318) y agente Jaeger (puerto 6831 UDP)
  - UI web para visualización de trazas
- **Puerto UI**: 16686

## Requisitos Previos

- Docker
- Docker Compose
- Puerto 5000 disponible (Flask app)
- Puerto 16686 disponible (Jaeger)

## Instalación y Ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/mero02/laboratorio.git
   cd laboratorio
   ```

2. Construye y ejecuta los servicios:
   ```bash
   docker-compose up --build
   ```

   Para ejecutar en segundo plano:
   ```bash
   docker-compose up --build -d
   ```

3. Verifica que todos los servicios estén ejecutándose:
   ```bash
   docker-compose ps
   ```

## Uso

### Acceso a la Aplicación Flask
- URL: http://localhost:5000
- Endpoints disponibles:
  - `GET /`: Mensaje de bienvenida
  - `GET /ping`: Verificación de estado
  - `GET /compute`: Operación de ejemplo con delay
  - `GET /demo`: Demo interactiva del laboratorio

### Acceso a Jaeger UI
- URL: http://localhost:16686
- Selecciona el servicio "flask-app" en el dropdown para ver las trazas

### Monitoreo de Logs
- Conecta al contenedor monitor:
  ```bash
  docker-compose exec monitor bash
  ```
- Verifica logs recibidos:
  ```bash
  tail -f /var/log/cliente1.log
  ```

### Monitoreo SNMP
- Desde el contenedor monitor, consulta SNMP del cliente1:
  ```bash
  snmpwalk -v 2c -c public cliente1
  ```

## Configuración de Traza

La aplicación Flask está configurada con:

- **Proveedor de trazas**: OpenTelemetry SDK
- **Recurso**: Nombre del servicio "flask-app"
- **Exportador**: JaegerExporter (UDP al agente Jaeger)
- **Procesador**: BatchSpanProcessor para envío eficiente
- **Instrumentación**: Automática para Flask + manual en endpoints

## Desarrollo

### Estructura del Proyecto
```
.
├── docker-compose.yml
├── README.md
├── cliente1/
│   ├── Dockerfile
│   ├── rsyslog-client.conf
│   ├── snmpd.conf
│   └── start.sh
├── flask-app/
│   ├── Dockerfile
│   ├── app.py
│   ├── instrumentation.py
│   ├── requirements.txt
│   ├── static/
│   │   ├── script.js
│   │   ├── style.css
│   │   └── images/
│   └── templates/
│       ├── demo.html
│       └── index.html
└── monitor/
    ├── Dockerfile
    ├── rsyslog-server.conf
    └── start.sh
```

### Logs de Servicios

Para ver logs de un servicio específico:
```bash
docker-compose logs <nombre-del-servicio>
```

Ejemplos:
```bash
docker-compose logs flask-app
docker-compose logs jaeger
```

## Tecnologías Utilizadas

- **Contenedorización**: Docker, Docker Compose
- **Backend**: Python, Flask
- **Observabilidad**: OpenTelemetry, Jaeger
- **Logging**: rsyslog
- **Monitoreo**: SNMP
- **Sistema Base**: Ubuntu 22.04

## Contexto Académico

Este proyecto fue desarrollado como parte del curso **Administración y Seguridad de Redes**, con el objetivo de demostrar la implementación práctica de conceptos de monitoreo, logging, y observabilidad en entornos de red distribuidos.
