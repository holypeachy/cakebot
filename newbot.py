# Main Packages
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

# Other scripts
import responses

# Settings from config.py
from config import TOKEN
from config import COMMAND_PREFIX
from config import RAPIAPI_KEY

# Errors
from discord.ext.commands import CommandNotFound
from discord.ext.commands import MissingRequiredArgument
from  asyncio import TimeoutError

# Other Packages
import pytz
import random
import json
import requests
import threading, asyncio, datetime, time


# Global vars
serverDict = dict()
welcomeMessageDict = dict()
goodbyeDict = dict()
idsDict = { 'vibes': 339550706342035456, 'sufyaan': 851221324126093382, 'tayimo': 403249158187778067, 'kena': 700077496909037679, 'peach': 266621758205853708}
bot = None

role_select_emojis = [
    "😇","❤️","💥","👍","😭","💵","😘","🍕","😍","✨","🎉","😃","💕","🥺","⚠️","🔥","😊","🐣","🖤","🐼","🙄","🥳","💯", "👻",
]


# ? APIs
# Chuck Norris API
chuck_url = "https://matchilling-chuck-norris-jokes-v1.p.rapidapi.com/jokes/random"
chuck_headers = {
	"accept": "application/json",
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "matchilling-chuck-norris-jokes-v1.p.rapidapi.com"
}

# Weather API
weather_url = "https://weatherapi-com.p.rapidapi.com/current.json"
weather_headers = {
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
}

# Cats API
cats_url = "https://cat14.p.rapidapi.com/v1/images/search"
cats_headers = {
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "cat14.p.rapidapi.com"
}

# Porn Star API
pstar_url = "https://papi-pornstarsapi.p.rapidapi.com/pornstars/"
pstar_headers = {
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "papi-pornstarsapi.p.rapidapi.com"
}

# Porn Gallery API
lewd_url = "https://porn-gallery.p.rapidapi.com/pornos/"
lewd_headers = {
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "porn-gallery.p.rapidapi.com"
}
current_lewd_users = []

# CheapShark API
cheapshark_stores = None
discount_url = "https://cheapshark-game-deals.p.rapidapi.com/deals"
discount_games_url = "https://cheapshark-game-deals.p.rapidapi.com/games"
discount_headers = {
	"X-RapidAPI-Key": f"{RAPIAPI_KEY}",
	"X-RapidAPI-Host": "cheapshark-game-deals.p.rapidapi.com"
}
DEALS_DAY_OF_WEEK = 5
DEALS_AMOUNT = 10


def start_bot():
    # Intents
    my_intents = discord.Intents.default()
    my_intents.message_content = True
    my_intents.dm_messages = True
    my_intents.members = True
    my_intents.guild_reactions = True

    # Setting up the bot's client
    global bot
    bot = commands.Bot(COMMAND_PREFIX, intents=my_intents, help_command=None)

    # Loads the stored server data from the json file
    load_servers()

    load_messages()

    fetch_cheapshark_stores()


    # These methods are organizational and contain the events and commands that will be registered async
    event_methods()

    dev_command_methods()

    command_methods()

    slash_commands_methods()

    lewd_commands()

    # Run bot
    bot.run(TOKEN)


