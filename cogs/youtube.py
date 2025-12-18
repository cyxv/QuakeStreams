import json
import pprint
import requests
import time
from discord.ext import commands

invidious_instance = "inv.perditum.com"

def get_channel_videos(channel_id: str):
    req = requests.get(f"https://{invidious_instance}/api/v1/channels/{channel_id}/videos")
    pprint.pp(json.loads(req.text))

class YouTube(commands.Cog, name="youtube"):
    def __init__(self, client):
        self.client = client

async def setup(client):
    await client.add_cog(YouTube(client))

if __name__ == "__main__":
    pass