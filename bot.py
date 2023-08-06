import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.ext.commands import MissingRequiredArgument
import responses
import pytz
import random

# Tokens
TOKEN = 'MTEzNjAwNjU5NjMyNjA3MjMzMQ.GL7u5C.z6vZiaRGZIAzmWPrVkjuuB_nhMl6TGm2v-plyQ'
KRAYON_TOKEN = "MTEzNzU0NDIxNTAzNTkxNjM5OQ.G6rfMa.Vp5tPyCOuZE5Jp0RBIQHc_uIRLzvmStPlujSxY"

# IDs
GUILD_ID = 1133876820555595816
AUDIT_CHANNEL_ID = 1136087223947767909
CONFESSIONS_CHANNEL_ID = 1136107904425001021
WELCOME_CHANNEL_ID = 1133919325544251453
vibesID = 339550706342035456

COMMAND_PREFIX = '!'
CONFESSIONS_ALLOWED = True


def start_bot():
    myIntents = discord.Intents.default()
    myIntents.message_content = True
    myIntents.dm_messages = True
    myIntents.members = True
    # client = discord.Client(intents=myIntents)
    client = commands.Bot(COMMAND_PREFIX, intents=myIntents, help_command=None)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await client.change_presence(status=discord.Status.online, activity=discord.Game('games! 🍰'))

    @client.event
    async def on_audit_log_entry_create(entry):
        channel = entry.guild.get_channel(AUDIT_CHANNEL_ID)
        time = entry.created_at.astimezone(tz=pytz.timezone('America/New_York')).isoformat()

        print('\nServer log created:')
        print(
            f" Server Nickname: {'No nickname' if (type(entry.user) is discord.user.User or type(entry.user) is None) else entry.user.nick} User: {entry.user.global_name} ID:{entry.user.name} | Action: {entry.action.name} | Date: {time.split('T')[0]} Time: {time.split('T')[1].split('.')[0]} EST\n")

        oldLog = f"\n Server Nickname: \"{'No nickname' if (type(entry.user) is discord.user.User or type(entry.user) is None) else entry.user.nick}\"\n User: \"{entry.user.global_name}\"\n ID: \"{entry.user.name}\" \n Action: {entry.action.name} \n Date: {time.split('T')[0]}\n  Time: {time.split('T')[1].split('.')[0]} EST"
        newLog = f"{entry.user.name}  {entry.action.name} \n{time.split('T')[0]} at {time.split('T')[1].split('.')[0]} EST"
        embededLog = discord.Embed(title="🫧", description=newLog, color=0x9dc8d1)

        # await channel.send(f":bookmark:\n> Server Nickname: \"{'No nickname' if (type(entry.user) is discord.user.User or type(entry.user) is None) else entry.user.nick}\"\n> User: \"{entry.user.global_name}\"\n> ID: \"{entry.user.name}\" \n> Action: {entry.action} \n> Date: {time.split('T')[0]}\n > Time: {time.split('T')[1].split('.')[0]} EST")
        await channel.send(embed=embededLog)

    @client.command(name='repeat')
    async def repeat(context, *, arg):
        if not isinstance(context.channel, discord.DMChannel):
            await context.send(arg)

    @repeat.error
    async def repeat(context, error):
        if not isinstance(context.channel, discord.DMChannel):
            await context.channel.send(f'The command should go:\n{COMMAND_PREFIX}repeat I will repeat this!')

    @client.command(name='confess')
    async def confess(context, *, arg):
        if isinstance(context.channel, discord.DMChannel):
            if CONFESSIONS_ALLOWED:
                if client.get_guild(GUILD_ID).get_member(context.author.id) is None:
                    await context.author.send('You are not a member of our server! 😔')

                else:
                    confession = str(arg)
                    if '@everyone' in confession:
                        await context.author.send('Please don\'t mention everyone on confessions')
                    else:
                        embededConfession = discord.Embed(title="🫧  By Anonymous Member!", description=confession,
                                                          color=0x9dc8d1)
                        await context.author.send('Your confession was posted on the Confessions channel! 🫧')
                        # await client.get_channel(CONFESSIONS_CHANNEL_ID).send("### 🫧  By Anonymous Member!\n>>> " + confession)
                        await client.get_channel(CONFESSIONS_CHANNEL_ID).send(embed=embededConfession)
            else:
                await context.author.send('Sorry, confessions are temporarily disabled')
        else:
            await context.channel.send('Sorry, but you need to tell me that in a DM')

    @confess.error
    async def confess(context, error):
        print(COMMAND_PREFIX + 'confess: ' + str(error))
        if isinstance(context.channel, discord.DMChannel):
            if CONFESSIONS_ALLOWED:
                if client.get_guild(GUILD_ID).get_member(context.author.id) is None:
                    await context.author.send('You are not a member of our server! 😔')
                else:
                    await context.author.send(
                        'The command is:\n' + COMMAND_PREFIX + 'confess I confess that I am a good cake!')
            else:
                await context.author.send('Sorry, confessions are temporarily disabled')
        else:
            await context.channel.send('Sorry, but you need to tell me that in a DM')

    @client.command(name='standoff')
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
                    await context.channel.send(
                        f'The usage of the command is:\n' + COMMAND_PREFIX + 'standoff @user\n or (this following bit has not been implemented yet)\n' + COMMAND_PREFIX + 'standoff @user @user')
                    return

                if player2.startswith('&'):
                    player2 = str.removeprefix(player2, '&')

                player2 = int(player2)
                temp = client.get_guild(GUILD_ID).get_member(player2)
                if temp.nick is None:
                    player2 = temp.global_name
                else:
                    player2 = temp.nick

                if random.randint(1, 10) <= 5:
                    await context.channel.send(f'# 💥👉      👈🤠\n> **{player1}** wins!')

                else:
                    await context.channel.send(f'# 🤠👉      👈💥\n> **{player2}** wins!')
            else:
                await context.channel.send(f'The usage of the command is:\n' + COMMAND_PREFIX + 'standoff @user\n')
        else:
            await context.author.send(f'Sorry, you can\'t use that command here. Please, do it in the server')

    @client.command(name='help')
    async def help(context):
        if not isinstance(context.channel, discord.DMChannel):
            await context.send(
                f'>>> 🍰 Hi! My current commands are\n**{COMMAND_PREFIX}repeat** I will repeat anything you want to say!\n**{COMMAND_PREFIX}standoff** Want to do a cowboy stand off against a friend? 🤠\nand if you DM me...\n**{COMMAND_PREFIX}confess** Your confession will be sent to the #Confessions Channel!\nIf you need help with individual commands type the command!')

    @client.event
    async def on_command_error(context, error):
        if isinstance(error, CommandNotFound):
            print("Command not found!")
        elif isinstance(error, MissingRequiredArgument):
            print("Missing argument!")
        else:
            raise error

    @client.event
    async def on_member_join(member):
        print(member.global_name + ' joined the server')

        welcome_messages = [
            f"Hello __{member.global_name}__, welcome to our server! I hope you have a great time here! 🍰",
            f"Hi __{member.global_name}__, welcome! I hope you make lots of friends here! 🍰",
            f"Welcome __{member.global_name}__, do you also like cake!? 🍰",
            f"Please everyone welcome __{member.global_name}__! 🍰",
            f"Heyo __{member.global_name}__, welcome to our server! 🍰"]

        await client.get_guild(GUILD_ID).get_channel(WELCOME_CHANNEL_ID).send(
            '### ' + welcome_messages[random.randint(0, len(welcome_messages) - 1)])

    @client.event
    async def on_message(message):
        # Checks if a DM is a from a guild member
        if client.get_guild(GUILD_ID).get_member(message.author.id) is None:
            await message.channel.send('You are not a member of our server! 😔')
            return

        # Ignores Bot's messages
        if message.author == client.user:
            return

        # Message log
        if not (str(message.content).startswith(f'{COMMAND_PREFIX}confess') and isinstance(message.channel, discord.DMChannel)):
            print(f"\n\"{message.author.global_name}\" / \"{message.author}\" said: \"{str(message.content)}\" in \"{message.channel}\" server: \"{message.guild}\"")

        if (message.author.id == vibesID) and not (str(message.content).startswith(f'{COMMAND_PREFIX}confess')):
            vibesNum = random.randint(0, 100)
            # print('vibesNum is '+ str(vibesNum))
            if (vibesNum < 5):
                await message.channel.send('Shut up vibes')
                print('Vibes was attacked')
                return

        # This actually processes the commands since we overrode on_message()
        await client.process_commands(message)

        # Custom text messages
        if isinstance(message.channel, discord.DMChannel):
            response = responses.handle_dm(message.content)
            if response != '':
                await message.channel.send(response)
        else:
            await answer_message(message)

    # !purge [limit]
    @client.command(name='purge')
    async def purge_channel(context, *args):
        # Test channel ID for krayon: 1098216731111067731
        live_channel_ids: dict = {"Bot-Testing": 1136013944029462538}
        permitted_channels: list = [channel for channel in live_channel_ids.values()]
        channel: discord.TextChannel = context.channel
        if channel.id in permitted_channels:  # Channel check
            limit = int(args[0]) if args else 200  # If user specifies limit, else default to 200
            print(f'Purge command called in channel "{channel.name} for {limit} messages".')
            author: discord.Member = context.author
            if is_permitted_to_purge(author):  # User check
                await channel.purge(limit=limit+1)
        else:
            print(f'Channel "{channel.name}" is not eligible for purging.')

    # Run bot
    client.run(TOKEN)


