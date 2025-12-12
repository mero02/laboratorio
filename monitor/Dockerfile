FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iputils-ping \
    rsyslog \
  && apt-get clean && rm -rf /var/lib/apt/lists/*


# Copiamos archivo de configuración del servidor syslog
COPY rsyslog-server.conf /etc/rsyslog.d/01-server.conf

# rsyslog debe correr como servicio foreground
CMD ["rsyslogd", "-n"]
