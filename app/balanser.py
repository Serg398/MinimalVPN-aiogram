import json

import aiohttp
from dotenv import load_dotenv
import os


load_dotenv()

SERVERS_WG = json.loads(os.environ['SERVERS_WG'])
PORT_WG = os.environ.get("PORT_WG")
PASSWD_WG = os.environ.get("PASSWD_WG")


async def balanser():
    balans = []
    for server in SERVERS_WG:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG}) as resp:
                    cookies = resp.cookies
                async with aiohttp.ClientSession(cookies=cookies) as session:
                    peersAllWG = await session.get(f'http://{server}:{PORT_WG}/api/wireguard/client')
                    peersAllWG = await peersAllWG.json()
                    balans.append({"host": server, "peers": len(peersAllWG)})
                    await session.close()
        except:
            print(f"WG::{server}:: не могу подключиться")
    max_dict = min(balans, key=lambda x: x['peers'])
    print(f"BALANCER::{max_dict['host']}:: в приоритете")
    return max_dict["host"]