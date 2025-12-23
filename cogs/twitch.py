import discord
import math
import os
import requests
import time
from datetime import datetime, timezone
from discord.ext import commands, tasks

twitch_data = {
    "channel_id": None,
    "client_id": None,
    "client_secret": None,
    "twitch_api_key": None,
    "currently_live": list()
}

# not really a secret but it's convenient to have it here OK
with open("secrets/channel_id_twitch.txt") as channel_id_file:
    twitch_data["channel_id"] = int(channel_id_file.read())

with open("secrets/twitch_client_id.txt") as client_id_file:
    twitch_data["client_id"] = client_id_file.read()

with open("secrets/twitch_client_secret.txt") as client_secret_file:
    twitch_data["client_secret"] = client_secret_file.read()

def refresh_twitch_api():
    api_req = requests.post("https://id.twitch.tv/oauth2/token", {
        "client_id": twitch_data["client_id"],
        "client_secret": twitch_data["client_secret"],
        "grant_type": "client_credentials"
    })
    twitch_data["twitch_api_key"] = api_req.json()["access_token"]
    print(f"Twitch API key refreshed: {twitch_data["twitch_api_key"]}")

def twitch_api_call(endpoint: str, params: dict) -> dict:
    req = requests.get(f"https://api.twitch.tv/helix/{endpoint}", params=params, headers={"Authorization": f"Bearer {twitch_data["twitch_api_key"]}", "Client-Id": twitch_data["client_id"]})
    if req.status_code == 401:
        refresh_twitch_api()
        return twitch_api_call(endpoint, params)
    
    return req.json()["data"]
        
def get_users(user_names: list):
    return twitch_api_call("users", {"login": user_names})

def get_streams(channel_names: list):
    return twitch_api_call("streams", {"user_login": channel_names})

def create_live_embed(stream_data: dict, user_data: dict):
    username = stream_data["user_name"]
    embed = discord.Embed(
        title=stream_data["title"],
        url=f"https://twitch.tv/{username}"
    )
    embed.set_author(name=f"{username} is now live on Twitch!", url=f"https://twitch.tv/{username}", icon_url=user_data["profile_image_url"])
    embed.set_image(url=f"{stream_data["thumbnail_url"].format(width=1920, height=1080)}?t={math.floor(time.time())}")
    embed.add_field(name="Game", value=stream_data["game_name"])
    embed.set_footer(text=str(datetime.now(timezone.utc)).split(".")[0])

    return embed

class Twitch(commands.Cog, name="twitch"):
    def __init__(self, client):
        self.client = client
        
    @tasks.loop(seconds=10)
    async def do_update(self):
        with open("user_list.txt", "r") as user_list_file:
            user_list = [x.strip() for x in user_list_file.readlines()]

        streams = get_streams(user_list)
        users = get_users(user_list)

        for probably_live_channel in twitch_data["currently_live"]:
            if probably_live_channel not in [x["user_login"] for x in streams]:
                twitch_data["currently_live"].remove(probably_live_channel)
                print(f"{probably_live_channel} went offline")

        for channel in streams:
            if channel["user_login"] not in twitch_data["currently_live"]:
                current_user_data = [x for x in users if x["login"] == channel["user_login"]][0]

                view = discord.ui.View()
                url_button = discord.ui.Button(style=discord.ButtonStyle.url, label="Watch Stream", url=f"https://twitch.tv/{channel["user_login"]}")
                view.add_item(url_button)
                await self.client.get_channel(twitch_data["channel_id"]).send(f"{channel["user_name"]} is now live on Twitch!", embed=create_live_embed(channel, current_user_data), view=view)

                twitch_data["currently_live"].append(channel["user_login"])
        
        with open("currently_live.txt", "w") as currently_live:
            currently_live.writelines([line + "\n" for line in twitch_data["currently_live"]])

    @commands.Cog.listener()
    async def on_ready(self):
        refresh_twitch_api()

        if not os.path.exists("currently_live.txt"):
            open("currently_live.txt", "w").close()
        with open("currently_live.txt", "r") as currently_live:
            twitch_data["currently_live"] = [channel.strip() for channel in currently_live.readlines()]

        self.do_update.start()

async def setup(client):
    await client.add_cog(Twitch(client))