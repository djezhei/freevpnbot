import json
import requests
from uuid import uuid4

from models import ProxyServer
import settings


def authorization(login_url: str) -> str:
    """
    Return cookie_session if auth is successful, the corresponding exception otherwise.

    :param login_url: proxy server URL like 'http://host:port/login'
    """
    r = requests.post(
        login_url,
        data={
            'username': settings.API_LOGIN,
            'password': settings.API_PASS
        }
    )
    cookie_session = r.headers['Set-Cookie']
    return cookie_session


def get_user_vpn_url(utid: str, protocol:str, host: str, api_port: int, user_port: int, inbound_id: int, cookie: str) -> str:
    api_inbounds_url = f'{protocol}://{host}:{api_port}{settings.API_INBOUNDS}/{inbound_id}'
    headers = {'cookie': cookie}
    r = requests.get(
        api_inbounds_url,
        headers=headers
    ).json()['obj']
    stream = json.loads(r['streamSettings'])
    user_flow = json.loads(r['settings'])['clients'][0]['flow']
    user_vpn_url = (f'{r["protocol"]}://{utid}@{host}:{user_port}?type={stream["network"]}&security={stream["security"]}&fp='
                    f'{stream["realitySettings"]["settings"]["fingerprint"]}&pbk={stream["realitySettings"]["settings"]["publicKey"]}'
                    f'&sni={stream["realitySettings"]["serverNames"][0]}&flow={user_flow}&sid={stream["realitySettings"]["shortIds"][0]}'
                    f'&spx=%2F#{r["remark"]}@{utid}')
    return user_vpn_url


def add_vless_client(utid: str, server: ProxyServer, gb_limit: int = 0) -> str:
    """
    Add vless client to the proxy server.
    Return user vpn_url.
    """
    api_add_cli_url = f'{server.protocol}://{server.host}:{server.api_port}{settings.API_ADD_CLIENT_PATH}'
    headers = {'cookie': server.cookie}
    payload = {
        'id': server.inbound_id,
        'settings': '{"clients":[{"id":"' + utid + '","flow":"xtls-rprx-vision","email":"' + utid + '","limitI'
                    'p":0,"totalGB":"' + str(gb_limit) + '","expiryTime":0,"enable":true,"tgId":"","subID":"' + 
                    str(uuid4()) + '"}]}'
    }
    r = requests.post(api_add_cli_url, data=payload, headers=headers)
    # if not r.json()['success']:   # TODO если статус код != 200 (нет куков или сети)
        # print(r.json()['msg'])
    vpn_url = get_user_vpn_url(utid, server.protocol, server.host, server.api_port, server.client_port,
                               server.inbound_id, server.cookie)
    return vpn_url


def delete_client(utid: str, server: ProxyServer) -> None:
    headers = {'cookie': server.cookie}
    api_delete_cli_path = settings.API_DELETE_CLI.format(inbound_id=server.inbound_id, utid=utid)
    api_delete_cli_url = f'{server.protocol}://{server.host}:{server.api_port}{api_delete_cli_path}'
    r = requests.post(api_delete_cli_url, headers=headers)
    # if not r.json()['success']:
