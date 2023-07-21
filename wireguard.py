import requests
from dotenv import load_dotenv
import os


load_dotenv()

PORT_WG = os.environ.get("PORT_WG")
PASSWD_WG = os.environ.get("PASSWD_WG")


def createPeerWG(ids, server):
    try:
        session = requests.Session()
        session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG})
        cookies = session.cookies.get_dict()
        session.post(f'http://{server}:{PORT_WG}/api/wireguard/client', cookies=cookies, json={"name": f"{ids}"})
        session.close()
        print(f"WG::{server}:: добавлен {ids}")
        return True
    except:
        print(f"WG::{server}:: ошибка добавления {ids}")
        return False


def deletePeerWG(ids, server):
    try:
        session = requests.Session()
        session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG})
        cookies = session.cookies.get_dict()
        peersAllWG = session.get(f'http://{server}:{PORT_WG}/api/wireguard/client', cookies=cookies).json()
        for peer in peersAllWG:
            if peer['name'] == ids:
                session.delete(f'http://{server}:{PORT_WG}/api/wireguard/client/{peer["id"]}', cookies=cookies)
        print(f"WG::{server}:: удален {ids}")
        return True
    except:
        print(f"WG::{server}:: не могу удалить {ids}")
        return False


def updatePeerWG(ids, status, server):
    try:
        session = requests.Session()
        session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG})
        cookies = session.cookies.get_dict()
        peersAllWG = session.get(f'http://{server}:{PORT_WG}/api/wireguard/client', cookies=cookies).json()
        for peer in peersAllWG:
            if peer['name'] == ids:
                session.post(f'http://{server}:{PORT_WG}/api/wireguard/client/{peer["id"]}/{status}', cookies=cookies)
        if status == 'disable':
            print(f"WG::{server}:: отключен {ids}")
        else:
            print(f"WG::{server}:: включен {ids}")
        return True
    except:
        return False


def getFilePeerWG(ids, server):
    print(server)
    print(ids)
    session = requests.Session()
    session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG})
    cookies = session.cookies.get_dict()
    peersAllWG = session.get(f'http://{server}:{PORT_WG}/api/wireguard/client', cookies=cookies).json()
    for peerWG in peersAllWG:
        if peerWG['name'] == ids:

            file = session.get(f"http://{server}:{PORT_WG}/api/wireguard/client/{peerWG['id']}/configuration", cookies=cookies)

            return file.content


def check_server(server):
    try:
        session = requests.Session()
        session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG})
        return True
    except:
        return False

