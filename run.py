import os
import requests
import toml

traefik_host = os.getenv('TRAEFIK_HOST', "10.1.0.34")

traefik_api_port = os.getenv('TRAEFIK_API_PORT', '8080')
traefik_api_ssl = str(os.getenv('TRAEFIK_API_SSL', 'FALSE')).lower()

traefik_fwd_port = os.getenv('TRAEFIK_FWD_PORT', '443')
traefik_fwd_ssl = str(os.getenv('TRAEFIK_FWD_SSL', 'TRUE')).lower()

traefik_api_url = "https://" if traefik_api_ssl == 'true' else "http://"
traefik_api_url += traefik_host + ":" + traefik_api_port
traefik_api = requests.get(url=traefik_api_url + "/api/providers/").json()

traefik_fwd_url = "https://" if traefik_api_ssl == 'true' else "http://"
traefik_fwd_url += traefik_host + ":" + traefik_api_port
traefik_fwd = {'fwd-host': {'url': traefik_fwd_url, 'weight': 1}}

traefik_trigger = os.getenv('TRAEFIK_TRIGGER', 'external')

traefik_refresh = int(os.getenv('TRAEFIK_REFRESH', 30))

rules = {}
for provider in traefik_api:
    if len(traefik_api[provider]) != 0:
        for rule in traefik_api[provider]['frontends']:
            if traefik_trigger in traefik_api[provider]['frontends'][rule]['entryPoints']:
                _rule = dict()

                _rule['frontend'] = traefik_api[provider]['frontends'][rule]
                _rule['frontend']['entryPoints'].remove(traefik_trigger)

                _rule['backend'] = traefik_api[provider]['backends'][rule]
                _rule['backend']['servers'] = traefik_fwd

                _rule['frontend']['backend'] = str(rule).replace('.', '_')
                _rule['frontend']['routes'] = {str(rule).replace('.', '_'): _rule['frontend']['routes'][rule]}

                rules[str(rule).replace('.', '_')] = _rule

output = {'backends': {}, 'frontends': {}}
for rule in rules:
    output['backends'][rule] = rules[rule]['backend']
    output['frontends'][rule] = rules[rule]['frontend']

output = toml.dumps(output)

with open(os.path.normpath(os.getcwd() + "/config/rules.toml"), 'w') as f:
    f.write(output)
    f.close()

