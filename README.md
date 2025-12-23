# QuakeStreams
### To use:
- Install requirements with `pip install -r requirements.txt`
- Make a folder called secrets with 4 files. channel_id_twitch.txt, twitch_client_id.txt, twitch_client_secret.txt and token.txt
  - In twitch_client_id.txt and twitch_client_secret.txt, paste your Client ID and Client Secret respectively from your Twitch application (can find/create at https://dev.twitch.tv/console/apps)
  - In token.txt, paste your Discord bot token (can find/create at https://discord.com/developers/applications/)
  - In channel_id_twitch.txt, paste the ID of the Discord channel you want notifications to go to
- Make a file called user_list.txt in the same directory as main.py and enter Twitch names for all streamers you want notifications for (each on their own line)
- Run main.py