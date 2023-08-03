# Main Packages
import discord
from discord.ext import commands
import responses

#Errors
from discord.ext.commands import CommandNotFound
from discord.ext.commands import MissingRequiredArgument

#Other Packages
import pytz
import random
import json

TOKEN = 'MTEzNjcyNzU3ODE0OTkxMjY3Nw.G_uikU.3FesIGyUYtuRysYESpXQyEBh2hhKXUgKglP8Wo'

GUILD_ID = 1136726273788493995
AUDIT_CHANNEL_ID = 1136729290709405887
CONFESSIONS_CHANNEL_ID = 1136729441528188987
WELCOME_CHANNEL_ID = 1136729265530998884

COMMAND_PREFIX = '!'

CONFESSIONS_ALLOWED = True

def start_bot():
    my_intents = discord.Intents.default()
    my_intents.message_content = True
    my_intents.dm_messages = True
    my_intents.members = True
    # client = discord.Client(intents=myIntents)
    global bot
    bot = commands.Bot(COMMAND_PREFIX, intents=my_intents, help_command=None)

    global serverDict 
    serverDict = dict()

    load_servers()
    serverDict[123] = Server(123)
    save_servers()

    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running!')
        await bot.change_presence( status=discord.Status.online, activity=discord.Game('games! 🍰') )

    @bot.event
    async def on_audit_log_entry_create(entry):
        channel = entry.guild.get_channel(AUDIT_CHANNEL_ID)
        time = entry.created_at.astimezone(tz=pytz.timezone('America/New_York')).isoformat()

        print('\nServer log created:')
        print(f" Server Nickname: {'No nickname' if (type(entry.user) is discord.user.User or type(entry.user) is None) else entry.user.nick} User: {entry.user.global_name} ID:{entry.user.name} | Action: {entry.action.name} | Date: {time.split('T')[0]} Time: {time.split('T')[1].split('.')[0]} EST\n")

        oldLog = f"\n Server Nickname: \"{'No nickname' if (type(entry.user) is discord.user.User or type(entry.user) is None) else entry.user.nick}\"\n User: \"{entry.user.global_name}\"\n ID: \"{entry.user.name}\" \n Action: {entry.action.name} \n Date: {time.split('T')[0]}\n  Time: {time.split('T')[1].split('.')[0]} EST"
        newLog = f"{entry.user.name}  {entry.action.name} \n{time.split('T')[0]} at {time.split('T')[1].split('.')[0]} EST"
        embededLog = discord.Embed(title="🫧", description=newLog, color=0x9dc8d1)

        # await channel.send(f":bookmark:\n> Server Nickname: \"{'No nickname' if (type(entry.user) is discord.user.User or type(entry.user) is None) else entry.user.nick}\"\n> User: \"{entry.user.global_name}\"\n> ID: \"{entry.user.name}\" \n> Action: {entry.action} \n> Date: {time.split('T')[0]}\n > Time: {time.split('T')[1].split('.')[0]} EST")
        await channel.send(embed=embededLog)

    @bot.command(name='repeat')
    async def repeat(context, *, arg):
        if not isinstance(context.channel, discord.DMChannel):
            await context.send(arg)
    
    @repeat.error
    async def repeat(context, error):
        if not isinstance(context.channel, discord.DMChannel):
            await context.channel.send(f'The command should go:\n{COMMAND_PREFIX}repeat I will repeat this!')


    @bot.command(name='confess')
    async def confess(context, *, arg):
        if isinstance(context.channel, discord.DMChannel):
            if CONFESSIONS_ALLOWED:
                if bot.get_guild(GUILD_ID).get_member(context.author.id) is None:
                    await context.author.send('You are not a member of our server! 😔')

                else:
                    confession = str(arg)
                    if '@everyone' in confession:
                        await context.author.send('Please don\'t mention everyone on confessions')
                    else:
                        embededConfession = discord.Embed(title="🫧  By Anonymous Member!", description=confession, color=0x9dc8d1)
                        await context.author.send('Your confession was posted on the Confessions channel! 🫧')
                        # await client.get_channel(CONFESSIONS_CHANNEL_ID).send("### 🫧  By Anonymous Member!\n>>> " + confession)
                        await bot.get_channel(CONFESSIONS_CHANNEL_ID).send(embed=embededConfession)
            else:
                await context.author.send('Sorry, confessions are temporarily disabled')
        else:
            await context.channel.send('Sorry, but you need to tell me that in a DM')
    
    @confess.error
    async def confess(context, error):
        print(COMMAND_PREFIX + 'confess: ' + str(error))
        if isinstance(context.channel, discord.DMChannel):
            if CONFESSIONS_ALLOWED:
                if bot.get_guild(GUILD_ID).get_member(context.author.id) is None:
                        await context.author.send('You are not a member of our server! 😔')
                else:
                    await context.author.send('The command is:\n' + COMMAND_PREFIX + 'confess I confess that I am a good cake!')
            else:
                await context.author.send('Sorry, confessions are temporarily disabled')
        else:
            await context.channel.send('Sorry, but you need to tell me that in a DM')


    @bot.command(name='standoff')
    async def standoff(context, *arg):
        if not isinstance(context.channel, discord.DMChannel):
            if len(arg) == 1:
                if context.author.nick is None:
                    player1 = context.author.global_name
                else:
                    player1 = context.author.nick

                player2 = str(arg[0])
                if player2.startswith('<@') and player2.endswith('>'):
                    player2 = str.removeprefix(player2, '<@')
                    player2 = str.removesuffix(player2, '>')
                else:
                    await context.channel.send(f'The usage of the command is:\n' + COMMAND_PREFIX +'standoff @user\n or (this following bit has not been implemented yet)\n' + COMMAND_PREFIX + 'standoff @user @user')
                    return

                if player2.startswith('&'):
                    player2 = str.removeprefix(player2, '&')

                player2 = int(player2)
                temp = bot.get_guild(GUILD_ID).get_member(player2)
                if temp.nick is None:
                    player2 = temp.global_name
                else:
                    player2 = temp.nick

                if random.randint(1, 10) <= 5:
                    await context.channel.send(f'# 💥👉      👈🤠\n> **{player1}** wins!')
                    
                else:
                    await context.channel.send(f'# 🤠👉      👈💥\n> **{player2}** wins!')
            else:
                await context.channel.send(f'The usage of the command is:\n' + COMMAND_PREFIX +'standoff @user\n')
        else:
            await context.author.send(f'Sorry, you can\'t use that command here. Please, do it in the server')


    @bot.command(name='help')
    async def help(context):
        if not isinstance(context.channel, discord.DMChannel):
            await context.send(f'>>> 🍰 Hi! My current commands are\n**{COMMAND_PREFIX}repeat** I will repeat anything you want to say!\n**{COMMAND_PREFIX}standoff** Want to do a cowboy stand off against a friend? 🤠\nand if you DM me...\n**{COMMAND_PREFIX}confess** Your confession will be sent to the #Confessions Channel!\nIf you need help with individual commands type the command!')


    @bot.command(name='shutdown')
    @commands.is_owner()
    async def shutdown(ctx):
        exit()


    @bot.event
    async def on_command_error(context, error):
        if isinstance(error, CommandNotFound):
            print("Command not found!")
        elif isinstance(error, MissingRequiredArgument):
            print("Missing argument!")
        else:
            raise error


    @bot.event
    async def on_member_join(member):
        print(member.global_name + ' joined the server')

        welcome_messages = [f"Hello __{member.global_name}__, welcome to our server! I hope you have a great time here! 🍰", f"Hi __{member.global_name}__, welcome! I hope you make lots of friends here! 🍰",
        f"Welcome __{member.global_name}__, do you also like cake!? 🍰", f"Please everyone welcome __{member.global_name}__! 🍰", f"Heyo __{member.global_name}__, welcome to our server! 🍰"]

        await bot.get_guild(GUILD_ID).get_channel(WELCOME_CHANNEL_ID).send( '### ' + welcome_messages[ random.randint(0, len(welcome_messages)-1) ] )

    @bot.event
    async def on_guild_join(guild):
        print(f'bot joined guild {guild.id}')

    @bot.event
    async def on_message(message):
        # Checks if a DM is a from a guild member
        if (bot.get_guild(GUILD_ID).get_member(message.author.id) is None):
            await message.channel.send('You are not a member of our server! 😔')
            return

        # Ignores Bot's messages
        if message.author == bot.user:
            return

        # Message log
        if not ( str(message.content).startswith(f'{COMMAND_PREFIX}confess') and isinstance(message.channel, discord.DMChannel) ):
            print(f"\n\"{message.author.global_name}\" / \"{message.author}\" said: \"{str(message.content)}\" in \"{message.channel}\" server: \"{message.guild}\"")

        # This actually processes the commands since we overrode on_message()
        await bot.process_commands(message)

        # Custom text messages
        if isinstance(message.channel, discord.DMChannel):
            response = responses.handle_dm(message.content)
            if response != '':
                await message.channel.send(response)
        else:
            await answer_message(message)
    
    # Run bot
    bot.run(TOKEN)


async def answer_message(original_message):
    try:
        response = responses.handle_response(str(original_message.content))
        if response != '':
            await original_message.channel.send(response)

    except Exception as e:
        print(e)




def get_guild(context):
    guild = bot.get_guild(context.guild.id)
    return guild


def is_member_on_guild(context):
    member = bot.get_guild(context.guild.id).get_member(context.author.id)
    if member is None:
        return False
    else:
        return True


def is_DM(context):
    if isinstance(context.channel, discord.DMChannel):
        return True
    else:
        return False


def load_servers():
    print('Loading server data...')

    with open('servers.json', 'r') as file:
        jsondict = json.loads(file.read())

        for key in jsondict:
            server = Server( (jsondict[str(key)])['id'] )
            server.load_data(jsondict[str(key)])
            serverDict[server.id] = server
        
        print('Servers:')
        for key in serverDict:
            print(f'\"{serverDict[key]}\"')

        file.close()

def save_servers():
    with open('servers.json', 'w') as file:
        dict_to_save = dict()
        for key in serverDict:
            dict_to_save[key] = serverDict[key].__dict__
        json_string = json.dumps(dict_to_save, indent = 4)
        file.write(json_string)

        file.close()



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
