import requests
import json

TOKEN = "7910119865:AAE0sDHkSMR35W2wdEeZgNprK1eprSM4hOg"
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
print(json.dumps(requests.get(url).json(), indent=4))
