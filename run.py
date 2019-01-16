import json
import os
import requests
import time
import traceback

# Internal API URL
if str(os.getenv('TRAEFIK_INTERNAL_APISSL', None)).lower() in ['true']:
    traefik_internal_api = "https://"
else:
    traefik_internal_api = "http://"
traefik_internal_api += str(os.getenv('TRAEFIK_INTERNAL_HOST', 'traefik-internal')) + ":"
traefik_internal_api += str(os.getenv('TRAEFIK_INTERNAL_APIPORT', '8080'))

# Internal Backend URL
if str(os.getenv('TRAEFIK_INTERNAL_BACKENDSSL', None)).lower() in ['true']:
    traefik_internal_backend = "https://"
else:
    traefik_internal_backend = "http://"
traefik_internal_backend += str(os.getenv('TRAEFIK_INTERNAL_HOST', 'traefik-internal')) + ":"
traefik_internal_backend += str(os.getenv('TRAEFIK_INTERNAL_BACKENDPORT', 80))

# External Traefik API
if str(os.getenv('TRAEFIK_EXTERNAL_APISSL', None)).lower() in ['true']:
    traefik_external_api = "https://"
else:
    traefik_external_api = "http://"
traefik_external_api += str(os.getenv('TRAEFIK_EXTERNAL_HOST', 'traefik-external')) + ":"
traefik_external_api += str(os.getenv('TRAEFIK_EXTERNAL_APIPORT', '8080'))

# Set External API hook
traefik_external_hook = str(os.getenv('TRAEFIK_EXTERNAL_HOOK', 'external'))

external_backends = {
    'internal': {
        'loadBalancer': {'method': 'drr'},
        'servers': {
            'server0': {
                'weight': 1,
                'url': traefik_internal_backend
            }
        }
    }
}

external_frontends = {}
error = None
payload = {'frontends': {}, 'backends': {}}
while True:
    try:
        traefik_internal = requests.get('{}/api/providers'.format(traefik_internal_api))
        if traefik_internal.status_code == 200:
            traefik_internal_json = traefik_internal.json()
            for backend in traefik_internal_json.keys():
                frontends = traefik_internal_json[backend]['frontends']
                for frontend in frontends:
                    if traefik_external_hook in frontends[frontend]['entryPoints']:
                        temp = {}
                        for key, value in frontends[frontend].items():
                            if key in ['entryPoints', 'passHostHeader', 'redirect', 'routes']:
                                temp[key] = value
                        external_frontends[frontend] = temp
                        external_frontends[frontend]['backend'] = 'internal'
                        external_frontends[frontend]['entryPoints'].remove(traefik_external_hook)
            payload = {
                'frontends': external_frontends,
                'backends': external_backends
            }
            external_push = requests.put('{}/api/providers/web'.format(traefik_external_api), json.dumps(payload))
            if external_push.status_code != 200:
                error = 1
            else:
                pass
        else:
            error = 2
    except Exception as e:
        error = "{}".format(e)
        traceback.print_exc()

    if error is not None:
        errors = {
            1: "Invalid external API: {}".format(traefik_external_api),
            2: 'Invalid internal API: {}'.format(traefik_internal_api),
        }
        if error in errors:
            error = errors[error]
        print("Error: {}".format(error))
        break
    else:
        time.sleep(int(os.getenv("TRAEFIK_EXTERNAL_REFRESH", 60)))
