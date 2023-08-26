# Main Packages
import discord
from discord import app_commands
from discord.ext import commands

# Other scripts
import responses

# Settings from config.py
from config import TEST_TOKEN as TOKEN
from config import TEST_COMMAND_PREFIX as COMMAND_PREFIX

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

serverDict = dict()
welcomeDict = dict()
bot = None

def start_bot():
    # Intents
    my_intents = discord.Intents.default()
    my_intents.message_content = True
    my_intents.dm_messages = True
    my_intents.members = True

    global bot
    bot = commands.Bot(COMMAND_PREFIX, intents=my_intents, help_command=None)

    # Loads the stored server data from the json file
    load_servers()

    load_welcome_messages()


    # These methods are organizational and contain the events and commands that will be registered async
    event_methods()

    dev_command_methods()

    command_methods()

    slash_commands_methods()

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
        # We get the time of the entry in iso format
        time = entry.created_at.astimezone(tz=pytz.timezone('America/New_York')).isoformat()

        # Log for the terminal
        print('\nServer log:')
        print(f" Guild: \"{entry.guild.name}\" id: {entry.guild.id} Server Nickname: {'No nickname' if (type(entry.user) is discord.user.User or type(entry.user) is None) else entry.user.nick} User: {entry.user.global_name} ID:{entry.user.name} | Action: {entry.action.name} | Date: {time.split('T')[0]} Time: {time.split('T')[1].split('.')[0]} EST\n")

        # We check if we need to send the guild the log
        if serverDict[entry.guild.id].audit_enabled == True:
            channel = entry.guild.get_channel(serverDict[entry.guild.id].audit_channel_id)

            if channel is None:
                if serverDict[entry.guild.id].audit_channel_id == 0:
                    print(f'Server \"{entry.guild.name}\" has not set up a AuditLog channel yet!')
                else:
                    print(f'Server \"{entry.guild.name}\" has a registered AuditLog Channel that is not found in the server!')

        elif serverDict[entry.guild.id].audit_enabled == False:
            print(f'Audit log disabled for  \"{entry.guild.name}\" guild')
        else:
            log = f"{entry.user.name}  {entry.action.name} \n{time.split('T')[0]} at {time.split('T')[1].split('.')[0]} EST"
            embededLog = discord.Embed(title="🫧", description=log, color=0x9dc8d1)
            await channel.send(embed=embededLog)

 
    @bot.event
    async def on_command_error(context, error):
        if isinstance(error, CommandNotFound):
            print("Command Error: Command not found!")
        elif isinstance(error, MissingRequiredArgument):
            print("Command Error: Missing argument!")
        else:
            print(f'Command Error: \"{error}\"')
            # raise error


    @bot.event
    async def on_member_join(member: discord.Member):

        print(f'\"{member.global_name}\" (id: {member.id}) joined the server {member.guild.name}\n')

        if serverDict.__contains__(member.guild.id):
            serverInfo = serverDict[member.guild.id]
            if serverInfo.welcome_enabled:
                welcome_channel = bot.get_channel(serverInfo.welcome_channel_id)
                if welcome_channel is None:
                    print(f'Welcome channel for guild {member.guild.name} is enabled but the stored channel cannot be found')
                else:
                    num = random.randint(1, len(welcomeDict))
                    welcome_message = welcomeDict[str(num)]
                    welcome_message = welcome_message.replace('{user}', f'<@{member.id}>')
                    await welcome_channel.send('> ## ' + welcome_message)


    @bot.event
    async def on_guild_join(guild: discord.Guild):
        print(f'{bot.user} joined a new guild \"{guild.name}\" id: {guild.id}')
        serverDict[guild.id] = Server(guild.id)
        save_servers()

    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        print(f'{bot.user} has left guild \"{guild.name}\" id: {guild.id}')
        if serverDict.__contains__(guild.id):
            del serverDict[guild.id]
            save_servers()


    @bot.event
    async def on_message(message: discord.Message):
        # Ignores Bot's own messages
        if message.author == bot.user:
            return

        # Checks if a DM is a from a guild member
        is_found = False
        if is_DM(message.channel):
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
    async def dev_shutdown(context : commands.Context):
        save_servers()
        await context.channel.send('⚠️ Servers have been saved and the bot server will be shutdown!')
        await bot.close()

    @dev_shutdown.error
    async def dev_shutdown_error(context: commands.Context, error):
        if not await bot.is_owner(context.author):
            await context.channel.send(f'{context.author.name} is not the owner and cannot execute dev_shutdown')

    @bot.command(name='dev_saveservers')
    @commands.is_owner()
    async def dev_saveservers(context: commands.Context):
        save_servers()
        await context.channel.send('⚠️ Server data has been saved!')

    @dev_saveservers.error
    async def dev_saveservers_error(context: commands.Context, error):
        if not await bot.is_owner(context.author):
            print(f'{context.author.name} is not the owner and cannot execute dev_saveservers')


