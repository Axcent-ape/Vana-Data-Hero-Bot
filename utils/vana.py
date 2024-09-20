from pyrogram.raw.functions.messages import RequestAppWebView
import random
import string
import time
from pyrogram import Client
from utils.core import logger, RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import asyncio
from urllib.parse import unquote
from data import config
import aiohttp
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector
from faker import Faker


class Vana:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread

        self.user, self.sp = None, None
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector,
                                             timeout=aiohttp.ClientTimeout(120))

    async def stats(self):
        await self.login()

        player = await self.get_player()
        balance = str(round(player.get('points'), 2))
        referral_link = f"https://t.me/VanaDataHeroBot/VanaDataHero?startapp={player.get('id')}"

        tasks = (await (await self.session.get('https://www.vanadatahero.com/api/tasks')).json()).get('tasks')
        referrals = str(len(tasks[1].get('completed')))

        leaderboard = (await (await self.session.get('https://www.vanadatahero.com/api/leaderboard')).json()).get('currentPlayerPosition')

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

        return [phone_number, name, str(balance), str(leaderboard), str(referrals), referral_link, proxy]

    async def complete_task(self, id_: int, reward: [int, float]):
        json_data = {"status": "completed", "points": reward}
        resp = await self.session.post(f'https://www.vanadatahero.com/api/tasks/{id_}', json=json_data)

        return await resp.text() == ''

    async def get_tasks(self):
        r = await (await self.session.get('https://www.vanadatahero.com/api/tasks')).json()
        return r.get('tasks')

    async def get_player(self):
        r = await (await self.session.get('https://www.vanadatahero.com/api/player')).json()
        return r

    async def send_clicks(self, clicks: int):
        resp = await self.session.post('https://www.vanadatahero.com/api/tasks/1', json={"status": "completed", "points": clicks*0.1})
        return await resp.text() == ''

    async def register(self):
        r = await (await self.session.post('https://www.vanadatahero.com/api/player', json={})).json()
        return r

    async def need_register(self):
        r = await (await self.session.get('https://www.vanadatahero.com/api/player')).json()
        return r.get('status') == 404 and 'not found' in r.get('message')

    async def logout(self):
        await self.session.close()

    async def login(self):
        attempts = 3
        while attempts:
            try:
                self.sp = '1262949286'
                query = await self.get_tg_web_data()

                if query is None:
                    logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
                    await self.logout()
                    return None

                self.session.headers['X-Telegram-Web-App-Init-Data'] = query
                if await self.need_register():
                    info = await self.register()
                    if info.get('createdAt'):
                        await self.session.post('https://www.vanadatahero.com/api/tasks/2', json={"status": "completed", "data": {"referredUsername": info.get('tgUsername'), "referredPlayerId": info.get('id'), "referredBy": int(query.split('start_param=')[1].split('&auth_date=')[0])}})

                        logger.success(f"Thread {self.thread} | {self.account} | Registered!")

                logger.success(f"Thread {self.thread} | {self.account} | Login")
                return

            except Exception as e:
                logger.error(f"Thread {self.thread} | {self.account} | Left login attempts: {attempts}, error: {e}")
                await asyncio.sleep(random.uniform(*config.DELAYS['RELOGIN']))
                attempts -= 1
        else:
            logger.error(f"Thread {self.thread} | {self.account} | Couldn't login")
            await self.logout()
            return

    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            if not (await self.client.get_me()).username:
                while True:
                    username = Faker('en_US').name().replace(" ", "") + '_' + ''.join(random.choices(string.digits, k=random.randint(3, 6)))
                    if await self.client.set_username(username):
                        logger.success(f"Thread {self.thread} | {self.account} | Set username @{username}")
                        break
                await asyncio.sleep(5)

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('VanaDataHeroBot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('VanaDataHeroBot'), short_name="VanaDataHero"),
                platform='android',
                write_allowed=True,
                start_param=self.sp if False else "5190551798"
            ))
            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            return query
        except:
            return None

    @staticmethod
    def current_time():
        return int(time.time())
