# This is a Discord bot that allows for more IRC-like moderation
# TODO:
# 1) Implement actual functionality to mute and unmute after time passes.
# 2) Create a '++help' command that lists possible commands
# 3) Create some sort of way to rate-limit voting

import sqlite3
from sqlite3 import Error
import config
import discord
from discord.utils import get

# Sets the intents on startup so bot can read all users in the server
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


# SQLite function definitions

# Opens the connection to the sql db
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


# Creates a new member
def create_member(conn, project):
    sql = ''' INSERT INTO members(name,points) 
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()

    return cur.lastrowid


# Updates a member's info
def update_member(conn, member):
    sql = ''' UPDATE members
              SET points = points + ?
              WHERE name = ?'''

    cur = conn.cursor()
    cur.execute(sql, member)
    conn.commit()


# Executes update_member
def update_main(vote_amount, vote_member):
    database = "pysqlite_test.db"

    conn = create_connection(database)
    with conn:
        update_member(conn, (vote_amount, vote_member))


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
    if message.content.startswith(',mute') and get(message.author.roles, name="Moderator"):
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
        if get(message.author.roles, name="Registered Voter"):
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
                    if vote_amount < 1 or vote_amount > 100:
                        raise ValueError
                    else:
                        await message.channel.send(f'Vote amount: -{vote_amount}.\nVoted for: {vote_member}.')
                        update_main(vote_amount, vote_member)

                elif vote_sign == '++':
                    if vote_amount < 1 or vote_amount > 100:
                        raise ValueError
                    else:
                        await message.channel.send(f'Vote amount: {vote_amount}.\nVoted for: {vote_member}.')
                        update_main(vote_amount, vote_member)

                else:
                    await message.channel.send("Something went wrong.")

            except ValueError:
                await message.channel.send("Invalid vote amount.")
        else:
            await message.channel.send("You don't have permission to do that.")


if __name__ == "__main__":
    client.run(config.TOKEN)
