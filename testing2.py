import requests
import json
from config import RAPIAPI_KEY

pstar_url = "https://papi-pornstarsapi.p.rapidapi.com/pornstars/"
pstar_headers = {
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "papi-pornstarsapi.p.rapidapi.com"
}

response = requests.get(pstar_url, headers=pstar_headers)

with open('test.json', 'w') as file:
    
    json_string = json.dumps(response.json(), indent = 4)
    file.write(json_string)

    file.close()