def command_methods():
    # Set channels
    @bot.command(name='set_audit')
    async def set_audit(context: commands.Context):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                serverDict[context.guild.id].audit_channel_id = context.channel.id
                print(f'Guild: \"{context.guild.name}\" Audit Log channel is now: {serverDict[context.guild.id].audit_channel_id}')
                save_servers()
                await context.channel.send('This channel is now the \"Audit Log\" channel!')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')
    

    # ! set_welcome is depricated for now
    @bot.command(name='set_welcome')
    async def set_welcome(context: commands.Context):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                serverDict[context.guild.id].welcome_channel_id = context.channel.id
                print(f'Guild: \"{context.guild.name}\" Welcome channel is now: {serverDict[context.guild.id].welcome_channel_id}')
                save_servers()
                await context.channel.send('This channel is now the \"Welcome\" channel!')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')


    @bot.command(name='set_confessions')
    async def set_confessions(context: commands.Context):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                serverDict[context.guild.id].confessions_channel_id = context.channel.id
                print(f'Guild: \"{context.guild.name}\" Confessions channel is now: {serverDict[context.guild.id].confessions_channel_id}')
                save_servers()
                await context.channel.send('This channel is now the \"Confessions\" channel!')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')


    # Enable Settings
    @bot.command(name='enable_audit')
    async def enable_audit(context: commands.Context, arg):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                if serverDict[context.guild.id].audit_channel_id == 0:
                    await context.send(f'Please set an Audit Log channel before enabling it! Use the following command to do so:\n**{COMMAND_PREFIX}set_audit**')
                elif arg.lower() == 'true' or arg.lower() == 'false':
                    serverDict[context.guild.id].audit_enabled = True if arg == 'true' else False
                    state = serverDict[context.guild.id].audit_enabled
                    save_servers()
                    await context.channel.send('Audit Logs are now enabled!' if (state == True) else 'Audit Logs are now disabled')
                else:
                    await context.send(f'The command is:\n{COMMAND_PREFIX}enable_audit true')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')
    
    @enable_audit.error
    async def enable_audit_error(context: commands.Context, error):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                await context.send(f'The command is:\n{COMMAND_PREFIX}enable_audit true')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')


    @bot.command(name='enable_welcome')
    async def enable_welcome(context: commands.Context, arg):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                if serverDict[context.guild.id].welcome_channel_id == 0:
                    await context.send(f'Please set a Welcome channel before enabling it! Use the following command to do so:\n**{COMMAND_PREFIX}set_welcome**')
                elif arg.lower() == 'true' or arg.lower() == 'false':
                    serverDict[context.guild.id].welcome_enabled = True if arg == 'true' else False
                    state = serverDict[context.guild.id].welcome_enabled
                    save_servers()
                    await context.channel.send('Welcome messages are now enabled!' if (state == True) else 'Welcome messages are now disabled')
                else:
                    await context.send(f'The command is:\n{COMMAND_PREFIX}enable_welcome true')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')
    
    @enable_welcome.error
    async def enable_welcome_error(context: commands.Context, error):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                await context.send(f'The command is:\n{COMMAND_PREFIX}enable_welcome true')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')


    @bot.command(name='enable_confessions')
    async def enable_confessions(context: commands.Context, arg):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                if serverDict[context.guild.id].confessions_channel_id == 0:
                    await context.send(f'Please set a Confessions channel first! Use the following command to do so:\n**{COMMAND_PREFIX}set_confessions**')
                else:
                    if arg.lower() == 'true' or arg.lower() == 'false':
                        serverDict[context.guild.id].confessions_allowed = True if arg == 'true' else False
                        state = serverDict[context.guild.id].confessions_allowed
                        save_servers()
                        await context.channel.send('Confessions are now allowed!' if (state == True) else 'Confessions are no longer allowed')
                    else:
                        await context.send(f'The command is:\n{COMMAND_PREFIX}enable_confessions true')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')

    @enable_confessions.error
    async def enableconfessions_error(context: commands.Context, error):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                await context.send(f'The command is:\n{COMMAND_PREFIX}enable_confessions true')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')


    @bot.command(name='repeat')
    async def repeat(context: commands.Context, *, arg):
        if not is_DM(context.channel):
            await context.send(arg)
    
    @repeat.error
    async def repeat_error(context: commands.Context, error):
        if not is_DM(context.channel):
            await context.channel.send(f'The command should go:\n{COMMAND_PREFIX}repeat I will repeat this!')

    @bot.command(name='standoff')
    async def standoff(context: commands.Context, *arg):
        if not is_DM(context.channel):
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
        if not is_DM(context.channel):
            await context.send(f'>>> 🍰 Hi! My current commands are:\n**{COMMAND_PREFIX}repeat** I will repeat anything you say\n**{COMMAND_PREFIX}standoff** Want to do a cowboy stand off against a friend? 🤠\n**/confess** in the confessions channel to send an anonymous confessions\n\n**For Testers**\n**{COMMAND_PREFIX}embed** Allows you to create an embeded message\n**/poll** Allows you to create polls\n\n**For admins**\n**{COMMAND_PREFIX}purge** Will delete x number of messages from the current channel\n**{COMMAND_PREFIX}set_welcome** Sets the Welcome channel\n**{COMMAND_PREFIX}set_audit** Sets the AuditLog channel \n**{COMMAND_PREFIX}set_confessions** Sets the Confessions channel\n**{COMMAND_PREFIX}enable_confessions** Enable of disable confessions for this server\n**{COMMAND_PREFIX}enable_audit** Enable of disable Audit Logs in this server\n\nIf you need help with individual commands type the command!')

        
    # Usage: !purge [limit]
    @bot.command(name='purgee')
    async def purge_channel(context: commands.Context, *args):
        if not is_DM(context.channel):
            test_channel_ids: dict = {'general': 1098216731111067731, 'welcome_test' : 1136729265530998884, 'log_audit' : 1136729290709405887}  # Test channel IDs for krayon
            live_channel_ids: dict = {'Bot-Testing': 1136013944029462538}  # Live channel IDs where purging is allowed:
            permitted_channels: list = [channel for channel in test_channel_ids.values()]
            channel: discord.TextChannel = context.channel
            if channel.id in permitted_channels:  # Channel check
                limit = int(args[0]) if args else 200  # If user specifies limit, else default to 200
                print(f'Purge command called in channel "{channel.name}" for {limit} messages.')
                author: discord.Member = context.author
                if is_permitted_to_purge(context.author):  # User check
                    await channel.purge(limit=limit+1)
            else:
                print(f'Channel "{channel.name}" is not eligible for purging.')
        else:
            await context.author.send('Sorry, you can only purge on a server')


    @bot.command(name='purge')
    async def purge(context: commands.Context, arg):
        if not is_DM(context.channel):
            if is_permitted_to_purge(context.author):
                limit = int(arg)
                await send_purge_audit(context.author, context.guild.id, limit, context.channel)
                await context.channel.purge(limit=limit+1)
            else:
                await context.channel.send('Sorry, only an admin can purge')
    
    @purge.error
    async def purge_error(context: commands.Context, error):
        if not is_DM(context.channel):
            if is_permitted_to_purge(context.author):
                await context.channel.send(f'The usage of the command is:\n{COMMAND_PREFIX}purge 5')
            else:
                await context.channel.send('Sorry, only an admin can purge')


    @bot.command(name='embed')
    async def embed(context: commands.Context, title: str, message: str):
        if not is_DM(context.channel):
            if context.author.guild_permissions.manage_channels:
                embededMessage = discord.Embed(title=f"🫧  {title}", description=message, color=0x9dc8d1)
                embededMessage.set_author(name=f'{context.author.global_name}', icon_url=context.author.avatar.url)
                await context.channel.send(embed=embededMessage)
            else:
                await context.channel.send(f'Sorry, only an admin can do that')

    @embed.error
    async def embed_error(context: commands.Context, error):
        if not is_DM(context.channel):
            if not context.author.guild_permissions.manage_channels:
                await context.channel.send(f'Sorry, only an admin can do that')
            else:
                await context.channel.send(f'The command is:\n{COMMAND_PREFIX}embed "My Embed Title" "I would like to say cake is great!  🍰"')


