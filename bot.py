#!/usr/bin/env python3
import asyncio
import base64
from datetime import datetime
from datetime import timezone
import os
import re
import signal
import sys

import discord
from discord import Game
from discord.enums import ChannelType

#--- Config ---
TOKEN = ''
USE_LOCALTIME = True
LOG_DIR = 'logs'
MAX_MESSAGES = 7500
#--------------

def clean_filename(string):
    return re.sub(r'[/\\:*?"<>|\x00-\x1f]', '', string)

def make_filename(message):
    if message.channel.type == ChannelType.text:
        time = datetime.now()
        folderdate = time.strftime('%F')
        return "{}/{}/{}/ChatLog/{}.txt".format(LOG_DIR, folderdate, message.server.id, message.channel.id)
    elif message.channel.type == ChannelType.private:
        time = datetime.now()
        folderdate = time.strftime('%F')
        return "{}/{}/DM/{}.txt".format(LOG_DIR, folderdate, message.channel.user.id)
    elif message.channel.type == ChannelType.group:
        time = datetime.now()
        folderdate = time.strftime('%F')
        return "{}/{}/DM/{}.txt".format(LOG_DIR, folderdate, message.channel.id)

def make_message(message):
    time = datetime.now()
    timestamp = time.strftime('[%H:%M:%S]')
    author = "<{}#{} ({})>".format(message.author.name, message.author.discriminator, message.author.id)
    content = message.clean_content
    attachments = ' '.join([attachment['url'] for attachment in message.attachments])
    return("{} {} {} {}".format(timestamp, author, content, attachments))

def write(filename, string):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'a', encoding='utf8') as file:
        print(string, file=file)

client = discord.Client()

@client.event
async def on_member_join(member):
    time = datetime.now()
    timestamp = time.strftime("[%H:%M:%S]")
    folderdate = time.strftime("%Y-%m-%d")
    filename = "{}/{}/{}/MemberJoinLeave.txt".format(LOG_DIR, folderdate, member.server.id)
    string = "{} <{}#{} ({})> Join Server".format(timestamp, member.name, member.discriminator, member.id)
    write(filename, string)

@client.event
async def on_member_remove(member):
    time = datetime.now()
    timestamp = time.strftime("[%H:%M:%S]")
    folderdate = time.strftime("%Y-%m-%d")
    filename = "{}/{}/{}/MemberJoinLeave.txt".format(LOG_DIR, folderdate, member.server.id)
    string = "{} <{}#{} ({})> Leave Server".format(timestamp, member.name, member.discriminator, member.id)
    write(filename, string)

@client.event
async def on_message(message):
    filename = make_filename(message)
    string = make_message(message)
    write(filename, string)

@client.event
async def on_message_edit(_, message):
    filename = make_filename(message)
    string = make_message(message)
    write(filename, string)

@client.event
async def on_voice_state_update(member_before, member_after):
    server = member_after.server
    voice_channel_before = member_before.voice_channel
    voice_channel_after = member_after.voice_channel
    if voice_channel_before == voice_channel_after:
        return
    if voice_channel_before == None:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        string = "{} <{}#{} ({})> Connect : {}".format(timestamp, member_after.name, member_after.discriminator, member_after.id, voice_channel_after.name)
    else:
        if voice_channel_after == None:
            time = datetime.now()
            timestamp = time.strftime("[%H:%M:%S]")
            string = "{} <{}#{} ({})> Leave : {}".format(timestamp, member_after.name, member_after.discriminator, member_after.id, voice_channel_before.name)
        else:
            time = datetime.now()
            timestamp = time.strftime("[%H:%M:%S]")
            string = "{} <{}#{} ({})> Move : {} to {}".format(timestamp, member_after.name, member_after.discriminator, member_after.id, voice_channel_before.name, voice_channel_after.name)
    try:
        time = datetime.now()
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/ServerVoiceLog.txt".format(LOG_DIR, folderdate, member_after.server.id)
        write(filename, string)

    except discord.DiscordException as exception:
        return

