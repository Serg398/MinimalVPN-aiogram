from pymongo import MongoClient
import datetime
import uuid
from wireguard import createPeerWG, deletePeerWG, getFilePeerWG, check_server, updatePeerWG
from balanser import balanser
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_MONGO = os.environ.get("SERVER_MONGO")


client = MongoClient("80.92.206.247", 27017, username='serg398', password='Kon031fit')
users = client['users']
peers = client['peers']["peers"]


def createNewPeer(telegramID):
    newIDS = str(uuid.uuid4())
    date = datetime.datetime.now()
    date_timestamp = int(round(date.timestamp()))
    server = balanser()
    peerWG = createPeerWG(ids=newIDS, server=server)
    if peerWG == True:
        peersAll = list(peers.find({"telegramID": str(telegramID)}))
        peers.insert_one(
            {
                "ids": newIDS,
                "telegramID": str(telegramID),
                "name": f"{str(len(peersAll) + 1)}-{newIDS[:4]}",
                "enabled": True,
                "server": server,
                "disableDate": date_timestamp
            }
        )
        print(f"MONGO:: добавлен {newIDS}")
        return f"Добавлено устройство: Device-{str(len(peersAll) + 1)}"
    else:
        print(f"MONGO:: не добавлен {newIDS}")
        return "Ошибка при добавлении устройства"


def getFilePeer(ids):
    peer = list(peers.find({"ids": ids}))
    print(ids)
    file = getFilePeerWG(server=peer[0]["server"], ids=ids)

    return file, peer[0]["name"]


def getAllUserPeers(telegramID):
    peersAll = list(peers.find({"telegramID": str(telegramID)}))
    return peersAll


def deletePeer(ids):
    try:
        findPeer = list(peers.find({"ids": ids}))[0]
        r = deletePeerWG(ids=findPeer["ids"], server=findPeer["server"])
        if r == True:
            peers.delete_one({"ids": ids})
            print(f"MONGO:: удален {ids}")
            return f"Удалено устройство: {findPeer['name']}"
        else:
            return f"Ошибка удаления: {findPeer['name']}"
    except:
        print(f"MONGO:: не найден {ids}")


def updatePeer(ids, status):
    date = datetime.datetime.now() + datetime.timedelta(days=31)
    date_timestamp = int(round(date.timestamp()))
    findPeer = list(peers.find({"ids": ids}))[0]
    updatePeerWG(ids=ids, server=findPeer['server'], status=status)
    peers.update_one({"ids": ids}, {"$set": {'enabled': True, "disableDate": date_timestamp}})
    return list(peers.find({"ids": ids}))[0]


def ping_server(ids):
    findPeer = list(peers.find({"ids": ids}))[0]
    return check_server(findPeer['server'])



