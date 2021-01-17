# This is a Discord bot that allows for more IRC-like moderation
# TODO:
# 1) Implement actual functionality to mute and unmute after time passes
# 2) Implement a totally arbitrary point system that people can assign to others
# 3) Only allow certain roles to use certain commands (moderator, verified, etc.)

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

    # Voting system
    if message.content.startswith('++') or message.content.startswith('--'):
        # Silly slice to get all server members
        member_list = [str(i).split('#')[0].lower() for i in client.get_all_members()]
        # Index between command/vote and given username
        space_index = message.content.find(' ')
        vote_sign = message.content[:2]
        vote_amount = message.content[2:space_index]
        vote_member = message.content[space_index + 1:]

        # Try/Except block that ensures valid input
        try:
            vote_amount = int(vote_amount)

            if vote_member not in member_list:
                await message.channel.send("There is no user in this server by that name.")

            elif vote_sign == '--':
                if vote_amount < 1:
                    raise ValueError
                else:
                    await message.channel.send(f'Vote amount: -{vote_amount}.\nVoted for: {vote_member}.')

            elif vote_sign == '++':
                if vote_amount < 1:
                    raise ValueError
                else:
                    await message.channel.send(f'Vote amount: {vote_amount}.\nVoted for: {vote_member}.')

            else:
                await message.channel.send("Something went wrong.")

        except ValueError:
            await message.channel.send("Invalid vote amount.")


if __name__ == "__main__":
    client.run(config.TOKEN)
