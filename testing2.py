import requests
import json
from config import RAPIAPI_KEY

from datetime import datetime
import pytz
from threading import Timer

current_time=datetime.today()
future_time=current_time.replace(day=current_time.day, hour=23, minute=5, second=30, microsecond=0)
delta_t=future_time-current_time

secs=delta_t.seconds+1

def hello_world():
    print ("hello world")
    #...

timer = Timer(secs, hello_world)
timer.start()



url = "https://cheapshark-game-deals.p.rapidapi.com/deals"

querystring = {"storeID[0]":"1","metacritic":"0","onSale":"true","pageNumber":"0","upperPrice":"50","exact":"0","pageSize":"3","sortBy":"Deal Rating","steamworks":"0","output":"json","desc":"0","steamRating":"0","lowerPrice":"0"}

headers = {
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "cheapshark-game-deals.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

with open('test.json', 'w') as file:
    
    json_string = json.dumps(response.json(), indent = 4)
    file.write(json_string)

    file.close()