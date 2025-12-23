import discord
import json
import math
import os
import pprint
import requests
import time
from discord.ext import commands, tasks

data = {
    "invidious_instance": None,  # need a working invidious instance with public API
    "time_on_load": None,
    "discord_channel": None,
    "tracked_channels": None
}

with open("secrets/channel_id_youtube.txt") as channel_id_file:
    data["discord_channel"] = int(channel_id_file.read())

def get_channel_videos(channel_id: str) -> list[dict]:
    req = requests.get(f"https://{data["invidious_instance"]}/api/v1/channels/{channel_id}/videos")
    return req.json()["videos"]

def create_upload_embed(video_data: dict) -> discord.Embed:
    embed = discord.Embed(
        title=data["title"],
        description=f"{data["author"]} published a video on YouTube!",
        url=f"https://youtube.com/watch?v={data["videoId"]}"
    )
    embed.set_author(name=data["author"], url=f"https://youtube.com{data["authorUrl"]}")
    return embed

class YouTube(commands.Cog, name="youtube"):
    def __init__(self, client):
        self.client = client

    @tasks.loop(seconds=30)
    async def do_update(self):
        if not os.path.exists("posted_videos.txt"):
            open("posted_videos.txt", "w+").close()
        with open("posted_videos.txt", "r") as posted_videos_file:
            posted_videos = [x.strip() for x in posted_videos_file.readlines()]
        
        for channel in data["tracked_channels"]:
            recent_videos = get_channel_videos(channel)[:5]
            for video in recent_videos:
                if video["published"] > data["time_on_load"] and video["videoId"] not in posted_videos:
                    self.client.get_channel(data["discord_channel"]).send(embed=create_upload_embed(video))

        
    @commands.Cog.listener()
    async def on_ready(self):
        data["time_on_load"] = math.floor(time.time())
        with open("youtube_channels.txt", "r") as tracked_channels_file:
            data["tracked_channels"] = [x.strip() for x in tracked_channels_file.readlines()]
        
        self.do_update.start()

async def setup(client):
    await client.add_cog(YouTube(client))

if __name__ == "__main__":
    pass