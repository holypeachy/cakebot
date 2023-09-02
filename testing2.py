import requests
import json

url = "https://weatherapi-com.p.rapidapi.com/current.json"

querystring = {"q":"Kyoto"}

headers = {
	"X-RapidAPI-Key": "14e9fe8769msh499735591a0acb0p1752f2jsn57f9e03212c5",
	"X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

with open('test.json', 'w') as file:
    
    json_string = json.dumps(response.json(), indent = 4)
    file.write(json_string)

    file.close()