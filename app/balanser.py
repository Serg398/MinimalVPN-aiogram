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


