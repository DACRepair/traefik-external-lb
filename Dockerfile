FROM python

ENV TRAEFIK_HOST "localhost"

ENV TRAEFIK_API_PORT 8080
ENV TRAEFIK_API_SSL "false"

ENV TRAEFIK_FWD_PORT 80
ENV TRAEFIK_FWD_SSL "false"

ENV TRAEFIK_TRIGGER "external"
ENV TRAEFIK_REFRESH 30

WORKDIR /opt/traefik

COPY requirements.txt /opt/traefik/
COPY run.py /opt/traefik/

RUN pip install -r requirements.txt