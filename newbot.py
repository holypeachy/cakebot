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

VIBES_ID = 339550706342035456
SUFYAAN_ID = 851221324126093382

TAYIMO_ID = 403249158187778067

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
        # We register/sync the slash commands with discord
        try:
            synced = await bot.tree.sync()
            print(f'Synced {len(synced)} command(s)')
        except Exception as e:
            print(e)
        
        # We set the bot's status
        await bot.change_presence( status=discord.Status.online, activity=discord.Game('games! 🍰') )

        print(f'{bot.user} is now running!')


    @bot.event
    async def on_audit_log_entry_create(entry: discord.AuditLogEntry):
        time = entry.created_at.astimezone(tz=pytz.timezone('America/New_York')).isoformat()

        print('\nServer log:')
        print(f" Server Nickname: {'No nickname' if (type(entry.user) is discord.user.User or type(entry.user) is None) else entry.user.nick} User: {entry.user.global_name} ID:{entry.user.name} | Action: {entry.action.name} | Date: {time.split('T')[0]} Time: {time.split('T')[1].split('.')[0]} EST\n")

        channel = entry.guild.get_channel(serverDict[entry.guild.id].audit_channel_id)

        if type(channel) is None:
            print(f'Server \"{entry.guild.name}\" has not set up a AuditLog channel yet!')
        elif serverDict[entry.guild.id].audit_enabled == False:
            print(f'Audit log disabled for  \"{entry.guild.name}\" guild')
        else:
            log = f"{entry.user.name}  {entry.action.name} \n{time.split('T')[0]} at {time.split('T')[1].split('.')[0]} EST"
            embededLog = discord.Embed(title="🫧", description=log, color=0x9dc8d1)
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
    async def on_member_join(member: discord.Member):
        print(member.global_name + f' joined the server {member.guild.name}')


    @bot.event
    async def on_guild_join(guild: discord.Guild):
        print(f'{bot.user} joined a new guild \"{guild.name}\" id: {guild.id}')
        serverDict[guild.id] = Server(guild.id)
        save_servers()


    @bot.event
    async def on_message(message: discord.Message):
        # Ignores Bot's messages
        if message.author == bot.user:
            return

        # Checks if a DM is a from a guild member
        is_found = False
        if is_DM(message):
            for entry in serverDict:
                temp_guild = bot.get_guild(entry)
                temp_member = temp_guild.get_member(message.author.id)
                if not type(temp_member) is None:
                    is_found = True
                    break
            if not is_found:
                print(f'Member {temp_member.global_name} is not in any of the servers')
                await message.author.send('Sorry but you are not a member of the servers I know')
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
    @bot.command(name='set_welcome')
    async def set_welcome(context: commands.Context):
        if is_admin(context):
            serverDict[context.guild.id].welcome_channel_id = context.channel.id
            print(serverDict[context.guild.id].welcome_channel_id)
            save_servers()
            await context.channel.send('This channel is now the \"Welcome\" channel!')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')
    
    @bot.command(name='set_audit')
    async def set_audit(context: commands.Context):
        if is_admin(context):
            serverDict[context.guild.id].audit_channel_id = context.channel.id
            print(serverDict[context.guild.id].audit_channel_id)
            save_servers()
            await context.channel.send('This channel is now the \"Audit Log\" channel!')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')
    
    @bot.command(name='set_confessions')
    async def set_confessions(context: commands.Context):
        if is_admin(context):
            serverDict[context.guild.id].confessions_channel_id = context.channel.id
            print(serverDict[context.guild.id].confessions_channel_id)
            save_servers()
            await context.channel.send('This channel is now the \"Confessions\" channel!')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')

    # Set Settings
    @bot.command(name='enableconfessions')
    async def enable_confession(context: commands.Context, arg):
        if is_admin(context):
            if arg.lower() == 'true' or arg.lower() == 'false':
                serverDict[context.guild.id].confessions_allowed = True if arg == 'true' else False
                state = serverDict[context.guild.id].confessions_allowed
                await context.channel.send('Confessions are now allowed!' if (state == True) else 'Confessions are no longer allowed')
            else:
                await context.send(f'The command is:\n{COMMAND_PREFIX}canconfess true')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')

    @enable_confession.error
    async def enableconfession_error(context: commands.Context, error):
        if is_admin(context):
            await context.send(f'The command is:\n{COMMAND_PREFIX}enableconfessions true')
        else:
            await context.channel.send('Sorry only an admin can do that 😔')


    @bot.command(name='repeat')
    async def repeat(context: commands.Context, *, arg):
        if not is_DM(context):
            await context.send(arg)
    
    @repeat.error
    async def repeat_error(context: commands.Context, error):
        if not is_DM(context):
            await context.channel.send(f'The command should go:\n{COMMAND_PREFIX}repeat I will repeat this!')

    @bot.command(name='standoff')
    async def standoff(context: commands.Context, *arg):
        if not is_DM(context):
            if len(arg) == 1:
                if context.author.nick is None:
                    player1 = context.author.display_name
                else:
                    player1 = context.author.nick

                player2 = str(arg[0])
                if player2.startswith('<@') and player2.endswith('>'):
                    player2 = str.removeprefix(player2, '<@')
                    player2 = str.removesuffix(player2, '>')
                else:
                    await context.channel.send(f'The usage of the command is:\n' + COMMAND_PREFIX +'standoff @user')
                    return

                if player2.startswith('&'):
                    player2 = str.removeprefix(player2, '&')

                player2 = int(player2)
                player2id = player2
                temp = bot.get_guild(context.guild.id).get_member(player2)
                if temp.nick is None:
                    player2 = temp.display_name
                else:
                    player2 = temp.nick

                if context.author.id == TAYIMO_ID:
                    await context.channel.send(f'# 🤠   👉      👈💥\n> **{player2}** wins!')
                elif player2id == TAYIMO_ID:
                    await context.channel.send(f'# 💥👉      👈🤠\n> **{player1}** wins!')
                elif random.randint(1, 10) <= 5:
                    await context.channel.send(f'# 💥👉      👈🤠\n> **{player1}** wins!')
                else:
                    await context.channel.send(f'# 🤠👉      👈💥\n> **{player2}** wins!')
            else:
                await context.channel.send(f'The usage of the command is:\n' + COMMAND_PREFIX +'standoff @user\n')
        else:
            await context.author.send(f'Sorry, you can\'t use that command here. Please, do it in the server')


    @bot.command(name='help')
    async def help(context: commands.Context):
        if not isinstance(context.channel, discord.DMChannel):
            await context.send(f'>>> 🍰 Hi! My current commands are\n**{COMMAND_PREFIX}standoff** Want to do a cowboy stand off against a friend? 🤠\n**/confess** in the confessions channel to send an anonymous confessions\nIf you need help with individual commands type the command!')


