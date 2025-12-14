FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iputils-ping \
    rsyslog \
    iproute2 \
    snmpd \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiamos configuración del agente SNMP 
COPY snmpd.conf /etc/snmp/snmpd.conf

# Copiamos configuración de rsyslog
COPY rsyslog-client.conf /etc/rsyslog.d/01-forward.conf

# Copiamos el script de inicio
COPY start.sh /start.sh

RUN chmod +x /start.sh

CMD ["/start.sh"]