def slash_commands_methods():

    @bot.tree.command(name='confess', description='Tell a secret while remaining anonymous')
    @app_commands.guild_only()
    @app_commands.check(can_confess)
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
        if serverDict[interaction.guild.id].confessions_channel_id == 0:
            await interaction.response.send_message('Confessions channel is not set for this server, please tell an admin to set a confessions channel!', ephemeral=True)
        elif not serverDict[interaction.guild.id].confessions_allowed:
            await interaction.response.send_message('Sorry, confessions are not allowed on this server, tell an admin to enable them.', ephemeral=True)
        elif bot.get_channel(serverDict[interaction.guild.id].confessions_channel_id) is None:
            await interaction.response.send_message('A Confessions channel is set but it is not found in this server (could\'ve been deleted). Please tell an admin about this problem.', ephemeral=True)
        elif not serverDict[interaction.guild.id].confessions_channel_id == interaction.channel.id:
            await interaction.response.send_message('Sorry, please do your confession on the confessions channel.', ephemeral=True)
        else:
            print(f'/confess: {error}')
            await interaction.response.send_message('Uknown Error, please report to admin or dev.', ephemeral=True)

    @bot.tree.command(name='poll', description='Make a poll')
    @app_commands.guild_only()
    @app_commands.check(can_poll)
    @app_commands.describe(title= 'The title of the poll',question = 'What would you like to ask?', options = 'Add options separated by a \"/\"')
    async def poll( interaction: discord.Interaction, title: str, question: str, options: str):
        options = options.split('/')
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        if len(options) >= 2 and len(options) <= 10:
            embed_message = f'{question}\n\n'
            for i in range(1, len(options) + 1):
                embed_message += f'{emojis[i-1]}. {options[i-1]}\n'
            embeded_poll = discord.Embed(title=f"🫧  Poll: {title}", description=embed_message, color=0x9dc8d1)
            embeded_poll.set_author(name=f'{interaction.user.global_name}', icon_url=interaction.user.avatar.url)
            poll_message = await interaction.channel.send(embed=embeded_poll)
            for i in range(1, len(options) + 1):
                await poll_message.add_reaction(emojis[i-1])
            await interaction.response.send_message(f'Poll was succesfully posted!', ephemeral=True)
        else:
            await interaction.response.send_message(f'Sorry, the number of options needs to be between 2-10. Your input had {len(options)} options', ephemeral=True)
    
    @poll.error
    async def poll_error(interaction : discord.Interaction, error):
        if not can_poll(interaction):
            await interaction.response.send_message('Sorry, only an admin can poll', ephemeral=True)
        else:
            print(f'/poll: {error}')
            await interaction.response.send_message('Uknown Error, please report to admin or dev.', ephemeral=True)