# Send messages
async def answer_message(original_message):
    try:
        response = responses.handle_response(str(original_message.content))
        if response != '':
            await original_message.channel.send(response)

    except Exception as e:
        print(e)


def is_permitted_to_purge(member: discord.Member):
    permitted_roles = ['Owner', 'Admin', 'Mods']
    member_roles = member.roles
    for role in member_roles:
        if role.name in permitted_roles:
            print(f'User "{member.global_name}" is eligible to purge.')
            return True
    print(f'User "{member.global_name}" is not eligible to purge.')  # TODO: Send in text channel
    return False


"""
    confess
    if isinstance(message.channel, discord.DMChannel):
        if client.get_guild(GUILD_ID).get_member(message.author.id) is None:
            await message.author.send("You are not a member of our server! 😔")

        else:
            temp = message.content
            if (temp.startswith("!confess")):
                text = temp.split(' ', maxsplit=1)
                if len(text) > 1:
                    await message.author.send("Your confession was posted on the Confessions channel!")
                    await client.get_channel(CONFESSIONS_CHANNEL_ID).send("### 🫧  By Anonymous Member!\n>>> " + text[1])
                    await client.get_channel(CONFESSIONS_CHANNEL_ID).send("  Thanks for reading!")
                elif temp == "!confess ":
                    await message.author.send("The command is:\n!confess I confess that I am a good cake!")
                elif temp == "!confess":
                    await message.author.send("The command is:\n!confess I confess that I am a good cake!")
            else:
                await message.author.send("Hi! 👋 To make your confession type !confess followed by your message")
"""

# TODO: Add 3 confessions a day for users
# TODO: Add standoffs for 2 people
# TODO: Add Taymio to always lose
