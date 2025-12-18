import time
startTime = time.time()

import asyncio
import discord
from discord.ext import commands, tasks

with open("secrets/token.txt", "r") as token_file:
    token = token_file.read()

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(
    command_prefix="!qs ",
    intents=intents
)

@client.event
async def on_ready():
    print(f"QuakeStreams successfully loaded & connected in {round(time.time() - startTime, 4)} seconds.")

extensions = ["cogs.twitch", "cogs.youtube"]
async def load_extensions():
    for extension in extensions:
        try:
            print(f"Loading extension \"{extension}\"")
            await client.load_extension(extension)
        except Exception as e:
            print(f"{extension} failed to load [{e}]")

if __name__ == "__main__":
    asyncio.run(load_extensions())
    client.run(token)