# Command Categories
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

        offer_timer_thread = threading.Thread(target=start_offer_timer, daemon=True)
        offer_timer_thread.start()

        print('\033[92m' + f'{bot.user} is now running!' + '\033[0m')


    @bot.event
    async def on_audit_log_entry_create(entry: discord.AuditLogEntry):
        # We get the time of the entry in iso format
        time = entry.created_at.astimezone(tz=pytz.timezone('America/New_York')).isoformat()

        # Log for the terminal
        print('\nServer log:')
        print(f" Guild: \"{entry.guild.name}\" id: {entry.guild.id} Server Nickname: {'No nickname' if (type(entry.user) is discord.user.User or type(entry.user) is None) else entry.user.nick} User: {entry.user.global_name} ID:{entry.user.name} | Action: {entry.action.name} | Date: {time.split('T')[0]} Time: {time.split('T')[1].split('.')[0]} EST\n")

        # Update Role Select if roles were changed in server
        if entry.action in [discord.AuditLogAction.role_create, discord.AuditLogAction.role_update, discord.AuditLogAction.role_delete] and await is_role_select_setup(entry.guild.id):
            channel = bot.get_channel(serverDict[entry.guild.id].role_select_channel)
            
            # This directly makes a call to the discord servers, should never return an error
            for message_id in serverDict[entry.guild.id].role_select_messages:
                original_message = await channel.fetch_message(message_id)
                await original_message.delete()

            # Check if excluded roles still exist, if it doesn't we remove it from excluded list
            for role_id in serverDict[entry.guild.id].role_select_excluded:
                if any(role.id == role_id for role in entry.guild.roles) == False:
                    serverDict[entry.guild.id].role_select_excluded.remove(role_id)

            save_servers()
            # We resend the role_select message and we delete original
            await role_select_function(channel, entry.guild, entry.guild.owner)

        # We check if we need to send the guild the log
        if serverDict[entry.guild.id].audit_enabled:
            channel = entry.guild.get_channel(serverDict[entry.guild.id].audit_channel_id)

            if channel is None:
                if serverDict[entry.guild.id].audit_channel_id == 0:
                    print(f'Server \"{entry.guild.name}\" has not set up a AuditLog channel yet!')
                else:
                    print(f'Server \"{entry.guild.name}\" has a registered AuditLog Channel that is not found in the server!')
            else:
                log = f"{entry.user.name}  {entry.action.name} \n{time.split('T')[0]} at {time.split('T')[1].split('.')[0]} EST"
                embededLog = discord.Embed(title="🫧  Log Entry", description=log, color=0x9dc8d1)
                embededLog.set_author(name=f'{entry.user.global_name}', icon_url=entry.user.avatar.url)
                embededLog.set_thumbnail(url=entry.user.avatar.url)
                await channel.send(embed=embededLog)

        else:
            print(f'Audit log disabled for  \"{entry.guild.name}\" guild')

 
    @bot.event
    async def on_command_error(context, error):
        if isinstance(error, CommandNotFound):
            print("Command Error: Command not found!")
        elif isinstance(error, MissingRequiredArgument):
            print("Command Error: Missing argument!")
        else:
            print(f'Command Error: \"{error}\"') # Printing it cus it's less important
            # raise error


    @bot.event
    async def on_member_join(member: discord.Member):
        # Terminal log
        print(f'\"{member.global_name}\" (username: {member.name}) joined the server {member.guild.name}\n')


        if serverDict.__contains__(member.guild.id): # Just in case
            serverInfo = serverDict[member.guild.id]
            if serverInfo.welcome_enabled:
                # Here we check if registered channel exists, if it does we send the welcome message
                welcome_channel = bot.get_channel(serverInfo.welcome_channel_id)
                if welcome_channel is None:
                    print(f'Welcome channel for guild \"{member.guild.name}\" is enabled but the stored channel cannot be found')
                else:
                    random_number = random.randint(0, len(welcomeMessageDict) - 1)
                    welcome_message = welcomeMessageDict[str(random_number)]
                    welcome_message = welcome_message.replace('{user}', f'<@{member.id}>')
                    embeded_welcome = discord.Embed(title="🫧", description=welcome_message, color=0x9dc8d1)
                    embeded_welcome.set_author(name=f'{member.global_name}', icon_url=member.avatar.url)
                    embeded_welcome.set_thumbnail(url='https://cdn.discordapp.com/attachments/1136729265530998884/1145392932120186890/Cute.JPG')
                    await welcome_channel.send(embed=embeded_welcome)
    

    @bot.event
    async def on_member_remove(member: discord.Member):

        print(f'\"{member.global_name}\" (username: {member.name}) has left (or removed from) the server {member.guild.name}\n')

        if serverDict.__contains__(member.guild.id): # Just in case
            # Here we check if registered channel exists, if it does we send the welcome message
            serverInfo = serverDict[member.guild.id]
            if serverInfo.welcome_enabled:
                welcome_channel = bot.get_channel(serverInfo.welcome_channel_id)
                if welcome_channel is None:
                    print(f'Welcome channel for guild {member.guild.name} is enabled but the stored channel cannot be found')
                else:
                    random_number = random.randint(1, len(goodbyeDict))
                    goodbye_message = goodbyeDict[str(random_number)]
                    goodbye_message = goodbye_message.replace('{user}', f'<@{member.id}>')
                    embeded_goodbye = discord.Embed(title="🫧", description=goodbye_message, color=0x9dc8d1)
                    embeded_goodbye.set_author(name=f'{member.global_name}', icon_url=member.avatar.url)
                    embeded_goodbye.set_thumbnail(url='https://cdn.discordapp.com/attachments/1136729265530998884/1145393743189508178/IMG_20230818_170852_197.jpg')
                    await welcome_channel.send(embed=embeded_goodbye)


    @bot.event
    async def on_guild_join(guild: discord.Guild):
        # Bot joins guild
        print(f'{bot.user} joined a new guild \"{guild.name}\" id: {guild.id}')
        # We make a new Server object and put it in dictionary. We Then save servers
        serverDict[guild.id] = Server(guild.id)
        save_servers()


    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        # Bot leaves guild, gets kicked, or banned
        print(f'{bot.user} has left guild \"{guild.name}\" id: {guild.id}')
        # We delete the guild and its data after leaving
        if serverDict.__contains__(guild.id):
            del serverDict[guild.id]
            save_servers()


    @bot.event
    async def on_message(message: discord.Message):
        # Ignores Bot's own messages
        if message.author == bot.user:
            return

        # ! Checks if a DM is a from a guild member. Probably unnecesary
        is_member_in_guild = False
        if is_DM(message.channel):
            for entry in serverDict:
                temp_guild = bot.get_guild(entry)
                temp_member = temp_guild.get_member(message.author.id)
                if not type(temp_member) is None:
                    is_member_in_guild = True
                    break
            if not is_member_in_guild:
                print(f'Member {temp_member.global_name} is not in any of the servers')
                await message.author.send('Sorry but you are not a member of the servers I know')
                return
                

        # Message log
        #if not is_DM(message.channel):
        print(f"\n\"{message.author.global_name}\" / \"{message.author}\" said: \"{str(message.content)}\" in \"{message.channel}\" server: \"{message.guild}\"")

        # * This actually processes the commands since we overrode on_message()
        await bot.process_commands(message)

        # Custom text messages
        if not is_DM(message.channel):
            await handle_message(message)


    @bot.event
    async def on_raw_reaction_add(payload : discord.RawReactionActionEvent):
        channel = bot.get_channel(payload.channel_id)
        if not is_DM(channel):
            # Is channel None? AND is the message the same as the stored one AND is the the user not the bot 
            if channel and payload.message_id in serverDict[payload.guild_id].role_select_messages and payload.user_id != bot.user.id:
                message_index = serverDict[payload.guild_id].role_select_messages.index(payload.message_id)
                roleDict = serverDict[payload.guild_id].role_select_dicts[message_index]
                if payload.emoji.__str__() in roleDict.keys():
                    guild = bot.get_guild(payload.guild_id)
                    role_to_add = guild.get_role(roleDict[payload.emoji.__str__()])

                    await guild.get_member(payload.user_id).add_roles(role_to_add)
    
    
    @bot.event
    async def on_raw_reaction_remove(payload : discord.RawReactionActionEvent):
        channel = bot.get_channel(payload.channel_id)
        if not is_DM(channel):
            # Is channel None? AND is the message the same as the stored one AND is the the user not the bot 
            if channel and payload.message_id in serverDict[payload.guild_id].role_select_messages and payload.user_id != bot.user.id:
                message_index = serverDict[payload.guild_id].role_select_messages.index(payload.message_id)
                roleDict = serverDict[payload.guild_id].role_select_dicts[message_index]
                if payload.emoji.__str__() in roleDict.keys():
                    guild = bot.get_guild(payload.guild_id)
                    role_to_remove = guild.get_role(roleDict[payload.emoji.__str__()])
                    
                    if not role_to_remove.name.lower() == 'minor':
                        await guild.get_member(payload.user_id).remove_roles(role_to_remove)


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

                # ! Tayimo's preference
                if context.author.id == idsDict['tayimo']:
                    await context.channel.send(f'# 🤠👉          💥💀\n> **{player2}** wins!')
                elif player2id == idsDict['tayimo']:
                    await context.channel.send(f'# 💀💥          👈🤠\n> **{player1}** wins!')

                elif random.randint(1, 10) <= 5:
                    await context.channel.send(f'# 💀💥          👈🤠\n> **{player1}** wins!')
                else:
                    await context.channel.send(f'# 🤠👉          💥💀\n> **{player2}** wins!')
            else:
                await context.channel.send(f'The usage of the command is:\n' + COMMAND_PREFIX +'standoff @user\n')
        else:
            await context.author.send(f'Sorry, you can\'t use that command here. Please, do it in the server')


    @bot.command(name='help')
    async def help(context: commands.Context):
        if not is_DM(context.channel):
            message = ''
            message += f'>>> 🍰 Hi! My current commands are:\n**{COMMAND_PREFIX}repeat** I will repeat anything you say\n**{COMMAND_PREFIX}standoff** Want to do a cowboy stand off against a friend? 🤠\n\n'
            message += f'**/confess** in the confessions channel to send an anonymous confessions\n**/suggest** Allows you to send a suggestion to admins about the server or CakeBot!\n\n**{COMMAND_PREFIX}chuck** Wanna know some cool, Chuck Norris facts?\n**{COMMAND_PREFIX}weather** '
            message += f'Allows you to see the current weather conditions of a location of your choosing\n**{COMMAND_PREFIX}cat** Wanna see a cute cat picture?\n\n**{COMMAND_PREFIX}roles** '
            message += f'Shows all the roles in the server\n\n**{COMMAND_PREFIX}discounts** Shows you the **best** discounts on steam, or allows you to search for a **game** in different stores\n\n🔞 Adult Commands (DM Only):\n**{COMMAND_PREFIX}pstar** Wanna see some \"stats\" on your favorite star?\n**{COMMAND_PREFIX}lewd** '
            message += f'Want some tasty pics from your favorite categories? 😋'
            if can_manage_channels(context.author):
                message += f'\n\n**💝 For Admins**\n**{COMMAND_PREFIX}embed** Allows you to create an embeded message\n**/poll** Allows you to create polls\n**{COMMAND_PREFIX}purge** Will delete x number of messages from the current channel\n\n**{COMMAND_PREFIX}'
                message += f'role_select** Sends the message to allow people to select roles\n**{COMMAND_PREFIX}role_exclude** Allows you to exclude roles from Role Select\n**{COMMAND_PREFIX}reset_role_exclude**'
                message += f' Resets the list of excluded roles\n\n**{COMMAND_PREFIX}set_welcome** Sets the Welcome channel\n**{COMMAND_PREFIX}'
                message += f'set_audit** Sets the AuditLog channel\n**{COMMAND_PREFIX}set_confessions** Sets the Confessions channel\n**{COMMAND_PREFIX}set_suggestions** Sets the Suggestions channel\n**{COMMAND_PREFIX}enable_confessions** Enable or disable confessions for this server\n**'
                message += f'{COMMAND_PREFIX}enable_audit** Enable or disable Audit Logs in this server\n**{COMMAND_PREFIX}enable_welcome** Enable or disable welcome messages in this server\n**{COMMAND_PREFIX}enable_suggestions** Enable or disable suggestions in this server \n\n**{COMMAND_PREFIX}set_discounts** Will send a message with current offers and will set the channel for future weekly offer messages\n'
                message += f'**{COMMAND_PREFIX}enable_discounts** Allows you to enable or disable weekly Steam offer messages for your server'

            message += f'\n\n⚠️ If you need help with individual commands type that command!'
            await context.send(message)

        
    # ! Usage: !purge [limit] | Depricated-ish
    @bot.command(name='purge_og')
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
                await send_purge_audit(context.author, context.guild, limit, context.channel)
                await context.channel.purge(limit=limit+1)
            else:
                await context.channel.send('Sorry, only an admin can purge 😖')
    
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
            if can_manage_channels(context.author):
                embededMessage = discord.Embed(title=f"🫧  {title}", description=message, color=0x9dc8d1)
                embededMessage.set_author(name=f'{context.author.global_name}', icon_url=context.author.avatar.url)
                await context.channel.send(embed=embededMessage)
            else:
                await context.channel.send(f'Sorry, only an admin can do that 😓')

    @embed.error
    async def embed_error(context: commands.Context, error):
        if not is_DM(context.channel):
            if not context.author.guild_permissions.manage_channels:
                await context.channel.send(f'Sorry, only an admin can do that')
            else:
                await context.channel.send(f'The command is:\n{COMMAND_PREFIX}embed "My Embed Title" "I would like to say cake is great!  🍰"')


    @bot.command(name='roles')
    async def show_roles(context: commands.Context):
        if not is_DM(context.channel):
            roles_message = ''
            for r in context.guild.roles:
                roles_message += '' if r.name == '@everyone' else f'- {r.name}\n'

            if len(serverDict[context.guild.id].role_select_excluded) != 0:
                roles_message += '\n Roles you cannot select and which must be given by staff are:\n'
                for role_id in serverDict[context.guild.id].role_select_excluded:
                    current_role = context.guild.get_role(role_id)
                    roles_message += f'- {current_role.name}\n'

            embededMessage = discord.Embed(title=f"🫧  These are all the Roles in {context.guild.name}", description=roles_message, color=0x9dc8d1)
            embededMessage.set_author(name=f'{context.guild.owner.global_name}', icon_url=context.guild.owner.avatar.url)
            embededMessage.set_thumbnail(url=context.guild.icon.url)

            await context.channel.send(embed=embededMessage)


    @bot.command(name='role_select')
    async def role_select(context: commands.Context):
        # ! I made this to be able to call role_select from another place aka on_audit_log_entry_create when updating role_select
        await role_select_function(context.channel, context.guild, context.author)


    @bot.command(name='role_exclude')
    async def role_exclude(context: commands.Context, *args):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                if len(args) == 0:
                    await context.channel.send(f'The command is:\n{COMMAND_PREFIX}role_exclude Admin Mod \"The Kueen"')
                else:
                    # We loop through the provided roles
                    for arg in args:
                        # We check if role (arg) matches the name of any roles in the guild roles
                        if any(role.name == arg for role in context.guild.roles):
                            filtered_roles = list(filter(lambda role: role.name == arg, context.guild.roles)) # Since we found we filter out those roles
                            if not serverDict[context.guild.id].role_select_excluded.__contains__(filtered_roles[0].id): # filtered_roles is a list, we get just first just in case. But it will never be more than 1
                                # If we haven't already added it to the list, we add it
                                serverDict[context.guild.id].role_select_excluded.append(filtered_roles[0].id)
                        else:
                           await context.channel.send(f'⚠️ Role \"{arg}\" was not found in the server. Check for typos.')
                    
                    message = ''
                    for role_id in serverDict[context.guild.id].role_select_excluded:
                        message += f'- {context.guild.get_role(role_id).name}\n'

                    message += f'\n⚠️ Remember to redo {COMMAND_PREFIX}role_select if it\'s in the server already, to make sure no one can select this role'
                    embededMessage = discord.Embed(title=f"🫧  Roles to Exclude from \"Role Select\"", description=message, color=0x9dc8d1)
                    embededMessage.set_footer(text='Changes have been saved')
                    embededMessage.set_thumbnail(url=context.guild.icon.url)
                    
                    save_servers()
                    await context.channel.send(embed=embededMessage)
            else:
                await context.channel.send(f'Sorry, only an admin can do that ☹️')


    @bot.command(name='reset_role_exclude')
    async def reset_role_exclude(context: commands.Context):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                def check_for_answer(m: discord.Message):
                    if m.content.lower().startswith('yes reset') and m.channel == context.channel and m.author == context.author:
                        return True
                    elif m.content.lower().startswith('no reset') and m.channel == context.channel and m.author == context.author:
                        return True
                    else:
                        return False
                await context.channel.send('⚠️ Type \"yes reset\" to confirm or \"no reset\" within 12 seconds to cancel.')

                try:
                    answer = await bot.wait_for("message", check=check_for_answer, timeout=12)
                except Exception as e:
                    if isinstance(e, TimeoutError):
                        await context.channel.send('⚠️ Timeout, I will assume you do not want to reset the excluded roles')
                    else:
                        raise e
                
                if answer.content.lower().startswith('yes reset'):
                    serverDict[context.guild.id].role_select_excluded = list()
                    save_servers()
                    await context.channel.send('The list of excluded roles for \"Role Select\" has been reset!')
                elif answer.content.lower().startswith('no reset'):
                    await context.channel.send('Roles have not been reset')
            
            else:
                await context.channel.send(f'Sorry, only an admin can do that')


    @bot.command(name='chuck')
    async def chuck_random(context: commands.Context):
        if not is_DM(context.channel):
            chuck_images = ['https://images01.military.com/sites/default/files/styles/full/public/2021-04/chucknorris.jpeg.jpg?itok=2b4A6n29', 'http://ultimateactionmovies.com/wp-content/uploads/2017/12/Chuck-Norris.jpg',
                            'https://www.joblo.com/wp-content/uploads/2023/05/Chuck-Norris-Invasion-USA-jpg.webp', 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Chuck_Norris%2C_The_Delta_Force_1986.jpg/800px-Chuck_Norris%2C_The_Delta_Force_1986.jpg',
                            'https://www.syfy.com/sites/syfy/files/2023/03/walker_texas_ranger.jpg', 'https://images.fineartamerica.com/images/artworkimages/mediumlarge/2/chuck-norris-in-walker-texas-ranger-1993--album.jpg',
                            'https://images02.military.com/sites/default/files/styles/full/public/2023-05/1time%20chuck%20norris%20water%201200.jpg', 'https://dlqxt4mfnxo6k.cloudfront.net/homesbytaber.com/aHR0cHM6Ly9zMy5hbWF6b25hd3MuY29tL2J1aWxkZXJjbG91ZC8yZDE2YzhkYzI2NmQxZGQyMDZkOTBhZDQ1YzRlNGViNi5qcGVn/webp/800/800',]
            response = requests.get(chuck_url, headers=chuck_headers)
            embededMessage = discord.Embed(title=f"🫧  Did you know?", description=response.json()['value'], color=0x9dc8d1)
            embededMessage.set_author(name=f'{bot.user.display_name}', icon_url=bot.user.avatar.url)
            embededMessage.set_image(url=f'{chuck_images[random.randint(0, len(chuck_images) - 1)]}')
            await context.channel.send(embed=embededMessage)


    @bot.command(name='weather')
    async def weather(context: commands.Context, *, arg):
        if not is_DM(context.channel):
            querystring = {"q":f"{arg}"}
            response = requests.get(weather_url, headers=weather_headers, params=querystring)

            json_response = response.json()
            if 'error' in json_response.keys():
                await context.channel.send(f"⚠️ {json_response['error']['message']}")
                return
            location = json_response['location']
            current = json_response['current']
            
            report = f"🌬️  Condition: {current['condition']['text']}\n🌡️  Temperature: {current['temp_f']}F ({current['temp_c']}C)\n🎁  Feels Like: {current['feelslike_f']}F ({current['feelslike_c']}C)\n "
            embededMessage = discord.Embed(title=f"{location['name']}, {location['region']} ({location['country']})", description=report, color=0x9dc8d1)
            embededMessage.set_author(name=f'Weather in:', icon_url=f"https:{current['condition']['icon']}")
            embededMessage.set_thumbnail(url= f"https:{current['condition']['icon']}")
            embededMessage.set_footer(text=f"⌚ Local Time: {location['localtime']}")
            await context.channel.send(embed=embededMessage)

    @weather.error
    async def weather_error(context: commands.Context, error):
        if not is_DM(context.channel):
            await context.channel.send(f'The command is:\n{COMMAND_PREFIX}weather New York')


    @bot.command(name='cat')
    async def cat(context: commands.Context):
        if not is_DM(context.channel):
            querystring = {"limit":"1"}

            response = requests.get(cats_url, headers=cats_headers, params=querystring)
            json_response = response.json()

            embededMessage = discord.Embed(title=f"🫧  Here is your cat image 🐱", color=0x9dc8d1)
            embededMessage.set_author(name=f'{context.author.global_name}', icon_url=context.author.avatar.url)
            embededMessage.set_image(url=f"{json_response[0]['url']}")
            await context.channel.send(embed=embededMessage)


    @bot.command(name='discounts')
    async def discounts(context: commands.Context, command: str, argument: str):
        if not is_DM(context.channel):
            if command.lower() == 'best':
                try:
                    if 11 > int(argument) > 0:
                        cheapshark_link = 'https://www.cheapshark.com/redirect?dealID='
                        querystring = {"storeID[0]":"1","metacritic":"0","onSale":"true","pageNumber":"0","upperPrice":"50","exact":"0","pageSize":f"{int(argument)}","sortBy":"Deal Rating","steamworks":"0","output":"json","desc":"0","steamRating":"0","lowerPrice":"0"}
                        response = requests.get(url=discount_url, headers=discount_headers, params=querystring)
                        json_response = response.json()

                        try:
                            if json_response['message']:
                                await context.channel.send('⚠️ This service is temporarily down, please try again in an hour.')
                                return
                        except Exception as e:
                            pass

                        message = f'Hey there {context.author.display_name}!! 😊 - Here {"is" if int(argument) == 0 else "are"} {int(argument)} great deals on steam!\n'
                        for game in json_response:
                            message += f"### {game['title']}\n💸 - Price: ${game['salePrice']}  |  ~~{game['normalPrice']}~~  \n⭐ - Steam Rating: {game['steamRatingPercent']}% ({game['steamRatingCount']})\n💦 - Deal Rating: {game['dealRating']}\n🍰  [Steam Link]({cheapshark_link+game['dealID']})  🍰\n\n"

                        embededMessage = discord.Embed(title=f"🫧  Best Discounts!", description=message, color=0x9dc8d1)
                        embededMessage.set_author(name=f'{context.author.display_name}', icon_url=context.author.avatar.url)
                        embededMessage.set_footer(text='>>> Powered by CheapShark\nNote from dev: CheapShark is great guys, use the links above to support them!\nThe links take you to Steam NOT their website.')
                        await context.channel.send(embed=embededMessage)
                    else:
                        await context.channel.send('Please enter a value between 1 and 10!')
                except:
                        await context.channel.send('Please enter a value between 1 and 10!')
            elif command.lower() == 'game':
                cheapshark_link = 'https://www.cheapshark.com/redirect?dealID='

                querystring = {"limit":"60","exact":"0","title":f"{argument}"}
                response = requests.get(url=discount_games_url, headers=discount_headers, params=querystring)
                json_response = response.json()

                try:
                    if json_response['message']:
                        await context.channel.send('⚠️ This service is temporarily down, please try again in an hour.')
                        return
                except Exception as e:
                    pass

                if len(json_response) == 0:
                    await context.channel.send(f'Game: \"{argument}\" was not found!')
                else:
                    game_id = json_response[0]['gameID']

                    querystring = {"id":f"{game_id}"}
                    response = requests.get(url=discount_games_url, headers=discount_headers, params=querystring)
                    json_response = response.json()
                    
                    game_name = json_response["info"]["title"]

                    message = f'Hey there {context.author.display_name}!! 😊 - Here are the best deals for **{game_name}** right now!\n'
                    message += f'\n**💸 Cheapest Price Ever: ${json_response["cheapestPriceEver"]["price"]}**\n'

                    at_least_one = False
                    for deal in json_response['deals']:
                        storeID = deal['storeID']
                        store_name = cheapshark_stores[int(storeID) - 1]['storeName']
                        if cheapshark_stores[int(storeID) - 1]['isActive'] == 0:
                            continue
                        
                        if deal['price'] == deal['retailPrice']:
                            continue
                        message += f"### Store: {store_name}\n💸 - Price: ${deal['price']}  |  ~~{deal['retailPrice']}~~\n🍰  [{store_name} Link]({cheapshark_link+deal['dealID']})  🍰\n\n"
                        at_least_one = True

                    if not at_least_one:
                        message += f'## Sorry, no discounts for this game were found as of right now 😢'
                    
                    embededMessage = discord.Embed(title=f"🫧  {game_name} Discounts!", description=message, color=0x9dc8d1)
                    embededMessage.set_author(name=f'{context.author.display_name}', icon_url=context.author.avatar.url)
                    embededMessage.set_footer(text='>>> Powered by CheapShark\n')
                    embededMessage.set_thumbnail(url=json_response['info']['thumb'])
                    await context.channel.send(embed=embededMessage)
            else:
                await context.channel.send(f'The command goes like:\n**{COMMAND_PREFIX}discounts game \"Assassin\'s Creed\"**\nor\n**{COMMAND_PREFIX}discounts best 5**')

    @discounts.error
    async def discounts_error(context: commands.Context, error):
        if not is_DM(context.channel):
            if type(error) is ValueError:
                pass
            else:
                await context.channel.send(f'The command goes like:\n**{COMMAND_PREFIX}discounts game \"Assassin\'s Creed\"**\nor\n**{COMMAND_PREFIX}discounts best 5**')


    @bot.command(name='set_discounts')
    async def set_discounts(context: commands.Context):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                serverDict[context.guild.id].discount_promote_channel_id = context.channel.id
                serverDict[context.guild.id].automated_discounts = True
                save_servers()
                await send_discount_message(context.guild)
            else:
                await context.channel.send('Sorry only an admin can do that 😔')


    @bot.command(name='enable_discounts')
    async def enable_discounts(context: commands.Context, arg):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                if serverDict[context.guild.id].discount_promote_channel_id == 0:
                    await context.send(f'Please set a Promote channel before enabling it! Use the following command to do so:\n**{COMMAND_PREFIX}set_discounts**')
                elif arg.lower() == 'true' or arg.lower() == 'false':
                    serverDict[context.guild.id].automated_discounts = True if arg == 'true' else False
                    state = serverDict[context.guild.id].automated_discounts
                    save_servers()
                    await context.channel.send('Automated Steam offer messages are now enabled!' if (state == True) else 'Automated Steam offer messages are now disabled!')
                else:
                    await context.send(f'The command is:\n**{COMMAND_PREFIX}enable_discounts true**')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')
    
    @enable_discounts.error
    async def enable_discounts_error(context: commands.Context, error):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                await context.send(f'The command is:\n**{COMMAND_PREFIX}enable_discounts true**')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')


    @bot.command(name='set_suggestions')
    async def set_suggestions(context: commands.Context):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                serverDict[context.guild.id].suggest_target_channel = context.channel.id
                save_servers()
                await context.channel.send('Channel has been set! This is where all user suggestions will go!')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')


    @bot.command(name='enable_suggestions')
    async def enable_suggestions(context: commands.Context, arg):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                if serverDict[context.guild.id].suggest_target_channel == 0:
                    await context.send(f'Please set a suggestions channel before enabling it! Use the following command to do so:\n**{COMMAND_PREFIX}set_suggestions**')
                elif arg.lower() == 'true' or arg.lower() == 'false':
                    serverDict[context.guild.id].suggest_enabled = True if arg == 'true' else False
                    state = serverDict[context.guild.id].suggest_enabled
                    save_servers()
                    await context.channel.send('Suggestions are now enabled!' if (state == True) else 'Suggestions are now disabled')
                else:
                    await context.send(f'The command is:\n{COMMAND_PREFIX}enable_suggestions true')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')
    
    @enable_suggestions.error
    async def enable_suggestions_error(context: commands.Context, error):
        if not is_DM(context.channel):
            if can_manage_channels(context.author):
                await context.send(f'The command is:\n{COMMAND_PREFIX}enable_suggestions true')
            else:
                await context.channel.send('Sorry only an admin can do that 😔')


