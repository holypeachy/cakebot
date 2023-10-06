import requests
import json
from config import RAPIAPI_KEY

from datetime import datetime
import pytz
from threading import Timer

url = "https://cheapshark-game-deals.p.rapidapi.com/stores"

headers = {
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "cheapshark-game-deals.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

with open('test.json', 'w') as file:
    
    json_string = json.dumps(response.json(), indent = 4)
    file.write(json_string)

    file.close()