# ! Depricated, need to implement new way of handling these
async def answer_message(original_message):
    try:
        response = responses.handle_response(str(original_message.content))
        if response != '':
            await original_message.channel.send(response)

    except Exception as e:
        print(e)


async def send_purge_audit(member: discord.Member, guild_id: int, limit : int, channel):
    if serverDict.__contains__(guild_id):
        if serverDict[guild_id].audit_enabled and not serverDict[guild_id].audit_channel_id == 0:
            if type(bot.get_channel(serverDict[guild_id].audit_channel_id)) is None:
                log = f"{member.global_name} called purge for {limit} messages in \"{channel.name}\"\n"
                embededLog = discord.Embed(title="🫧", description=log, color=0x9dc8d1)
                await bot.get_channel(serverDict[guild_id].audit_channel_id).send(embed=embededLog)
            else:
                print(f'Guild {bot.get_guild(guild_id).name} has an Audit Log channel registered but it cannot be found in the guild.')


# On these methods context means either context from a command or message
def get_guild(context: commands.Context):
    return bot.get_guild(context.guild.id)


def is_owner(context: commands.Context):
    return context.author.id == context.guild.owner_id


def can_manage_channels(member: discord.Member):
    return member.guild_permissions.manage_channels


def is_DM(channel: discord.channel):
    return isinstance(channel, discord.DMChannel)


def can_confess(interaction : discord.Interaction):
    if bot.get_channel(serverDict[interaction.guild.id].confessions_channel_id) is None:
        return False
    elif serverDict[interaction.guild.id].confessions_allowed and serverDict[interaction.guild.id].confessions_channel_id == interaction.channel.id:
        return True
    else:
        return False


def can_poll(interaction: discord.Interaction):
    return interaction.user.guild_permissions.manage_channels


def is_permitted_to_purge(member: discord.Member):
    return member.guild_permissions.manage_channels

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
        
        print('Servers Loaded:')
        for key in serverDict:
            print(f'\"{serverDict[key]}\"')

        file.close()
    
    print('Server data was loaded')


def load_welcome_messages():
    global welcomeDict
    print('Loading welcome message data...')

    with open('welcome.json', 'r') as file:
        jsondict = json.loads(file.read())

        welcomeDict = jsondict

        print('Welcome messages loaded')

        file.close()


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
        self.welcome_enabled = False
    
    def __str__(self) -> str:
        return f'id: {self.id}  welcome_channel_id: {self.welcome_channel_id}  audit_channel_id: {self.audit_channel_id}  confessions_channel_id: {self.confessions_channel_id}  confessions_allowed: {self.confessions_allowed}  audit_enabled: {self.audit_enabled}  welcome_enabled: {self.welcome_enabled}'

    def load_data(self, dictionary):
        self.id = dictionary['id']
        self.welcome_channel_id = dictionary['welcome_channel_id']
        self.audit_channel_id = dictionary['audit_channel_id']
        self.confessions_channel_id = dictionary['confessions_channel_id']
        self.confessions_allowed = dictionary['confessions_allowed']
        self.audit_enabled = dictionary['audit_enabled']
        self.welcome_enabled = dictionary['welcome_enabled']


# TODO: Add enable welcome, and add welcome messages

# * Commit:
# - 