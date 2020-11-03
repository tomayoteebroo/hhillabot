# hhillabot

# this work is extended from CodeSammich code:
https://github.com/CodeSammich/discord-bot

# i know the coding is bad, clumsy, , but it works, im lazy, 

# extra new feature:
- u now no nid to manually !2 or !3 to change the phase, it change automatically using simple image library (PIL ImageGrab, cv2)
- can run on windows 10 instead of linux, just install python and some other stuff

# what changes compared to CodeSammich:
- updated some depreciated discord.py function (not fully)

# how it works:
- detect the pixel color at 30% 2nd bar
- detect the pixel color at 20% 3rd bar
- then change timer automatically

# please be note that after a few FMA will got delay due to server latency
# please note that this only works on 1366*768 resolution due to that pixel position i set

# okay before you do all the steps, install this:
- python
- some python related library
- i think you need to download espeak
- i dont know what else you need download and pip install, will update this section later

# steps to make it work on your windows 10:
- first go do all the discord dev portal bot thingy create a bot then invite to your server
- of course clone or download this repository
- copy the bot token to secret_key.txt
- start menu -> type 'cmd' -> right click command prompt -> run as administrator
- cd into your this folder
- run 'python app.py'
- wait for bot to log in
- ok make sure you are an admin role or mod in your own discord server
- make sure you yourself join any voice call
- type '!start' in any text channel
- the timer has started, go kill the b****
- note that you need to enter '!start' immediately after your party leader enter heretic hilla else the timer will off
- after you finished (or failed) type '!stop' to stop the bot

# it didnt work? okay i dont know maybe make an issue, or ask in my reddit post, i will try to answer. 

# type '!4' after you win
# type '!5' after you all die out
# for fun
