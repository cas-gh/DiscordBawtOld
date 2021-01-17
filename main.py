# This is a Discord bot that allows for more IRC-like moderation
import discord
import config

# Sets the intents on startup so bot can read all users in the server
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


# Login
@client.event
async def on_ready():
    print('Login successful as {0.user}'.format(client))


# Message event handler
@client.event
# Ignores messages sent by the bot itself
async def on_message(message):
    if message.author == client.user:
        return

    # Ridiculous slice picks out just the discord username from messy generator
    # and forces lower case for ease of comparison later
    if message.content.startswith(',mute'):
        member_list = [str(i).split('#')[0].lower() for i in client.get_all_members()]

        # Try/Except block checking for ValueErrors and valid mute command
        try:
            if message.content[5] == ' ':
                raise ValueError
            elif message.content[6] == ' ':
                mute_time = int(message.content[5])
                mute_member = message.content[7:].lower()
            else:
                mute_time = int(message.content[5:7])
                mute_member = message.content[8:].lower()

            if mute_time > 60 or mute_time < 1:
                await message.channel.send("That is not a valid temporary mute time.")
            elif mute_member not in member_list:
                await message.channel.send("There is no user in this server by that name.")
            else:
                await message.channel.send(f'Muted {mute_member} for {mute_time} minutes.')

        except ValueError:
            await message.channel.send("Invalid Command.")


if __name__ == "__main__":
    client.run(config.TOKEN)
