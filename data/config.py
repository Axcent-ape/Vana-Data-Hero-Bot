# api id, hash
API_ID = 1488
API_HASH = 'abcde1488'


DELAYS = {
    "RELOGIN": [5, 7],  # delay after a login attempt
    'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
    'SEND_CLIKS': [25, 50],   # delay after play in a durov game
    'TASK': [5, 8],  # delay after completed the task
}

# count of click per SEND_CLIKS seconds. Max - 20000 clicks. 1 clicks = 0.1 points
CLICKS_PER_TIME = [10000, 20000]

BLACKLIST_TASKS = ['Play game', 'Refer a friend', 'Connect Telegram Wallet', 'Connect Wallet', 'Participate in rDataDAO']

PROXY = {
    "USE_PROXY_FROM_FILE": False,  # True - if use proxy from file, False - if use proxy from accounts.json
    "PROXY_PATH": "data/proxy.txt",  # path to file proxy
    "TYPE": {
        "TG": "socks5",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": "http"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
        }
}

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30
