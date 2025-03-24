import requests
import json

TOKEN = "7910119865:AAE0sDHkSMR35W2wdEeZgNprK1eprSM4hOg"
chat_id = "5459043780"
message = "hello from your telegram bot"
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
#print(requests.get(url).json()) # this sends the message
print(json.dumps(requests.get(url).json(), indent=4))
