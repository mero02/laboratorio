from flask import Flask, jsonify, request, render_template
import time
import docker
from pysnmp.hlapi import *

# Importa tracing
from instrumentation import setup_tracing
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Inicializa tracer
tracer = setup_tracing("flask-app")

app = Flask(__name__)

def get_monitor_logs():
    """Lee los logs del contenedor monitor via volumen compartido"""
    try:
        # Leer directamente desde el volumen compartido
        with open('/var/log/monitor/cliente1.log', 'r') as f:
            logs_content = f.read().strip()

        if logs_content:
            # Parsear y retornar últimas 20 líneas
            lines = [line.strip() for line in logs_content.split('\n') if line.strip()]
            return lines[-20:] if len(lines) > 20 else lines

    except FileNotFoundError:
        # Archivo no existe aún
        return [
            "Esperando logs de cliente1...",
            "El archivo de logs se creará cuando llegue el primer mensaje",
            f"Última verificación: {time.strftime('%H:%M:%S')}"
        ]
    except Exception as e:
        return [
            f"Error al leer logs: {str(e)}",
            f"Última actualización: {time.strftime('%H:%M:%S')}"
        ]

    # Fallback: retornar mensaje informativo
    return [
        "Esperando logs de cliente1...",
        "Usa la sección de simulación para generar mensajes de prueba",
        f"Última actualización: {time.strftime('%H:%M:%S')}"
    ]

def snmp_get(oid, timeout=2):
    """Realiza consulta SNMP GET al cliente1 con timeout optimizado"""
    try:
        # Usar snmpget command line tool que ya está disponible
        import subprocess
        result = subprocess.run([
            '/usr/bin/snmpget', '-v2c', '-c', 'public', '-t', str(timeout), 'cliente1', oid
        ], capture_output=True, text=True, timeout=timeout+1)

        if result.returncode == 0:
            # Parsear la salida: "SNMPv2-MIB::sysDescr.0 = STRING: Linux cliente1 5.15.0-119-generic #129-Ubuntu SMP Fri Aug 2 19:25:20 UTC 2024 x86_64"
            output = result.stdout.strip()
            if ' = ' in output:
                value_part = output.split(' = ', 1)[1]
                if 'STRING: ' in value_part:
                    return value_part.split('STRING: ', 1)[1]
                elif 'INTEGER: ' in value_part:
                    return value_part.split('INTEGER: ', 1)[1]
                elif 'Timeticks: ' in value_part:
                    return value_part.split('Timeticks: ', 1)[1]
                else:
                    return value_part
            return output
        else:
            return f"Error SNMP: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Timeout en consulta SNMP"
    except Exception as e:
        return f"Error: {str(e)}"

def get_system_metrics():
    """Obtiene métricas avanzadas del sistema via Docker SDK ejecutando SNMP en cliente1"""
    try:
        # Usar Docker SDK para ejecutar comandos SNMP directamente en cliente1
        docker_client = docker.from_env()
        container = docker_client.containers.get('cliente1')

        # CPU Load
        cpu_result = container.exec_run('snmpget -v2c -c public localhost 1.3.6.1.2.1.25.3.3.1.2.196608')
        cpu_load = cpu_result.output.decode('utf-8').strip()
        if 'INTEGER:' in cpu_load:
            cpu_percent = int(cpu_load.split('INTEGER:')[1].strip())
        else:
            cpu_percent = 15

        # Memory usage
        mem_total_result = container.exec_run('snmpget -v2c -c public localhost 1.3.6.1.2.1.25.2.3.1.5.1')
        mem_used_result = container.exec_run('snmpget -v2c -c public localhost 1.3.6.1.2.1.25.2.3.1.6.1')

        mem_total_str = mem_total_result.output.decode('utf-8').strip()
        mem_used_str = mem_used_result.output.decode('utf-8').strip()

        if 'INTEGER:' in mem_total_str and 'INTEGER:' in mem_used_str:
            mem_total = int(mem_total_str.split('INTEGER:')[1].strip())
            mem_used = int(mem_used_str.split('INTEGER:')[1].strip())
            mem_percent = min(100, int((mem_used / mem_total) * 100))
        else:
            mem_percent = 60

        # Disk usage (root filesystem)
        disk_total_result = container.exec_run('snmpget -v2c -c public localhost 1.3.6.1.2.1.25.2.3.1.5.2')
        disk_used_result = container.exec_run('snmpget -v2c -c public localhost 1.3.6.1.2.1.25.2.3.1.6.2')

        disk_total_str = disk_total_result.output.decode('utf-8').strip()
        disk_used_str = disk_used_result.output.decode('utf-8').strip()

        if 'INTEGER:' in disk_total_str and 'INTEGER:' in disk_used_str:
            disk_total = int(disk_total_str.split('INTEGER:')[1].strip())
            disk_used = int(disk_used_str.split('INTEGER:')[1].strip())
            disk_percent = min(100, int((disk_used / disk_total) * 100))
        else:
            disk_percent = 25

        # Network usage (simplified - just show some activity)
        net_percent = 10  # Simplified for demo

        return {
            'cpu': cpu_percent,
            'memory': mem_percent,
            'disk': disk_percent,
            'network': net_percent
        }

    except Exception as e:
        # Fallback a valores demo si Docker SDK falla
        return {
            'cpu': 15,
            'memory': 60,
            'disk': 25,
            'network': 10
        }