def slash_commands_methods():
    @bot.tree.command(name='confess', description='Tell a secret while remaining anonymous')
    @app_commands.guild_only()
    @app_commands.check(can_confess)
    @app_commands.describe(confession = 'What would you like to confess?')
    @app_commands.describe(image= 'Would you like to attach an image?')
    async def confess(interaction: discord.Interaction, confession: str, image: Optional[discord.Attachment] = None):
        if '@everyone' in confession:
            await interaction.response.send_message('Please don\'t mention everyone on your confession', ephemeral=True)
        else:
            hasImage = False
            embededConfession = discord.Embed(title="🫧  By Anonymous Member!", description=confession, color=0x9dc8d1)
            if image:
                if image.content_type and image.content_type.startswith("image/"):
                    embededConfession.set_image(url=image.url)
                    hasImage = True
                else:
                    await interaction.response.send_message("The file you uploaded is not an image, please make sure it's an image.\nYour confession:\n\n" + confession, ephemeral=True)
                    return
            await interaction.response.send_message('Your confession has been successfully posted and only you can see this message', ephemeral=True)
            confessions_channel = interaction.guild.get_channel(serverDict[interaction.guild.id].confessions_channel_id)
            await confessions_channel.send(embed=embededConfession)
            await send_confession_audit(interaction.guild, interaction.user, confession, hasImage)
    
    @confess.error
    async def confess_error(interaction : discord.Interaction, error):
        if serverDict[interaction.guild.id].confessions_channel_id == 0:
            await interaction.response.send_message('Confessions channel is not set for this server, please tell an admin to set a confessions channel!', ephemeral=True)
        elif not serverDict[interaction.guild.id].confessions_allowed:
            await interaction.response.send_message('Sorry, confessions are not allowed on this server, tell an admin to enable them.', ephemeral=True)
        elif bot.get_channel(serverDict[interaction.guild.id].confessions_channel_id) is None:
            await interaction.response.send_message('A Confessions channel is set but it is not found in this server (could\'ve been deleted). Please tell an admin about this problem.', ephemeral=True)
        # elif not serverDict[interaction.guild.id].confessions_channel_id == interaction.channel.id:
        #     await interaction.response.send_message('Sorry, please do your confession on the confessions channel.', ephemeral=True)
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


    @bot.tree.command(name='suggest', description='Send the admins your suggestions on how to make the server or cakebot better!')
    @app_commands.guild_only()
    @app_commands.describe(suggestion = 'What would you like to suggest?')
    async def suggest( interaction: discord.Interaction, suggestion: str):
        channel_id = serverDict[interaction.guild.id].suggest_target_channel
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            if serverDict[interaction.guild.id].suggest_enabled:
                embededMessage = discord.Embed(title=f"🫧  Suggestion:", description=suggestion, color=0x9dc8d1)
                embededMessage.set_author(name=f'{interaction.user.display_name}', icon_url=interaction.user.avatar.url)
                await channel.send(embed=embededMessage)

                await interaction.response.send_message(f'Your suggestion was successfully sent!', ephemeral=True)
            else:
                await interaction.response.send_message(f'Sorry, but suggestions are disabled for this server. Please contact an admin about this.', ephemeral=True)
        else:
            await interaction.response.send_message(f'Sorry, but a suggestions channel is not yet set! Contact an admin about this.', ephemeral=True)


