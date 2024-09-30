from requests import get
from requests.auth import HTTPBasicAuth
from base64 import b64encode
from json import loads
from os import getenv
from .helpers import encrypt

def request_auth_jwt():
    ip = ip_sisplan()
    params_request = {
        "USUARIO": "API",
        "SENHA": b64encode(encrypt('u^buhOCRgfta', 45857).encode('utf-8')).decode('utf-8')
    }
    response_jwt = get(url=f"{ip}/Login?", auth=HTTPBasicAuth("SISPLAN", "REwrCPMWrBSWa2qkX"), params=params_request)
    response_jwt_json = loads(response_jwt.text)
    return response_jwt_json['accessToken']

def ip_sisplan() -> str:
    try:
        apis_env = getenv("APIS_SISPLAN")
        apis_sisplan = apis_env.split(', ')
        for api in apis_sisplan:
            res = get(f"{api}/ping")
            if res.status_code == 200:
                return api
        return apis_sisplan[0]
    except:
        return apis_sisplan[0]

    
