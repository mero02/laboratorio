FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iputils-ping \
    snmp \
    snmp-mibs-downloader \
    tcpdump \
    rsyslog \
    net-tools \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY rsyslog-server.conf /etc/rsyslog.d/01-server.conf
COPY start.sh /start.sh

RUN chmod +x /start.sh
RUN sed -i 's/^mibs :/# mibs :/' /etc/snmp/snmp.conf && \
    download-mibs

CMD ["/start.sh"]