def lewd_commands():
    @bot.command(name='pstar')
    async def pstar_info(context: commands.Context, *, arg):
        if is_DM(context.channel):
            querystring = {"name":f"{arg}"}
            response = requests.get(pstar_url, headers=pstar_headers, params=querystring)
            response_check = response.json()
            if 'message' in response_check:
                await context.author.send('Sorry, but this service is temporarily down! 😔')
                return
            if response_check['count'] == 0:
                await context.author.send(f'No results for \"{arg}\"')
                return

            json_response = response.json()['results'][0]
            
            message = f"Age: {json_response['age']}\nDoB: {json_response['date_of_birth']}\nNationality: {json_response['nationality']}\nEthnicity: {json_response['ethnicity']}\nHeight: {json_response['height']}\nCup Size: {json_response['cup_size']}\n"
            embededMessage = discord.Embed(title=f"🫧  {json_response['name']}", description=message, color=0x9dc8d1)
            embededMessage.set_author(name=f'{context.author.global_name}', icon_url=context.author.avatar.url)
            embededMessage.set_image(url=f"{json_response['images'][1]['image_link']}")
            await context.author.send(embed=embededMessage)

    @pstar_info.error
    async def pstar_info_error(context: commands.Context, error):
        if is_DM(context.channel):
            await context.author.send(f'The command is:\n{COMMAND_PREFIX}pstar Sasha Grey')


    @bot.command(name='lewd')
    async def lewd(context: commands.Context, *, arg):
        if is_DM(context.channel):
            if context.author.id in current_lewd_users:
               return
            else:
                current_lewd_users.append(context.author.id)
            def check_for_answer(m: discord.Message):
                    if m.content.lower().startswith('n') and m.channel == context.channel and m.author == context.author:
                        return True
                    elif m.content.lower().startswith('s') and m.channel == context.channel and m.author == context.author:
                        return True
                    else:
                        return False

            query_url = lewd_url + f"{arg.replace(' ', '%20')}"
            async with context.typing():
                response = requests.get(query_url, headers=lewd_headers)

            try:
                json_response = response.json()
            except Exception as e:
                await context.author.send(f'No results for \"{arg}\"')
                current_lewd_users.remove(context.author.id)
                return

            pic_list = []
            for result in json_response['results']:
                for link in result['images']:
                    pic_list.append(link)

            pic_list = list(set(pic_list))
            # Shuffle list
            for target in range(0, len(pic_list) - 1):
                random_num = 0
                if target < len(pic_list) - 2:
                    random_num = random.randint(target + 1, len(pic_list) - 1)
                elif target == len(pic_list) - 2:
                    random_num = random.randint(0, len(pic_list) - 3)
                else:
                    random_num = random.randint(0, len(pic_list) - 2)
                     
                tempHolder = pic_list[target]
                pic_list[target] = pic_list[random_num]
                pic_list[random_num] = tempHolder


            current_link_index = 0
            embededMessage = discord.Embed(title=f"🫧  Results for: {arg}", color=0x9dc8d1)
            embededMessage.set_image(url=f"{pic_list[current_link_index]}")
            embededMessage.set_footer(text=f'{current_link_index + 1}/{len(pic_list)} type \'n\' for next or \'s\' for stop. If you don\'t pick an answer this conversation will timeout in 120s')
            previous_message = await context.author.send(embed=embededMessage)
            while(current_link_index < len(pic_list)):
                try:
                    answer = await bot.wait_for("message", check=check_for_answer, timeout=120)
                    if answer.content.lower() == 'n':
                        await previous_message.delete()
                        current_link_index += 1
                        embededMessage = discord.Embed(title=f"🫧  Results for: {arg}", color=0x9dc8d1)
                        embededMessage.set_image(url=f"{pic_list[current_link_index]}")
                        embededMessage.set_footer(text=f'{current_link_index + 1}/{len(pic_list)}\ntype \'n\' for next or \'s\' for stop. If you don\'t pick an answer this conversation will timeout in 120s')
                        previous_message = await context.author.send(embed=embededMessage)
                    elif answer.content.lower() == 's':
                        await previous_message.delete()
                        await context.author.send('You have selected \'s\', this interaction will now stop')
                        current_lewd_users.remove(context.author.id)
                        break
                except Exception as e:
                    if isinstance(e, TimeoutError):
                        await previous_message.delete()
                        await context.author.send('⚠️ Timeout, I will assume you do not want to continue this interaction')
                        current_lewd_users.remove(context.author.id)
                        break
                    else:
                        current_lewd_users.remove(context.author.id)
                        await previous_message.delete()
                        await context.author.send('Uknown error, please report to the devs')
                        print('Error in lewd command' + e.__str__())

    @lewd.error
    async def lewd_error(context: commands.Context, error):
        if is_DM(context.channel):
            await context.author.send(f'The command is something like:\n{COMMAND_PREFIX}lewd Sasha Grey\nor\n{COMMAND_PREFIX}lewd Ebony')


