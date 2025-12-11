FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    iputils-ping \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]
