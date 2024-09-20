import random
import os
from utils.vana import Vana
from asyncio import sleep
from random import uniform
from data import config
from utils.core import logger
import datetime
import pandas as pd
from utils.core.telegram import Accounts
import asyncio
from aiohttp.client_exceptions import ContentTypeError


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    vana = Vana(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await sleep(uniform(*config.DELAYS['ACCOUNT']))
    await vana.login()

    for task in await vana.get_tasks():
        if task['name'] in config.BLACKLIST_TASKS or task['completed']: continue

        if await vana.complete_task(task['id'], task['points']):
            logger.success(f"Thread {thread} | {account} | Completed task «{task['name']}» and got {task['points']} points!")
        else:
            logger.warning(f"Thread {thread} | {account} | Couldn't complete task «{task['name']}»")

        await asyncio.sleep(random.uniform(*config.DELAYS['TASK']))

    while True:
        try:
            clicks = random.randint(*config.CLICKS_PER_TIME)
            if await vana.send_clicks(clicks):
                logger.success(f"Thread {thread} | {account} | Send {clicks} clicks ({clicks/10} points)")
            else:
                logger.warning(f"Thread {thread} | {account} | Couldn't send {clicks} clicks")

            await asyncio.sleep(random.uniform(*config.DELAYS['SEND_CLIKS']))

        except Exception as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}. Make relogin...")
            await asyncio.sleep(15)
            await vana.login()

    await vana.logout()


async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(Vana(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    #         return [phone_number, name, str(balance), str(referrals), referral_link, proxy]
    columns = ['Phone number', 'Name', 'Balance', 'Leaderboard', 'Referrals', 'Referral link', 'Proxy (login:password@ip:port)']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df['Name'] = df['Name'].astype(str)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")
