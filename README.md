# hhillabot

this work is extended from CodeSammich code: https://github.com/CodeSammich/discord-bot

# extra new feature:
- automatically change phase using image library (PIL ImageGrab, cv2)
- runnable on windows 10

# how it works:
- detect the pixel color at 30% 2nd bar
- detect the pixel color at 20% 3rd bar

# please be note that after a few FMA will got delay due to server latency
# please note that this only works on 1366*768 resolution due to that pixel position i set

# another thing is sometimes there will be announcement bar on top which overlapped the hhilla hp bar, for this i created two color code at line 165, 166, 172, 173, you need to change them accordingly, just comment out 

# install prerequisite:
- python
- some python related library
- i think you need to download espeak
- i dont know what else you need download and pip install
- will update this section later
- need tester / fresh system to test out the requirements

# steps to make it work on your windows 10:
- first go do all the discord dev portal bot thingy create a bot then invite to your server
- clone or download this repository
- copy the bot token to secret_key.txt
- start menu -> type 'cmd' -> right click command prompt -> run as administrator
- cd into your this folder
- run 'python app.py'
- wait for bot to log in
- make sure you are an admin role or mod in your own discord server
- make sure you yourself join any voice call
- type '!start' in any text channel and enter
- the timer has started, go kill the b****
- note that you need to enter '!start' immediately after your party leader enter heretic hilla else the timer will off
- after you finished (or failed) type '!stop' to stop the bot

# it didnt work? make an issue or ask in reddit post, i will try to answer: 
https://www.reddit.com/r/Maplestory/comments/jnrhzf/verus_hilla_timer_discord_bot/

# type '!4' after you win
# type '!5' after you all die out