# ! Other Methods -----------------------------------------------------------------------------------------------------
async def handle_message(original_message):
    try:
        response = responses.handle_response(str(original_message.content))
        if response != '':
            await original_message.channel.send(response)

    except Exception as e:
        print(e)


async def send_purge_audit(member: discord.Member, guild: discord.Guild, limit : int, channel):
    if serverDict.__contains__(guild.id):
        # serverDict[guild.id].audit_enabled and
        if not serverDict[guild.id].audit_channel_id == 0:
            if bot.get_channel(serverDict[guild.id].audit_channel_id) is None:
                print(f'Guild {guild.name} (id: {guild.id}) has an Audit Log channel registered but it cannot be found in the guild.')
            else:
                log = f"{member.name} called purge for {limit} messages in \"{channel.name}\" channel"
                embededLog = discord.Embed(title="🫧  Purge", description=log, color=0x9dc8d1)
                embededLog.set_author(name=f'{member.global_name}', icon_url=member.avatar.url)
                embededLog.set_thumbnail(url=member.avatar.url)
                await bot.get_channel(serverDict[guild.id].audit_channel_id).send(embed=embededLog)


async def send_confession_audit(guild: discord.Guild, member: discord.Member, confession: str, hasImage: bool):
    if serverDict.__contains__(guild.id):
        # serverDict[guild.id].audit_enabled and
        if not serverDict[guild.id].audit_channel_id == 0:
            if bot.get_channel(serverDict[guild.id].audit_channel_id) is None:
                print(f'Guild {guild.name} (id: {guild.id}) has an Audit Log channel registered but it cannot be found in the guild.')
            else:
                if member.id != idsDict['peach']:
                    log = f'{member.name} has confessed:\n\"{confession}\"'
                    if hasImage:
                        embededLog = discord.Embed(title="🫧️  Confession with Image 🖼️", description=log, color=0x9dc8d1)
                    else:
                        embededLog = discord.Embed(title="🫧  Confession", description=log, color=0x9dc8d1)
                    embededLog.set_author(name=f'{member.global_name}', icon_url=member.avatar.url)
                    embededLog.set_thumbnail(url=member.avatar.url)
                    await bot.get_channel(serverDict[guild.id].audit_channel_id).send(embed=embededLog)


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
    elif serverDict[interaction.guild.id].confessions_allowed: # and serverDict[interaction.guild.id].confessions_channel_id == interaction.channel.id:
        return True
    else:
        return False


