import discord
from discord.ext import commands
import os

intents = discord.Intents().default()
client = commands.Bot(command_prefix='!', intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


if __name__ == "__main__" :
    client.load_extension("cogs.Music")
    client.run(DISCORD_TOKEN)