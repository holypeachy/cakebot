import json

class Server:
    def __init__(self, guild_id):
        self.id = guild_id

        # Default values
        self.command_prefix = '!'
        self.welcome_channel_id = 0
        self.audit_channel_id = 0
        self.confessions_channel_id = 0
    
    def __str__(self) -> str:
        return f'id: {self.id} command_prefix: {self.command_prefix} welcome_channel_id: {self.welcome_channel_id} audit_channel_id: {self.audit_channel_id} confessions_channel_id: {self.confessions_channel_id}'

    def load_data(self, dictionary):
        self.id = dictionary['id']
        self.command_prefix = dictionary['command_prefix']
        self.welcome_channel_id = dictionary['welcome_channel_id']
        self.audit_channel_id = dictionary['audit_channel_id']
        self.confessions_channel_id = dictionary['confessions_channel_id']


test = Server(1136726273788493995)
test2 = Server(789234612478)

testDict = dict()
testDict[test.id] = test.__dict__
testDict[test2.id] = test2.__dict__



with open('servers.json', 'w') as file:
    json_string = json.dumps(testDict, indent = 4)
    file.write(json_string)
    file.close()

with open('servers.json', 'r') as file:
    jsondict = json.loads(file.read())

    global serverList 
    serverList = list()
    for entry in jsondict:
        newServer = Server( (jsondict[str(entry)])['id'] )
        newServer.load_data(jsondict[str(entry)])
        serverList.append(newServer)
    
    for server in serverList:
        print(server)