import json
import requests
from dotenv import load_dotenv
import os


load_dotenv()

SERVERS_WG = json.loads(os.environ['SERVERS_WG'])
PORT_WG = os.environ.get("PORT_WG")
PASSWD_WG = os.environ.get("PASSWD_WG")


def balanser():
    balans = []
    for server in SERVERS_WG:
        try:
            session = requests.Session()
            session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG})
            cookies = session.cookies.get_dict()
            peersAllWG = session.get(f'http://{server}:{PORT_WG}/api/wireguard/client', cookies=cookies)
            balans.append({"host": server, "peers": len(peersAllWG.json())})
            session.close()
        except:
            print(f"WG::{server}:: не могу подключиться")
    max_dict = min(balans, key=lambda x: x['peers'])
    print(f"BALANCER::{max_dict['host']}:: в приоритете")
    return max_dict["host"]