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
  - API REST con endpoints básicos (`/`, `/ping`, `/compute`)
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
- Puertos 16686 y 4318 disponibles (Jaeger)

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
│   └── snmpd.conf
├── flask-app/
│   ├── Dockerfile
│   ├── app.py
│   ├── instrumentation.py
│   └── requirements.txt
└── monitor/
    ├── Dockerfile
    └── rsyslog-server.conf
```

### Modificación de Configuraciones

- **Flask App**: Edita `flask-app/app.py` y `flask-app/instrumentation.py`
- **Cliente**: Modifica `cliente1/rsyslog-client.conf` y `cliente1/snmpd.conf`
- **Monitor**: Actualiza `monitor/rsyslog-server.conf`
- **Jaeger**: Cambia la imagen en `docker-compose.yml` si es necesario

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

## Solución de Problemas

### Servicio flask-app no aparece en Jaeger
1. Verifica que la aplicación esté recibiendo requests
2. Revisa logs del contenedor flask-app
3. Confirma que Jaeger esté ejecutándose y accesible

### Logs no llegan al monitor
1. Verifica configuración rsyslog en cliente1
2. Confirma que el puerto UDP 514 esté abierto en monitor
3. Revisa logs de rsyslog en ambos contenedores

### Errores de construcción
1. Limpia imágenes Docker: `docker system prune`
2. Reconstruye sin cache: `docker-compose build --no-cache`

## Tecnologías Utilizadas

- **Contenedorización**: Docker, Docker Compose
- **Backend**: Python, Flask
- **Observabilidad**: OpenTelemetry, Jaeger
- **Logging**: rsyslog
- **Monitoreo**: SNMP
- **Sistema Base**: Ubuntu 22.04

## Licencia

Este proyecto está bajo la licencia MIT.