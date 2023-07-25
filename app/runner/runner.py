import asyncio
import datetime
import json
import os
from dotenv import load_dotenv
import motor.motor_asyncio
import aiohttp
import timeit


load_dotenv()

SERVERS_WG = json.loads(os.environ['SERVERS_WG'])
PORT_WG = os.environ.get("PORT_WG")
PASSWD_WG = os.environ.get("PASSWD_WG")
SERVER_MONGO = os.environ.get("SERVER_MONGO")

client = motor.motor_asyncio.AsyncIOMotorClient(SERVER_MONGO, 27017, username='serg398', password='Kon031fit')
peers = client.get_database("peers")["peers"]


async def editWG(server, ids, status):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG}) as resp:
            cookies = resp.cookies

        if status == True:
            await session.post(f'http://{server}:{PORT_WG}/api/wireguard/client/{ids}/enable', auth=aiohttp.BasicAuth(PASSWD_WG), cookies=cookies)
            print(server, ids, status)
        if status == False:
            await session.post(f'http://{server}:{PORT_WG}/api/wireguard/client/{ids}/disable', auth=aiohttp.BasicAuth(PASSWD_WG), cookies=cookies)
            print(server, ids, status)
        if status == 'delete':
            await session.delete(f'http://{server}:{PORT_WG}/api/wireguard/client/{ids}', auth=aiohttp.BasicAuth(PASSWD_WG), cookies=cookies)
            print(server, ids, status)
        if status == 'create':
            await session.post(f'http://{server}:{PORT_WG}/api/wireguard/client', auth=aiohttp.BasicAuth(PASSWD_WG), json={"name": f"{ids}"}, cookies=cookies)
            print(server, ids, status)

    await session.close()


async def compare(server, dataDB):
    # arrayDB = []
    # arrayWG = []
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG}) as resp:
                cookies = resp.cookies
            resp = await session.get(f'http://{server}:{PORT_WG}/api/wireguard/client', cookies=cookies)
            dataWG = await resp.json()

            # for peerDB in dataDB:
            #     arrayDB.append(peerDB['ids'])
            # for peerWG in dataWG:
            #     arrayWG.append(peerWG["name"])
            #
            # for peerWG in dataWG:
            #     if peerWG['name'] not in arrayDB:
            #         await editWG(server=server, status='delete', ids=peerWG['id'])
            #
            # for peerDB in dataDB:
            #     if peerDB['ids'] not in arrayWG:
            #         await editWG(server=server, status='create', ids=peerDB['ids'])

            for peerDB in dataDB:
                for peerWG in dataWG:
                    if peerDB['ids'] == peerWG['name'] and peerWG['enabled'] != peerDB['enabled']:
                        await editWG(server=server, ids=peerWG['id'], status=peerDB['enabled'])

            await session.close()

        except:
            print(f"{server} --- Превышен таймаут")


async def start():
    while True:
        start = timeit.default_timer()
        date = datetime.datetime.now()

        async for device_obj in peers.find():
            print(int(device_obj['disableDate']), int(round(date.timestamp())))
            if device_obj['enabled'] == True and int(device_obj['disableDate']) <= int(round(date.timestamp())):
                print(device_obj['ids'] + ": disable")
                await peers.update_one({"ids": device_obj['ids']}, {"$set": {'enabled': False}})

        tasks = []
        for server in SERVERS_WG:
            dataBD = []
            async for device_obj in peers.find({"server": server}):
                dataBD.append(device_obj)
            task = asyncio.create_task(compare(server=server, dataDB=dataBD))
            tasks.append(task)

        await asyncio.gather(*tasks)
        end = timeit.default_timer()
        print(f"Time taken is {end - start}\n")
        await asyncio.sleep(30)


asyncio.run(start())

