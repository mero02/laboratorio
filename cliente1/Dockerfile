FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iputils-ping \
    rsyslog \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiamos archivo de configuración del cliente
COPY rsyslog-client.conf /etc/rsyslog.d/01-client.conf

CMD ["rsyslogd", "-n"]
