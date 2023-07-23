import asyncio
import aiohttp
from dotenv import load_dotenv
import os


load_dotenv()

PORT_WG = os.environ.get("PORT_WG")
PASSWD_WG = os.environ.get("PASSWD_WG")


async def createPeerWG(ids, server):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG}) as resp:
                cookies = resp.cookies
            async with aiohttp.ClientSession(cookies=cookies) as session:
                await session.post(f'http://{server}:{PORT_WG}/api/wireguard/client', cookies=cookies, json={"name": f"{ids}"})
                print(f"WG::{server}:: добавлен {ids}")
                await session.close()
                return True
    except:
        print(f"WG::{server}:: ошибка добавления {ids}")
        return False


async def deletePeerWG(ids, server):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG}) as resp:
                cookies = resp.cookies
            async with aiohttp.ClientSession(cookies=cookies) as session:
                peersAllWG = await session.get(f'http://{server}:{PORT_WG}/api/wireguard/client')
                peersAllWG = await peersAllWG.json()
                for peer in peersAllWG:
                    if peer['name'] == ids:
                        await session.delete(f'http://{server}:{PORT_WG}/api/wireguard/client/{peer["id"]}')
                print(f"WG::{server}:: удален {ids}")
                await session.close()
                return True
    except:
        print(f"WG::{server}:: не могу удалить {ids}")
        return False


async def updatePeerWG(ids, status, server):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG}) as resp:
                cookies = resp.cookies
            async with aiohttp.ClientSession(cookies=cookies) as session:
                peersAllWG = await session.get(f'http://{server}:{PORT_WG}/api/wireguard/client')
                peersAllWG = await peersAllWG.json()
                for peer in peersAllWG:
                    if peer['name'] == ids:
                        await session.post(f'http://{server}:{PORT_WG}/api/wireguard/client/{peer["id"]}/{status}')
                if status == 'disable':
                    print(f"WG::{server}:: отключен {ids}")
                else:
                    print(f"WG::{server}:: включен {ids}")
                await session.close()
                return True
    except:
        return False


async def getFilePeerWG(ids, server):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG}) as resp:
            cookies = resp.cookies
        async with aiohttp.ClientSession(cookies=cookies) as session:
            peersAllWG = await session.get(f'http://{server}:{PORT_WG}/api/wireguard/client')
            peersAllWG = await peersAllWG.json()
            for peerWG in peersAllWG:
                if peerWG['name'] == ids:
                    file = await session.get(f"http://{server}:{PORT_WG}/api/wireguard/client/{peerWG['id']}/configuration")
                    await session.close()
                    return file.content


async def check_server(server):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG}) as resp:
                cookies = resp.cookies
            async with aiohttp.ClientSession(cookies=cookies) as session:
                await session.post(f'http://{server}:{PORT_WG}/api/session', json={"password": PASSWD_WG})
                await session.close()
                return True
    except:
        return False

