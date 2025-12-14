#!/bin/bash

# Arrancar rsyslog (cliente)
rsyslogd

# Arrancar snmpd en foreground
exec /usr/sbin/snmpd -f -Lo