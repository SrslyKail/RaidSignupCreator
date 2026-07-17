# RaidSignupCreator
I wrote this Python script to automate the creation of the signups for my FF14 raid group from [raid-helper.xyz](https://raid-helper.xyz/). We use to manually create the signups, which led to incorrect settings and/or people forgetting to do the creation, which led to missed raids and a sad group, so I automated it.

At the moment, it's made for my group specifically, but you can use it so long as you follow the quirks.

The run.sh file can also be used if you want to schedule the creation of raid events. Doing so will create a virtual environment, if needed, and install the required packages before execution.

# Assumptions

1. The raid title is formatted as "(fight_name) - (other information) in order to properly extract the fight name. You need to manually update the fights name, once cleared, for the system to keep working.
2. This is for Final Fantasy 14 Extreme raids; as such the value of 8 members being required is hard-coded, and the template ID for the raid-helper is hard-coded.
3. The raid-helper API version is v4

# Requirements

1. You have the Raid-Helper bot in your discord server
2. You have a Raid-Helper API key(which the bot can give you)
3. You have Developer Mode enabled in Discord, in order to get access to your discord user ID, the Server ID for your group, and the channel ID for the bot to post in
4. You install the required modules via `pip install -r requirements.txt`. It is recommended you also create a virtual environment.

# .Env 
To use this bot, you'll need a `.env` located at the project root; that is, in the same location as the RaidSignupCreator.py file. You can copy the `example.env` included in this repo as a starting point. Each line is 1 argument, and they **must** be formatted as `KEY=VALUE`.

- `API_KEY` is the raid-helper API key. The bot can give it to you.
- `SERVER_ID` is the Server ID for Discord.
- `CHANNEL_ID` is the Channel ID for Discord.
- `DISCORD_ID` is the Discord ID of the user you want listed as the leader.
- `RAID_DATES` is a list of dictionaries that include the `weekday`, `hour`, and `minute` keys. This is used to get the date and time of the next raid(s) to be created.
- `WEEKLY` is a flag used to select if you want to create a single event, or create all the events in the `RAID_DATES` variable. If `WEEKLY` is set to `false`, and there are multiple values in the `RAID_DATES` variable, only the first value will be used.

# Future upgrades
- Make the template type and member requirement to be set via the .env file; this would allow for this same script to be used for other games or other content types.
- Allow for the delimiter between `Raid Name` and the other information to be set via the .env file.
- Organize the Raid code into its own module so it doesn't cutter up the main file.
- Update from requirements.txt to pyproject.toml
- Add logging so we can avoid print statements and more gracefully capture/record exceptions for easier debugging.
- Convert ConfigFactory to a static class