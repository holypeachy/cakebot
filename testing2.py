import requests
import json
from config import RAPIAPI_KEY

url = "https://porn-gallery.p.rapidapi.com/pornos/Natasha%20Nice"

headers = {
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "porn-gallery.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

with open('test.json', 'w') as file:
    
    json_string = json.dumps(response.json(), indent = 4)
    file.write(json_string)

    file.close()