import json

import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_MONGO = os.environ.get("SERVER_MONGO")
SERVERS_WG = json.loads(os.environ['SERVERS_WG'])

client = motor.motor_asyncio.AsyncIOMotorClient(SERVER_MONGO, 27017, username='serg398', password='Kon031fit')
users = client['users']
peers = client['peers']["peers"]


async def balanser():
    print("Balanser start")
    balans = []
    for server in SERVERS_WG:
        try:
            total = await peers.count_documents({"server": server})
            balans.append({"host": server, "peers": total})
        except:
            print(f"WG::{server}:: не могу подключиться")
    max_dict = min(balans, key=lambda x: x['peers'])
    print(f"BALANCER::{max_dict['host']}:: в приоритете")
    return max_dict["host"]