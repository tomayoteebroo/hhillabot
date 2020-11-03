# Inspired by ThiefGMS and his insight/mp3 files into the Verus Hilla fight
# Special Thanks to MapleStory.gg and catboy on Discord for their contributions and initial hosting!
#
# Boss Timer Mechanics:
#     16s from start to hourglass timer (29:44)
#     First interval 150s (27:14, etc.)
#     When HP hits 25% on the second HP bar, interval becomes 125s
#     When HP hits 20% on the third HP bar, interval becomes 100s
#
# Possible Future Features:
# - Allow input of current clock time for soul split
#    - This is especially helpful after a phase change
#
# NOTE:
# This bot may not always be 100% accurate to the real fight due to unresolvable latency issues
# with both the Nexon and Discord servers. There may be a variance of 0-5s from actual game.

# Work with Python 3.6
import discord
#from discord.ext import commands
import time
import datetime
import asyncio
from ctypes.util import find_library
import pyttsx3
import os

import random
import cv2
import numpy as np
import imutils
from skimage.measure import compare_ssim
from PIL import ImageGrab
import win32gui
import win32api
import win32con

from discord.ext import commands, tasks
from discord.ext.commands import Bot
from itertools import cycle
import ctypes, time
from array import *

# client being run on the Discord servers for guilds (colloquially "servers") to connect to
client = discord.Client()
#client = commands.Bot(command_prefix = 'sudo ')

# then try finding the secret_key.txt file for the key (for local deployments)
token_file = open('secret_key.txt', 'r')
TOKEN = token_file.read() # make a file called secret_key.txt and replace with key
TOKEN = TOKEN.rstrip()

# open and load OPUS library for voice chat support and transcoding
opuslib = find_library('opus') # Linux-based function
discord.opus.load_opus(opuslib)

# free TTS engine for Python e-Speak (on Linux) for "soul split at xx:xx"
engine = pyttsx3.init()
engine.setProperty('rate', 100)
engine.setProperty('volume', 1)

# Concurrent Server Data Structures
# global dicts w/ information for each bot instance in each server/guild (Discord's term for server)
# keys are: vc.server.id (unique per server)
ffmpeg_players = {} # audio currently playing, prevents overlapping audio (see bot_speak)
phases = {} # boss timer phases (150s, 125s, 100s)
vcs = {} # voice channels the bot is currently in, derived from client.voice_clients (see find_bot_voice_client)
vcstate = None 
game_hwnd = 0

def mainLoop():
    while(True):
        time.sleep(1)
        print('main loop')

    return

@client.event
async def on_ready():
    '''
    Is run when program is run, to connect bot with Discord server specified in Developer's Portal API
    Bot needs to be authorized properly and initialized on the Dev Portal.
    Once completed, servers/guilds can begin connecting to the bot.
    '''
    log('Logged in as:')
    log(client.user.name)
    log(client.user.id)
    log('------')
    
    global game_hwnd
    windows_list = []
    toplist = []
    def enum_win(hwnd, result):
        win_text = win32gui.GetWindowText(hwnd)
        windows_list.append((hwnd, win_text))
    win32gui.EnumWindows(enum_win, toplist)
    for (hwnd, win_text) in windows_list:
        if "MapleStory" in win_text:
            # print('maplestory', hwnd, win_text)
            game_hwnd = hwnd

