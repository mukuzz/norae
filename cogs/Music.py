import discord
import os
import requests
import youtube_dl
import asyncio
import subprocess

from discord.ext import commands

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

AUDIO_DIR = 'audio/'
AUDIO_FORMAT = 'm4a'


class YouTube:
    '''
    returns youtube id and tittle of the top result for given keywords
    '''
    def search_song(self, keywords:list = None):
        if keywords == None:
            keywords = ["buttercup"]
        query_keys = "+".join(keywords)
        url = "https://www.googleapis.com/youtube/v3/search"
        response = requests.get(url, params={"part":"snippet","maxResults":1,"q":query_keys,"type":"video","key":YOUTUBE_API_KEY})
        result = response.json()
        video_id = result['items'][0]['id']['videoId']
        title = result['items'][0]['snippet']['title']
        print(title)
        return (video_id, title)
    
    '''
    returns the filename of the downloaded song
    '''
    def get_song(self, keywords:list = None):
        video_id, title = self.search_song(keywords)
        video_url = "https://www.youtube.com/watch?v="+video_id
        subprocess.run(['ytmdl', '--url', video_url, '--nolocal', '--skip-meta', '--format', AUDIO_FORMAT, '--download-archive', AUDIO_DIR+'archive', '--output-dir', AUDIO_DIR])
        return title+"."+AUDIO_FORMAT


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
    

    @commands.command(name='join', help='Tells the bot to join the voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
            if ctx.voice_client is None:
                await channel.connect()
            else:
                # move the bot audio to currently joined audio channel of user
                await ctx.voice_client.move_to(channel)

        
    @commands.command(name='leave', help='To make the bot leave the voice channel')
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel.")


    @commands.command(name='play', help='To play song')
    async def play(self, ctx, *args):
        try :
            await self.join(ctx)
            async with ctx.typing():
                filename = YouTube().get_song(args)
                source = AUDIO_DIR + filename
                if ctx.voice_client and ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                ctx.voice_client.play(discord.FFmpegPCMAudio(source))
            await ctx.send('**Now playing:** {}'.format(filename))
        except:
            await ctx.send("Some error occurred.")


    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")
        
    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play command")

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")


def setup(client):
    client.add_cog(Music(client))