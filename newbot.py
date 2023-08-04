# Main Packages
import discord
from discord import app_commands
from discord.ext import commands
import responses

# Config
from config import TOKEN
from config import COMMAND_PREFIX

# Errors
from discord.ext.commands import CommandNotFound
from discord.ext.commands import MissingRequiredArgument

# Other Packages
import pytz
import random
import json


GUILD_ID = 1136726273788493995
AUDIT_CHANNEL_ID = 1136729290709405887
CONFESSIONS_CHANNEL_ID = 1136729441528188987
WELCOME_CHANNEL_ID = 1136729265530998884


CONFESSIONS_ALLOWED = True

def start_bot():
    # Intents
    my_intents = discord.Intents.default()
    my_intents.message_content = True
    my_intents.dm_messages = True
    my_intents.members = True

    global bot
    bot = commands.Bot(COMMAND_PREFIX, intents=my_intents, help_command=None)

    global serverDict 
    serverDict = dict()

    load_servers()

    event_methods()

    dev_command_methods()

    command_methods()

    slash_commands()

    # Run bot
    bot.run(TOKEN)



def event_methods():

    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running!')
        try:
            synced = await bot.tree.sync()
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print(e)
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
        print(f'{bot.user} joined a new guild {guild.id}')
        serverDict[guild.id] = Server(guild.id)
        save_servers()


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


def dev_command_methods():

    @bot.command(name='dev_shutdown')
    @commands.is_owner()
    async def dev_shutdown(ctx):
        save_servers()
        exit()

    @bot.command(name='dev_saveservers')
    @commands.is_owner()
    async def dev_saveservers(ctx):
        save_servers()


def command_methods():
    # Set channels
    @bot.command(name='setwelcome')
    async def set_welcome(context):
        if is_admin(context):
            serverDict[context.guild.id].welcome_channel_id = context.channel.id
            print(serverDict[context.guild.id].welcome_channel_id)
            save_servers()
            await context.channel.send('This channel is now the \"Welcome\" channel!')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')
    
    @bot.command(name='setaudit')
    async def set_audit(context):
        if is_admin(context):
            serverDict[context.guild.id].audit_channel_id = context.channel.id
            print(serverDict[context.guild.id].audit_channel_id)
            save_servers()
            await context.channel.send('This channel is now the \"Audit Log\" channel!')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')
    
    @bot.command(name='setconfessions')
    async def set_confessions(context):
        if is_admin(context):
            serverDict[context.guild.id].confessions_channel_id = context.channel.id
            print(serverDict[context.guild.id].confessions_channel_id)
            save_servers()
            await context.channel.send('This channel is now the \"Confessions\" channel!')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')

    # Set Settings
    @bot.command(name='canconfess')
    async def can_confess(context, arg):
        if is_admin(context):
            if arg.lower() == 'true' or arg.lower() == 'false':
                get_server_info(context).confessions_allowed = bool(arg.lower())
                state = get_server_info(context).confessions_allowed
                await context.channel.send('Confessions are now allowed!' if (state == True) else 'Confessions are no longer allowed')
            else:
                await context.send('The command is:\n!canconfess true')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')

    @can_confess.error
    async def can_confess(context, error):
        if is_admin(context):
            await context.send('The command is:\n!canconfess true')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')


    @bot.command(name='repeat')
    async def repeat(context, *, arg):
        if not is_DM(context):
            await context.send(arg)
    
    @repeat.error
    async def repeat(context, error):
        if not is_DM(context):
            await context.channel.send(f'The command should go:\n{COMMAND_PREFIX}repeat I will repeat this!')


    @bot.command(name='confess')
    async def confess(context, *, arg):
        if isinstance(context.channel, discord.DMChannel):
            if get_server_info(context).confessions_allowed:
                if is_member_from_guild(context) is None:
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
                await context.author.send('Sorry, confessions are disabled')
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


def slash_commands():

    @bot.tree.command(name='confess')
    @app_commands.describe(confession = 'What would you like to confess?')
    async def confess(interaction: discord.Interaction, confession: str):
        await interaction.channel.send(confession)
        await interaction.response.defer()
        return await interaction.delete_original_response()


async def answer_message(original_message):
    try:
        response = responses.handle_response(str(original_message.content))
        if response != '':
            await original_message.channel.send(response)

    except Exception as e:
        print(e)


# On these methods context means either context from a command or message
def get_guild(context):
    return bot.get_guild(context.guild.id)


def is_member_from_guild(context):
    member = bot.get_guild(context.guild.id).get_member(context.author.id)
    if member is None:
        return False
    else:
        return True


def is_owner(context):
    if context.guild.owner_id == context.author.id:
        return True
    else:
        return False


def is_admin(context):
    if context.author.guild_permissions == discord.Permissions.all():
        return True
    else:
        return False


def is_DM(context):
    if isinstance(context.channel, discord.DMChannel):
        return True
    else:
        return False


def get_server_info(context):
    return serverDict[context.guild.id]


# Server information saving and loading
def save_servers():
    print('Saving server data...')
    with open('servers.json', 'w') as file:
        dict_to_save = dict()
        for key in serverDict:
            dict_to_save[key] = serverDict[key].__dict__
        json_string = json.dumps(dict_to_save, indent = 4)
        file.write(json_string)

        file.close()
    print('Servers were saved')


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
    
    print('Server data was loaded')


# Classes
class Server:
    def __init__(self, guild_id):
        self.id = guild_id

        # Default values
        self.welcome_channel_id = 0
        self.audit_channel_id = 0
        self.confessions_channel_id = 0
        self.confessions_allowed = False
    
    def __str__(self) -> str:
        return f'id: {self.id}  welcome_channel_id: {self.welcome_channel_id} audit_channel_id: {self.audit_channel_id} confessions_channel_id: {self.confessions_channel_id} confessions_allowed: {self.confessions_allowed}'

    def load_data(self, dictionary):
        self.id = dictionary['id']
        self.welcome_channel_id = dictionary['welcome_channel_id']
        self.audit_channel_id = dictionary['audit_channel_id']
        self.confessions_channel_id = dictionary['confessions_channel_id']
        self.confessions_allowed = dictionary['confessions_allowed']