def get_snmp_data():
    """Obtiene datos SNMP básicos del cliente1"""
    data = {
        'sysName': snmp_get('1.3.6.1.2.1.1.5.0'),
        'sysUpTime': snmp_get('1.3.6.1.2.1.1.3.0'),
        'sysDescr': snmp_get('1.3.6.1.2.1.1.1.0'),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Agregar métricas del sistema
    data.update(get_system_metrics())

    # Si los valores básicos son errores, mostrar datos de ejemplo para demo
    if all('Error' in str(v) for v in [data['sysName'], data['sysUpTime'], data['sysDescr']]):
        data.update({
            'sysName': 'cliente1 (demo)',
            'sysUpTime': '123456789 timeticks (14 days, 6:56:07.89)',
            'sysDescr': 'Linux cliente1 5.15.0-119-generic #129-Ubuntu SMP Fri Aug 2 19:25:20 UTC 2024 x86_64',
        })

    return data

def simulate_log(message="Mensaje de prueba desde dashboard", priority="user.info"):
    """Simula un log agregándolo directamente al archivo compartido"""
    try:
        # Formatear el log como lo haría rsyslog
        timestamp = time.strftime('%b %d %H:%M:%S')
        hostname = 'cliente1'
        tag = 'dashboard'

        # Formato estándar de syslog: timestamp hostname tag[pid]: message
        log_entry = f'{timestamp} {hostname} {tag}: {message}\n'

        # Escribir directamente en el archivo compartido
        with open('/var/log/monitor/cliente1.log', 'a') as f:
            f.write(log_entry)

        return {
            'success': True,
            'message': f'Log simulado agregado: "{message}"',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Error al escribir log: {str(e)}',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

# Instrumenta Flask
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def index():
    with tracer.start_as_current_span("index-handler"):
        return render_template("index.html")

@app.route("/ping")
def ping():
    with tracer.start_as_current_span("ping-handler"):
        return jsonify({"status": "ok"}), 200

@app.route("/compute")
def compute():
    with tracer.start_as_current_span("compute-handler"):
        time.sleep(0.3)
        x = 5 * 5
        return jsonify({"operation": "5*5", "result": x}), 200

@app.route("/demo")
def demo():
    with tracer.start_as_current_span("demo-handler"):
        return render_template("demo.html")

@app.route("/classic-monitor")
def classic_monitor():
    with tracer.start_as_current_span("classic-monitor-handler"):
        # Carga inicial rápida - solo datos básicos
        logs = get_monitor_logs()
        # SNMP data se carga via AJAX para no bloquear la carga de página
        snmp_data = {
            'sysName': 'Cargando...',
            'sysUpTime': 'Cargando...',
            'sysDescr': 'Cargando...',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return render_template("classic-monitor.html", logs=logs, snmp_data=snmp_data)

@app.route("/api/snmp-data")
def api_snmp_data():
    with tracer.start_as_current_span("snmp-data-api-handler"):
        return jsonify(get_snmp_data())

@app.route("/api/simulate-log", methods=['POST'])
def api_simulate_log():
    with tracer.start_as_current_span("simulate-log-api-handler"):
        data = request.get_json() or {}
        message = data.get('message', 'Mensaje de prueba desde dashboard')
        priority = data.get('priority', 'user.info')
        result = simulate_log(message, priority)
        return jsonify(result)

@app.route("/api/logs")
def api_logs():
    with tracer.start_as_current_span("logs-api-handler"):
        logs = get_monitor_logs()
        return jsonify({
            'logs': logs,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
