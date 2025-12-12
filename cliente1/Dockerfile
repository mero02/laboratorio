FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iputils-ping \
    rsyslog \
    iproute2 \
    snmpd \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiamos configuración del agente SNMP
COPY snmpd.conf /etc/snmp/snmpd.conf
COPY rsyslog-client.conf /etc/rsyslog.conf

CMD ["/usr/sbin/snmpd", "-f", "-Lo"]

# -f hace que snmpd corra en primer plano.
# -Lo envía logs a stdout para debug.
