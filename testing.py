import asyncio
import discord
from discord.ext import commands
import youtube_dl
import re


my_intents = discord.Intents.default()
my_intents.message_content = True
my_intents.dm_messages = True
my_intents.members = True
bot = commands.Bot(command_prefix='!',intents=my_intents)


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download= not stream))
        streamUrl = data['formats'][0]['url']
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][1]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename if stream == False else streamUrl, data['title']
    
@bot.command(name='play_song', help='To play song')
async def play(ctx,url):
    server = ctx.message.guild
    voice_channel = server.voice_client
    async with ctx.typing():
        source = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        voice_channel.play(discord.FFmpegPCMAudio(source=source[0]))
        # As The World Caves In - Matt Maltese (Cover by Sarah Cothran)-SqDjQPoJxiw.webm
        trimmed_filename = re.split(r'-\w*(\.webm)$', source[1])[0]
    await ctx.send('**Now playing:** {}'.format(trimmed_filename))


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")
    


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


if __name__ == "__main__" :
    bot.run("MTEzNjcyNzU3ODE0OTkxMjY3Nw.GWdXS2.EfLioGTzaajLwzsZ4TSf4iIsC3B7pqkF_e7z_4")
