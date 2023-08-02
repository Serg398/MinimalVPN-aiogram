import asyncio
import json
import motor.motor_asyncio
import datetime
import uuid
from wireguard import createPeerWG, deletePeerWG, getFilePeerWG, check_server, updatePeerWG
import os
from dotenv import load_dotenv


load_dotenv()

SERVER_MONGO = os.environ.get("SERVER_MONGO")
SERVERS_WG = json.loads(os.environ['SERVERS_WG'])
print(SERVER_MONGO)

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


async def createNewPeer(telegramID):
    await asyncio.sleep(1)
    newIDS = str(uuid.uuid4())
    date = datetime.datetime.now()
    date_timestamp = int(round(date.timestamp()))
    server = await balanser()
    peerWG = await createPeerWG(ids=newIDS, server=server)
    if peerWG == True:
        peersAll = []
        async for document in peers.find({"telegramID": str(telegramID)}):
            peersAll.append(document)
        await peers.insert_one(
            {
                "ids": newIDS,
                "telegramID": str(telegramID),
                "name": f"{str(len(peersAll) + 1)}-{newIDS[:4]}",
                "enabled": False,
                "server": server,
                "disableDate": date_timestamp
            }
        )
        print(f"MONGO:: добавлен {newIDS}")
        return f"Добавлено устройство: Device-{str(len(peersAll) + 1)}"
    else:
        print(f"MONGO:: не добавлен {newIDS}")
        return "Ошибка при добавлении устройства"


async def getFilePeer(ids):
    await asyncio.sleep(1)
    peer = []
    async for document in peers.find({"ids": ids}):
        peer.append(document)
    file = await getFilePeerWG(server=peer[0]["server"], ids=ids)
    return file, peer[0]["name"]


async def getAllUserPeers(telegramID):
    peersAll = []
    async for document in peers.find({"telegramID": str(telegramID)}):
        peersAll.append(document)
    return peersAll


async def deletePeer(ids):
    await asyncio.sleep(1)
    try:
        findPeer = []
        async for document in peers.find({"ids": ids}):
            findPeer.append(document)
        r = await deletePeerWG(ids=findPeer[0]["ids"], server=findPeer[0]["server"])
        if r == True:
            await peers.delete_one({"ids": ids})
            print(f"MONGO:: удален {ids}")
            return f"Удалено устройство: {findPeer[0]['name']}"
        else:
            return f"Ошибка удаления: {findPeer[0]['name']}"
    except:
        print(f"MONGO:: не найден {ids}")


async def updatePeer(ids, status):
    await asyncio.sleep(1)
    date = datetime.datetime.now()
    date_new = date + datetime.timedelta(days=31)
    date_timestamp = int(round(date_new.timestamp()))
    findPeer = []
    async for document in peers.find({"ids": ids}):
        findPeer.append(document)

    peer = findPeer[0]
    if int(peer['disableDate']) >= int(round(date.timestamp())):
        await updatePeerWG(ids=ids, server=peer['server'], status=status)
        await peers.update_one({"ids": ids}, {"$set": {'enabled': True, "disableDate": int(peer['disableDate']) + 2678400}})
    if int(peer['disableDate']) <= int(round(date.timestamp())):
        await updatePeerWG(ids=ids, server=peer['server'], status=status)
        await peers.update_one({"ids": ids}, {"$set": {'enabled': True, "disableDate": date_timestamp}})

    return_list = []
    async for document in peers.find({"ids": ids}):
        return_list.append(document)
    return return_list[0]


async def ping_server(ids):
    findPeer = []
    async for document in peers.find({"ids": ids}):
        findPeer.append(document)
    peer = findPeer[0]
    return await check_server(peer['server'])



