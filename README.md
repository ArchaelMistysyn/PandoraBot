# PandoraBot
Pandora Bot Repository
PandoraPortal.ca is the website for this bot. The bot is accessible from the discord server linked on the website.

run instructions:
sudo apt install screen (Install screen to run the session)
pip3 install -r requirements.txt (to install requirements)
screen -S bot_session (start session)
python3 pandorabot.py (to run the bot)
screen -r bot_session (reattach to the session. ctrl + c to terminate the process while attached)
screen -ls (check sessions)
screen -S bot_session -X quit (kill the session)