@client.event
async def on_member_update(member_before, member):
    if member.nick and not member_before.nick:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/MemberNickNameLog.txt".format(LOG_DIR, folderdate, member.server.id)
        string = "{} <{}#{} ({})> Change NickName : {}".format(timestamp, member.name, member.discriminator, member.id, member.nick)
        write(filename, string)

    elif member_before.nick and not member.nick:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/MemberNickNameLog.txt".format(LOG_DIR, folderdate, member.server.id)
        string = "{} <{}#{} ({})> Remove NickName : {} -> {}".format(timestamp, member.name, member.discriminator, member.id, member_before.nick, member.name)
        write(filename, string)

    elif member.nick != member_before.nick:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/MemberNickNameLog.txt".format(LOG_DIR, folderdate, member.server.id)
        string = "{} <{}#{} ({})> Change NickName : {} -> {}".format(timestamp, member.name, member.discriminator, member.id, member_before.nick, member.nick)
        write(filename, string)

    new_roles = set(member.roles) - set(member_before.roles)
    old_roles = set(member_before.roles) - set(member.roles)
    if new_roles:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/MemberRoleLog.txt".format(LOG_DIR, folderdate, member.server.id)
        string = "{} <{}#{} ({})> Roles Get : {r}".format(timestamp, member.name, member.discriminator, member.id, r = ', '.join(str(r) for r in new_roles))
        write(filename, string)

    if old_roles:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/MemberRoleLog.txt".format(LOG_DIR, folderdate, member.server.id)
        string = "{} <{}#{} ({})> Roles Remove: {r}".format(timestamp, member.name, member.discriminator, member.id, r = ', '.join(str(r) for r in old_roles))
        write(filename, string)

    if member.status != member_before.status:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/MemberStatusLog.txt".format(LOG_DIR, folderdate, member.server.id)
        string = "{} <{}#{} ({})> Change Status : {} -> {}".format(timestamp, member.name, member.discriminator, member.id, member_before.status, member.status)
        write(filename, string)

    if member.avatar_url != member_before.avatar_url:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/MemberAvatarLog.txt".format(LOG_DIR, folderdate, member.server.id)
        string = "{} <{}#{} ({})> Change Avatar : {} -> {}".format(timestamp, member.name, member.discriminator, member.id, member_before.avatar_url, member.avatar_url)
        write(filename, string)

    if member.game != member_before.game:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/MemberPlayLog.txt".format(LOG_DIR, folderdate, member.server.id)
        string = "{} <{}#{} ({})> Change Playing : {} -> {}".format(timestamp, member.name, member.discriminator, member.id, member_before.game, member.game)
        write(filename, string)

@client.event
async def on_server_update(server_before, server):
    if server.name != server_before.name:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/ServerNameLog.txt".format(LOG_DIR, folderdate, server.id)
        string = "{} Change Server Name : {} -> {}".format(timestamp, server_before.name, server.name)
        write(filename, string)

    if server.owner != server_before.owner:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/ServerOwnerLog.txt".format(LOG_DIR, folderdate, server.id)
        string = "{} Change Server Owner : <{}#{} ({})> -> <{}#{} ({})>".format(timestamp, server_before.owner.name, server_before.owner.discriminator, server_before.owner.id, server.owner.name, server.owner.discriminator, server.owner.id)
        write(filename, string)

    if server.icon_url != server_before.icon_url:
        time = datetime.now()
        timestamp = time.strftime("[%H:%M:%S]")
        folderdate = time.strftime("%Y-%m-%d")
        filename = "{}/{}/{}/ServerIconLog.txt".format(LOG_DIR, folderdate, server.id)
        string = "{} Change Server Icon : {} -> {}".format(timestamp, server_before.icon_url, server.icon_url)
        write(filename, string)

@client.event
async def on_ready():
    await client.change_presence(game=Game(name="BigBrother is watching"))
    print('------')
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN, bot=True, max_messages=MAX_MESSAGES)
