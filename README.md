# traefik-external-lb

ENV Vars:

| Variable                      | Type      | Default           | Description |
| ---                           | ---       | ---               | --- |
| TRAEFIK_INTERNAL_HOST         | string    | traefik-internal  | Host of the internal traefik instance. |
| TRAEFIK_INTERNAL_APIPORT      | integer   | 8080              | Port to the internal `/api` endpoints. |
| TRAEFIK_INTERNAL_APISSL       | boolean   | false             | Use SSL for internal API calls. |
| TRAEFIK_INTERNAL_BACKENDPORT  | integer   | 8080              | Port to the internal traefik instance used for traffic |
| TRAEFIK_INTERNAL_BACKENDSSL   | boolean   | false             | Use SSL for forwarded traffic. |
| TRAEFIK_EXTERNAL_HOST         | string    | traefik-external  | Host of the external traefik instance. |
| TRAEFIK_EXTERNAL_APIPORT      | integer   | 80                | Port to the external `/api` endpoints. |
| TRAEFIK_EXTERNAL_APISSL       | boolean   | false             | Use SSL for external API calls. |
| TRAEFIK_EXTERNAL_HOOK         | string    | external          | Endpoint used to trigger creation of a external rule. |
| TRAEFIK_EXTERNAL_REFRESH      | integer   | 30                | Time in seconds that the system refreshes |

Example:
```bash
docker -d --name traefik-external-lb \
  -e TRAEFIK_INTERNAL_HOST=traefik-internal \
  -e TRAEFIK_INTERNAL_APIPORT=8080 \
  -e TRAEFIK_INTERNAL_APISSL=false \
  -e TRAEFIK_INTERNAL_BACKENDPORT=80 \
  -e TRAEFIK_INTERNAL_BACKENDSSL=false \
  -e TRAEFIK_EXTERNAL_HOST=traefik-external \
  -e TRAEFIK_EXTERNAL_APIPORT=8080 \
  -e TRAEFIK_EXTERNAL_APISSL=false \
  -e TRAEFIK_EXTERNAL_HOOK=external \
  -e TRAEFIK_EXTERNAL_REFRESH=30 \
  dacrepair/traefik-external-lb
```

How it works:
```text
|-----------------------------|                         |------------------------------|                         |------------------|
|                    REST API | <----- Rest Calls ----- | REST API                     |                         | [Custom Routes ] |
| [External Traefik Instance] |                         | [Internal Traffic Instance ] | < -- HTTP(S) Traffic -- | [Microservices]  |
|             HTTP(S) Traffic | <-- HTTP(S) Traffic --> | HTTP(S) Traffic              |                         | [Other]          |
|-----------------------------|                         |------------------------------|                         |------------------|
```