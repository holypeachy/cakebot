import requests
import json
from config import RAPIAPI_KEY

from datetime import datetime
import pytz
from threading import Timer

x=datetime.today()
y=x.replace(day=x.day, hour=23, minute=5, second=30, microsecond=0)
delta_t=y-x

secs=delta_t.seconds+1

def hello_world():
    print ("hello world")
    #...

# t = Timer(secs, hello_world)
# t.start()



url = "https://cheapshark-game-deals.p.rapidapi.com/deals"

querystring = {"storeID[0]":"1","metacritic":"0","onSale":"true","pageNumber":"0","upperPrice":"50","exact":"0","pageSize":"1","sortBy":"Deal Rating","steamworks":"0","output":"json","desc":"0","steamRating":"0","lowerPrice":"0"}

headers = {
	"X-RapidAPI-Key": "0bc70c4f9cmsh23abfc8eeed6e1cp10e1d3jsn20a185f53455",
	"X-RapidAPI-Host": "cheapshark-game-deals.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

with open('test.json', 'w') as file:
    
    json_string = json.dumps(response.json(), indent = 4)
    file.write(json_string)

    file.close()