async def timer(vc, interval, boss_time):
    global phases
    while True:
        # boss_time first starts at 1784 seconds, or 29:44
        log('Timer has started at boss time: {} in the {} channel in {} server.'\
            .format(short_minutes_and_seconds(boss_time + interval), vc.channel, vc.guild))
        
        # text to speech
        # 60s warning
        log('Starting {}s timer on the {} channel in {} server.'\
            .format(interval, vc.channel, vc.guild))
        await asyncio.sleep(interval - 60)
        if phases[vc.guild.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break
        
        bot_speak(vc, 'a60seconds.mp3')
        
        # 30s warning
        await asyncio.sleep(30)
        if phases[vc.guild.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break

        bot_speak(vc, 'a30seconds.mp3')
        
        # 15s warning
        await asyncio.sleep(15)
        if phases[vc.guild.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break

        bot_speak(vc, 'a15seconds.mp3')
        
        # 5s warning
        await asyncio.sleep(10)
        if phases[vc.guild.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break

        bot_speak(vc, 'a5seconds.mp3')
        
        # 0s soul split announcement
        await asyncio.sleep(5)
        if phases[vc.guild.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break
        
        # Screenshot and Check
        position = win32gui.GetWindowRect(game_hwnd)
        # print(position)
        # x, y, w, h = position
        # x1 = x + 374
        # y1 = y + 380
        # position1 = (x1, y1, x1+110, y1+190)

        screenshot = ImageGrab.grab(position)
        # screenshot.show()
        screenshot = np.array(screenshot)
        img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        if phases[vc.guild.id] == 1:
            color = img[33, 552]
            print('ifphasesequal==1', color)
            # if color[0] == 34 and color[1] == 221 and color[2] == 187:    # Original
            if color[0] == 16 and color[1] == 103 and color[2] == 87:     # Shadow
                print('87 103 16 phase 2 yellow colour detected at 30% ')
                phases[vc.guild.id] = 2
        elif phases[vc.guild.id] == 2:
            color = img[33, 476]
            print('ifphasesequal==2', color)
            # if color[0] == 17 and color[1] == 136 and color[2] == 85:    # Original
            if color[0] == 8 and color[1] == 63 and color[2] == 40:     # Shadow
                print('40 63 8 phase 3 green colour detected at 20% ')
                phases[vc.guild.id] = 3

        # update internal representation of boss clock
        mins_and_secs = minutes_and_seconds(boss_time)
        
        # generate wav file to say "soul split at xx:xx"
        # unfortunately, this uses a really creepy low voice, but I really can't find
        # anything better for free. Google TTS is amazing, but requires real $$$
        soul_split_at_xx_xx = '\"soul. split. at. ' + mins_and_secs + '"'
        generate_speech_wav(vc, soul_split_at_xx_xx)
        bot_speak(vc, '{}soulsplit'.format(vc.guild.id)) # play the correct vc/server's file
        # bot_speak(vc, '{}soulsplit.wav'.format(vc.guild.id)) # play the correct vc/server's file


        
        # if phase changed, start timer again with less time
        if phases[vc.guild.id] == 1:
            await timer(vc, 150, boss_time - 150)
            break
        if phases[vc.guild.id] == 2:
            await timer(vc, 125, boss_time - 125)
            break # so previous thread of timer stops and returns
        elif phases[vc.guild.id] == 3:
            await timer(vc, 100, boss_time - 100)
            break

@client.event
async def ping(message):
    print('ping')
    if message.content.find("!hello") != -1:
        await message.channel.send('Pong!')

# responding to an external user message
@client.event
async def on_message(message):
   
    id = client.get_guild(739905077342371950)
    channels = ["bot"]

    if str(message.channel) in channels:
        if message.content.find("!hello") != -1:
            await message.channel.send("hi")
        elif message.content == "!users":
            await message.channel.send(f"""# of Members: {id.member_count}""")

    # so the dicts can always be accessed, even by async calls
    global phases 
    global vcs
    global vcstate


    # message sender's parameters
    author = message.author # or sender
    # channel = message.channel
    server = message.guild
    call = author.voice.channel # author's current voice channel
    
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!help'):
        # !help command, including usage tips
        msg = '\nCommands include:'
        msg += '\n     !start makes bot join voice chat (use upon entering)'
        msg += '\n     !2 for phase 2 (use after 1.75 HP bars have depleted)'
        msg += '\n     !3 for phase 3 (use after 2.75 HP bars have depleted)'
        msg += '\n     !stop to disconnect the bot.'
        await message.channel.send(msg)
       
    if message.content.startswith('!start') or message.content.startswith('!join') or message.content.startswith('!fight'):
        # Joins the voice chat of the person who used the command
        
        #voice_client = discord.utils.get(client.voice_clients, guild=server)
        
        print('vcstate before: ', vcstate)
        if vcstate is None:
        #if not client.is_voice_connected(server):
            # if the bot is not in a voice channel yet
            if call != None:
                # if sender is in a voice channel, join the vc
                try:
                    vc = await call.connect()
                    vcstate = vc
                    print('vcstate after: ', vcstate)
                    #vc = await client.join_voice_channel(call)

                    # tell the party the timer has begun in the chat
                    msg = 'Verus Hilla timer has started in the {} channel.'.format(vc.channel)
                    await message.channel.send(msg)
                    #await client.send_message(message.channel, msg)
                
                    # (re-)initialize the phase/vc for that server
                    phases[vc.guild.id] = 1
                    vcs[vc.guild.id] = vc

                    # play the start.mp3 file, which says "hilla fight starting, good luck"
                    bot_speak(vc, 'start.mp3')
                
                    # wait for 16s after entry to skip opening cutscene, as the announcement is being made
                    await asyncio.sleep(16)

                    if phases[vc.guild.id] != 0:
                        # if bot did not disconnect during sleep                    
                        # tell the party the fight has started in chat
                        # Bot may send this message multiple times if it is restarted before 16s sleep is over
                        # Does not influence timer or voice chat, they're just ghost threads that will die
                        # once !stop is calling again.
                        msg = 'Fight has started. Starting first 150s timer.'
                        msg += '\nIf you see this message multiple times, ignore it.'
                        await message.channel.send(msg)

                        await timer(vc, 150, 1634) # start timer 150s at 29:4
                except asyncio.TimeoutError:
                    msg = 'Cannot connect to voice channel, request timed out. Try checking your channel/bot permissions.'
                    await message.channel.send(msg)
            else:
                # if sender is not in VC, don't join and ask the sender to please join
                msg = 'Please join a voice channel first and re-use the command for bot to join.'
                await message.channel.send(msg)
        else:
            msg = 'Verus Hilla Bot is already in a voice channel.'
            await message.channel.send(msg)

        log('!start called by {} on {} server has finished executing'.format(author, server))

    # this should only be used at 2.2 bars left
    if message.content.startswith('!2'):
        if vcstate != None:
        #if client.is_voice_connected(server):
            # if bot is in a vc, find it
            vc = find_bot_voice_client(server.id)

            #if author in client.get_role(server.id).members:
            if author.guild_permissions.administrator or author_in_vc(author, vc):
                # if the author is an admin or is in the vc with the bot
                phases[vc.guild.id] = 2               # set the phase for sender's server
                bot_speak(vc, '125.mp3')               # say interval is now 125s
                msg = 'Split interval now 125 seconds. Will start after next soul split.'
            else:
                msg = 'You are not in the voice chat or an administrator.'
        else:
            # bot is not in a VC
            msg = 'Bot is not currently in a voice chat'

        await message.channel.send(msg)
        log('!2 called by {} on {} server has finished.'.format(author, server))

    # this should only be used at 1.2 bars left
    if message.content.startswith('!3'):
        if vcstate != None:     # if bot is in a vc
            vc = find_bot_voice_client(server.id) # find the vc

            if author.guild_permissions.administrator or author_in_vc(author, vc):
                # if the author is an admin or is in the vc with the bot
                phases[vc.guild.id] = 3              # set the phase for sender's server
                bot_speak(vc, '100.mp3')              # say interval is now 100s
                msg = 'Split interval now 100 seconds. Will start after next soul split.'
            else:
                msg = 'You are not in the voice chat or an administrator.'
        else:
            # if bot is not in a vc
            msg = 'Bot is not in a voice chat'

        # respond to the sender
        await message.channel.send(msg)
        log('!3 called by {} on {} server has finished.'.format(author, server))


    if message.content.startswith('!4'):
        if vcstate != None:     # if bot is in a vc
            vc = find_bot_voice_client(server.id) # find the vc

            if author.guild_permissions.administrator or author_in_vc(author, vc):
                # if the author is an admin or is in the vc with the bot
                bot_speak(vc, 'down_hhhilla.mp3')              # say interval is now 100s
                msg = 'Congratulations! You downed Hard Heretic Hilla!'
            else:
                msg = 'You are not in the voice chat or an administrator.'
        else:
            # if bot is not in a vc
            msg = 'Bot is not in a voice chat'

        # respond to the sender
        await message.channel.send(msg)
        log('!3 called by {} on {} server has finished.'.format(author, server))


    if message.content.startswith('!5'):
        if vcstate != None:     # if bot is in a vc
            vc = find_bot_voice_client(server.id) # find the vc

            if author.guild_permissions.administrator or author_in_vc(author, vc):
                # if the author is an admin or is in the vc with the bot
                bot_speak2(vc, ['yousuck.mp3','youlosechinese.mp3','wacao.mp3'])              # say interval is now 100s
                msg = 'yousuck youlose wacao'
            else:
                msg = 'You are not in the voice chat or an administrator.'
        else:
            # if bot is not in a vc
            msg = 'Bot is not in a voice chat'

        # respond to the sender
        await message.channel.send(msg)
        log('!3 called by {} on {} server has finished.'.format(author, server))

    # disconnect from server
    if message.content.startswith('!stop') or message.content.startswith('!leave'):
        # find the voice chat corresponding to the message and disconnect
        if vcstate != None:     # if bot is in a vc
            vc = find_bot_voice_client(server.id) # find the vc

            if author.guild_permissions.administrator or author_in_vc(author, vc):
                # if the author is an admin or is in the vc with the bot
                await vc.disconnect()                 # disconnect from voice channel
                phases[vc.guild.id] = 0
                del vcs[vc.guild.id]                 # delete the voice channel from dict
                vcstate = None
                msg = 'Disconnected from {}'.format(vc.channel)
                if author.guild_permissions.administrator:
                    msg += ' by administrator {}'.format(author) 
            else:
                msg = 'You are not in the voice chat or an administrator.'
        else:
            msg = 'Bot is not in a voice chat.'

        # respond to the sender
        await message.channel.send(msg)
        log('!stop called by {} on {} server has finished.'.format(author, server))

def author_in_vc(author, vc):
    '''
    Is the author in the vc?

    Inputs: String author
    Returns: True/False
    '''
    try:
        # need to compare ids and not just channel names because names are not unique
        # (e.g. two channels can have the same name)
        log('{} is in the {} channel. The bot is in the {} channel.'.format(author, author.voice.voice_channel, vc.channel))

        if author.voice.voice_channel.id == vc.channel.id:
            return True
    except AttributeError: # NoneType object has no attribute 'id'
        # this will happen if someone outside of the vc tries to use the command 
        pass
            
    return False
        
def find_bot_voice_client(server_id):
    '''
    Updates the voice chats (vcs) list with current voice connections
    and returns the voice chat in the server with server_id.
    
    Inputs: Unique id of Discord server/guild (vc.server.id or message.server.id)
    Returns: the voice chat object corresponding to the bot's server
    '''
    global vcs # so the dict can always be accessed, even by async calls
    # update vcs dict with current vc connections iterable
    for vc in client.voice_clients:
        # add vc to vcs dict if not already there
        if vc.guild.id not in vcs.keys():
            vcs[vc.guild.id] = vc
            
    return vcs[server_id]
    
def minutes_and_seconds(seconds):
    '''
    Converts seconds to minutes and seconds (xx minutes xx seconds)

    Inputs: String seconds
    Returns: String representation with minutes and seconds
    '''
    mins = int(seconds / 60)
    secs = seconds % 60
    mins_and_secs = str(mins) + " minutes " + str(secs) + " seconds"
    return mins_and_secs

def short_minutes_and_seconds(seconds):
    '''
    Converts seconds to minutes and seconds (xx:xx format)

    This is mostly used for convenient logging.

    Inputs: String seconds
    Returns: String representation with minutes and seconds
    '''
    mins = int(seconds / 60)
    secs = seconds % 60
    mins_and_secs = str(mins) + ":" + str(secs)
    return mins_and_secs

def generate_speech_wav(vc, text):
    '''
    Given a text string, generate a WAV file of a voice speaking the text.

    Input: String text
    Output: WAV file in the current directory with server.id as name
    '''
    # vc.server.id + soulsplit.wav file name to allow concurrent servers to speak
    # espeak_command = 'espeak -m {} -v mb-en1 --stdout > {}soulsplit.wav'.format(text, vc.guild.id)
    espeak_command = 'espeak -w{}soulsplit -m {} -v mb-en1 '.format(vc.guild.id, text)
    log(espeak_command)
    os.system(espeak_command) # generates soulsplit.wav
    log("TTS generation of {}soulsplit.wav is successful".format(vc.guild.id))
    
def log(line):
    '''
    Logs date and time to the console along with input.

    Input: String line
    Output: Datetime and line printed
    '''
    date_str = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print('[{}] {}'.format(date_str, line))

def bot_speak2(vc, mp3_name):
    global ffmpeg_players # so the dict can always be accessed, even by async calls
    if not vc.is_connected:
        return
    if vc.guild.id in ffmpeg_players:
        log('stopped {}'.format(vc.guild))
        vc.stop()
        ffmpeg_players.pop(vc.guild.id, None)
    log('playing {} in {}'.format(mp3_name, vc.guild))
    i = 0
    def repeat(i):
        if i >= len(mp3_name):
            return
        ffmpeg_players[vc.guild.id] = vc.play(discord.FFmpegPCMAudio(mp3_name[i]), 
            after=lambda e: plusone(i))
        vc.is_playing()
    def plusone(i):
        i+=1
        repeat(i)
    repeat(i)

def bot_speak(vc, mp3_name):
    '''
    Allows the bot to play audio, or speak, into the voice channel.

    Retains a mappiung of voice sessions to players.
    If a session has a voice line in progress, terminate it before playing the next one.

    Input: String mp3_name
    Output: MP3 file played by bot in the corresponding voice channel
    '''
    global ffmpeg_players # so the dict can always be accessed, even by async calls

    if not vc.is_connected:
        return

    # for the respective concurrent server, stop the current audio player
    if vc.guild.id in ffmpeg_players:
        log('stopped {}'.format(vc.guild))
        vc.stop()
        #ffmpeg_players[vc.guild.id].stop()
        ffmpeg_players.pop(vc.guild.id, None)

    # start a new audio player for the new audio and save in the global ffmpeg_players dict for concurrency
    log('playing {} in {}'.format(mp3_name, vc.guild))
    ffmpeg_players[vc.guild.id] = vc.play(discord.FFmpegPCMAudio(mp3_name), 
        after=lambda e: log('speech is done in the {} channel of {}.'.format(vc.channel, vc.guild)))
    #ffmpeg_players[vc.guild.id] = vc.create_ffmpeg_player(mp3_name,
    #    after=lambda: log('speech is done in the {} channel of {}.'.format(vc.channel, vc.guild)))
    vc.is_playing()
    #ffmpeg_players[vc.guild.id].start()

# run the client and connect to Discord's servers
# this needs to run before servers/guilds can connect successfully
client.run(TOKEN)