def slash_commands():

    @bot.tree.command(name='confess')
    @app_commands.check(is_confessions_channel)
    @app_commands.describe(confession = 'What would you like to confess?')
    async def confess(interaction: discord.Interaction, confession: str):
        if '@everyone' in confession:
            await interaction.response.send_message('Please don\'t mention everyone on your confession', ephemeral=True)
        else:
            embededConfession = discord.Embed(title="🫧  By Anonymous Member!", description=confession, color=0x9dc8d1)
            await interaction.response.send_message('Your confession has been successfully posted and only you can see this message', ephemeral=True)
            await interaction.channel.send(embed=embededConfession)
    
    @confess.error
    async def confess_error(interaction : discord.Interaction, error):
        if isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message('You can only confess in a server with a confessions channel!', ephemeral=True)
        elif not serverDict[interaction.guild.id].confessions_allowed:
            await interaction.response.send_message('Sorry, confessions are not allowed on this server, tell an admin to enable it', ephemeral=True)
        elif not serverDict[interaction.guild.id].confessions_channel_id == interaction.channel.id:
            await interaction.response.send_message('Sorry, please do your confession on the confessions channel', ephemeral=True)
        else:
            print(f'/confess: {error}')
            await interaction.response.send_message('Uknown Error, please report')
    


async def answer_message(original_message):
    try:
        response = responses.handle_response(str(original_message.content))
        if response != '':
            await original_message.channel.send(response)

    except Exception as e:
        print(e)


# On these methods context means either context from a command or message
def get_guild(context: commands.Context):
    return bot.get_guild(context.guild.id)


def is_member_from_guild(context: commands.Context):
    member = bot.get_guild(context.guild.id).get_member(context.author.id)
    if member is None:
        return False
    else:
        return True


def is_owner(context: commands.Context):
    if context.author.id == context.guild.owner_id:
        return True
    else:
        return False


def is_admin(context: commands.Context):
    if context.author.guild_permissions.administrator == True:
        return True
    else:
        return False


def is_DM(context: commands.Context):
    if isinstance(context.channel, discord.DMChannel):
        return True
    else:
        return False

def is_DM(message: discord.Message):
    if isinstance(message.channel, discord.DMChannel):
        return True
    else:
        return False


def is_confessions_channel(interaction : discord.Interaction):
    if isinstance(interaction.channel, discord.DMChannel):
        return False
    elif serverDict[interaction.guild.id].confessions_allowed and serverDict[interaction.guild.id].confessions_channel_id == interaction.channel.id:
        return True
    else:
        return False


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
        self.audit_enabled = False
    
    def __str__(self) -> str:
        return f'id: {self.id}  welcome_channel_id: {self.welcome_channel_id} audit_channel_id: {self.audit_channel_id} confessions_channel_id: {self.confessions_channel_id} confessions_allowed: {self.confessions_allowed} audit_enabled; {self.audit_enabled}'

    def load_data(self, dictionary):
        self.id = dictionary['id']
        self.welcome_channel_id = dictionary['welcome_channel_id']
        self.audit_channel_id = dictionary['audit_channel_id']
        self.confessions_channel_id = dictionary['confessions_channel_id']
        self.confessions_allowed = dictionary['confessions_allowed']
        self.audit_enabled = dictionary['audit_enabled']


# TODO: Add confession checking to error so we know what the error was (aka confessions channel not set). Or show commmand only on confessions channel
# TODO: Fix confessions