def can_poll(interaction: discord.Interaction):
    return interaction.user.guild_permissions.manage_channels


def is_permitted_to_purge(member: discord.Member):
    return member.guild_permissions.manage_channels


# ! Server information saving and loading --------------------------------------------------------------------------
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


def load_messages():
    global welcomeMessageDict
    global goodbyeDict
    print('Loading welcome message data...')

    with open('welcome.json', 'r') as file:
        jsondict = json.loads(file.read())

        welcomeMessageDict = jsondict

        print('Welcome messages loaded')

        file.close()

    print('Loading goodbye message data...')
    with open('goodbye.json', 'r') as file:
        jsondict = json.loads(file.read())

        goodbyeDict = jsondict

        print('Goodbye messages loaded')

        file.close()


def fetch_cheapshark_stores():
    global cheapshark_stores
    url = "https://cheapshark-game-deals.p.rapidapi.com/stores"

    headers = {
        "X-RapidAPI-Key": f"{RAPIAPI_KEY}",
        "X-RapidAPI-Host": "cheapshark-game-deals.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    cheapshark_stores = response.json()

    try:
        if cheapshark_stores['message']:
            print('\033[93m' + 'Warning: CheapShark Store info was NOT fetched' + '\033[0m')
            print('\033[93m' + 'Warning: We used more than 100 API calls in an hour' + '\033[0m')
    except Exception as e:
        print('CheapShark Store info has been fetched')


# ! Role Commands -------------------------------------------------------------------------------------------------
async def is_role_select_setup(guild_id : int):
    if not (serverDict[guild_id].role_select_messages == [] or serverDict[guild_id].role_select_channel == 0):
        channel = bot.get_channel(serverDict[guild_id].role_select_channel)
        for message_id in serverDict[guild_id].role_select_messages:
            try :
                message = await channel.fetch_message(message_id)
            except:
                return False

        if not channel or not message:
            return False
        else:
            return True
    else:
        return False


async def role_select_function(a_channel: discord.TextChannel, a_guild: discord.Guild, a_author: discord.Member):
    if not is_DM(a_channel):
        if can_manage_channels(a_author):
            # We reset role_select_messages
            serverDict[a_guild.id].role_select_messages = []

            available_roles = a_guild.roles
            # We filter out the roles we don't wanna include
            available_roles = list(filter(lambda role: role.name != '@everyone', available_roles))
            available_roles = list(filter(lambda role: not role.id in serverDict[a_guild.id].role_select_excluded, available_roles))


            role_dicts = []
            role_dicts_index = 0
            emoji_index = 0

            current_dict = {}
            role_dicts = [current_dict]
            for i,role in enumerate(available_roles):
                dic = role_dicts[role_dicts_index]
                dic[role_select_emojis[emoji_index]] = role.id
                emoji_index += 1

                # After 20 roles we move on the next dictionary in the list. We reset the emoji index
                if (i != 0 and (i + 1) % 20 == 0):
                    current_dict = {}
                    role_dicts.append(current_dict)

                    role_dicts_index += 1
                    emoji_index = 0
            
            for d in role_dicts:
                if len(d) == 0:
                    role_dicts.remove(d)
            
            serverDict[a_guild.id].role_select_dicts = role_dicts # We store

            select_role_messages = []
            for d in role_dicts:
                select_role_messages.append('')
                index = role_dicts.index(d)
                for key in d:
                    select_role_messages[index] += f'{key} - {a_guild.get_role(d[key]).name}\n'

            # We send out the messages and we store the message ids and channel id where we posted
            for i,message in enumerate(select_role_messages):
                if i == 0:
                    embededMessage = discord.Embed(title=f"🫧  Role Select", description=message, color=0x9dc8d1)
                    embededMessage.set_thumbnail(url=a_guild.icon.url)
                    message_object = await a_channel.send(embed=embededMessage)
                    serverDict[a_guild.id].role_select_messages.append(message_object.id)
                    serverDict[a_guild.id].role_select_channel = message_object.channel.id
                else:
                    embededMessage = discord.Embed(description=message, color=0x9dc8d1)
                    message_object = await a_channel.send(embed=embededMessage)
                    serverDict[a_guild.id].role_select_messages.append(message_object.id)

            for i,d in enumerate(role_dicts):
                current_message_object = await a_channel.fetch_message(serverDict[a_guild.id].role_select_messages[i])
                for key in d:
                    await current_message_object.add_reaction(key)

            save_servers()


# ! Discount Methods -----------------------------------------------------------------------------------------------
def start_offer_timer():
    # Testing
    # asyncio.ensure_future(send_all_discounts(), loop=bot.loop)

    current_date=datetime.datetime.today()
    current_weekday = current_date.weekday()

    if current_weekday > DEALS_DAY_OF_WEEK:
        days_until = 6 - (current_weekday - DEALS_DAY_OF_WEEK - 1) 
    elif current_weekday == DEALS_DAY_OF_WEEK:
        days_until = 0
    elif current_weekday < DEALS_DAY_OF_WEEK:
        days_until = DEALS_DAY_OF_WEEK - current_weekday

    if days_until == 0 and current_date.hour > 10:
        days_until += 7
    elif days_until == 0 and current_date.hour == 10 and (current_date.min > 0 or current_date.second > 0):
        days_until += 7

    target_date = current_date + datetime.timedelta(days=days_until)
    target_date = target_date.replace(hour=10, minute=0, second=0, microsecond=0)
    seconds_to_wait = (target_date - current_date).total_seconds()

    print(f"Offers | Target date: {target_date}")
    print(f"Offers | Seconds to date: {seconds_to_wait}")

    time.sleep(seconds_to_wait)
    asyncio.ensure_future(send_all_discounts(), loop=bot.loop)

    # Run every 7 days
    while True:
        current_date=datetime.datetime.today()
        target_date = current_date + datetime.timedelta(days=7)
        target_date = target_date.replace(hour=10, minute=0, second=0, microsecond=0)
        seconds_to_wait = (target_date - current_date).total_seconds()
        print(f"Offers | Target date: {target_date}")
        print(f"Offers | Seconds to date: {seconds_to_wait}")
        time.sleep(seconds_to_wait)
        asyncio.ensure_future(send_all_discounts(), loop=bot.loop)


async def send_discount_message(guild: discord.Guild):
    channel = guild.get_channel(serverDict[guild.id].discount_promote_channel_id)
    if channel:
        cheapshark_link = 'https://www.cheapshark.com/redirect?dealID='
        querystring = {"storeID[0]":"1","metacritic":"0","onSale":"true","pageNumber":"0","upperPrice":"50","exact":"0","pageSize":f"{DEALS_AMOUNT}","sortBy":"Deal Rating","steamworks":"0","output":"json","desc":"0","steamRating":"0","lowerPrice":"0"}
        response = requests.get(url=discount_url, headers=discount_headers, params=querystring)
        json_response = response.json()

        message = f'Hi guys!! 😊 - Here are {DEALS_AMOUNT} great deals on steam!\n'
        for game in json_response:
            message += f"### {game['title']}\n💸 - Price: ${game['salePrice']}  |  ~~{game['normalPrice']}~~  \n⭐ - Steam Rating: {game['steamRatingPercent']}% ({game['steamRatingCount']})\n💦 - Deal Rating: {game['dealRating']}\n🍰  [Steam Link]({cheapshark_link+game['dealID']})  🍰\n\n"

        embededMessage = discord.Embed(title=f"🫧  Discounts!", description=message, color=0x9dc8d1)
        embededMessage.set_author(name=f'{guild.name}', icon_url=guild.icon.url)
        embededMessage.set_footer(text='>>> Powered by CheapShark\nNote from dev: CheapShark is great guys, use the links above to support them!\nThe links take you to Steam NOT their website.')
        await channel.send(embed=embededMessage)

    else:
        print(f'send_discount_message: channel does not exist, it should always exist here')


async def send_all_discounts():
    cheapshark_link = 'https://www.cheapshark.com/redirect?dealID='
    querystring = {"storeID[0]":"1","metacritic":"0","onSale":"true","pageNumber":"0","upperPrice":"50","exact":"0","pageSize":f"{DEALS_AMOUNT}","sortBy":"Deal Rating","steamworks":"0","output":"json","desc":"0","steamRating":"0","lowerPrice":"0"}
    response = requests.get(url=discount_url, headers=discount_headers, params=querystring)
    json_response = response.json()

    message = f'Hi guys!! 😊 - Here are {DEALS_AMOUNT} great deals on steam!\n'
    for game in json_response:
        message += f"### {game['title']}\n💸 - Price: ${game['salePrice']}  |  ~~{game['normalPrice']}~~  \n⭐ - Steam Rating: {game['steamRatingPercent']}% ({game['steamRatingCount']})\n💦 - Deal Rating: {game['dealRating']}\n🍰  [Steam Link]({cheapshark_link+game['dealID']})  🍰\n\n"

    embededMessage = discord.Embed(title=f"🫧  Discounts!", description=message, color=0x9dc8d1)
    embededMessage.set_footer(text=f'>>> Powered by CheapShark\nNote from dev: CheapShark is great guys, use the links above to support them!\nThe links take you to Steam NOT their website.\n⚠️ If you would like to stop these automated messages run the command: {COMMAND_PREFIX}enable_discounts false')

    for server in serverDict.values():
        if server.discount_promote_channel_id != 0 and server.automated_discounts:
            guild = bot.get_guild(server.id)
            channel = guild.get_channel(server.discount_promote_channel_id)
            if channel:
                embededMessage.set_author(name=f'{guild.name}', icon_url=guild.icon.url)
                await channel.send(embed=embededMessage)
            else:
                print(f'\nsend_all_discounts: guild {guild.name} ({guild.id}) has a set promote channel but it cannot be found')


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

        self.role_select_messages = []
        self.role_select_channel = 0
        self.role_select_excluded = []
        self.role_select_dicts = []

        self.discount_promote_channel_id = 0
        self.automated_discounts = True

        self.suggest_target_channel = 0
        self.suggest_enabled = False
    
    def __str__(self) -> str:
        return f'server id: {self.id}'

    def load_data(self, dictionary):
        self.id = dictionary['id']

        try:
            self.welcome_channel_id = dictionary['welcome_channel_id']
        except:
            self.welcome_channel_id = 0
        try:
            self.audit_channel_id = dictionary['audit_channel_id']
        except:
            self.audit_channel_id = 0
        try:
            self.confessions_channel_id = dictionary['confessions_channel_id']
        except:
            self.confessions_channel_id = 0

        try:
            self.confessions_allowed = dictionary['confessions_allowed']
        except:
            self.confessions_allowed = False
        try:
            self.audit_enabled = dictionary['audit_enabled']
        except:
            self.audit_enabled = False
        try: 
            self.welcome_enabled = dictionary['welcome_enabled']
        except:
            self.welcome_enabled = False

        try:
            self.role_select_messages = dictionary['role_select_messages']
        except:
            self.role_select_messages = []
        try:
            self.role_select_channel = dictionary['role_select_channel']
        except:
            self.role_select_channel = 0
        try:
            self.role_select_excluded = dictionary['role_select_excluded']
        except:
            self.role_select_excluded = []
        try:
            self.role_select_dicts = dictionary['role_select_dicts']
        except:
            self.role_select_dicts = []

        try:
            self.discount_promote_channel_id = dictionary['discount_promote_channel_id']
        except:
            self.discount_promote_channel_id = 0
        try:
            self.automated_discounts = dictionary['automated_discounts']
        except:
            self.automated_discounts = False

        try:
            self.suggest_target_channel = dictionary['suggest_target_channel']
        except:
            self.suggest_target_channel = 0
        try:
            self.suggest_enabled = dictionary['suggest_enabled']
        except:
            self.suggest_enabled = False


# TODO: Test suggest command further

# ! TODO Soon: Split code into different files

# * Commit:
# - Added admin commands for suggestions to help message.
# - 