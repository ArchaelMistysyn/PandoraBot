# PandoraBot
Pandora Bot Repository
PandoraPortal.ca is the website for this bot. The bot is accessible from the discord server linked on the website.

prerequisite installs instructions:
sudo apt install python3-pip (install pip)
sudo apt update (update)
sudo apt install software-properties-common (deadsnakes PPA)
sudo add-apt-repository ppa:deadsnakes/ppa (deadsnakes PPA)
sudo apt install python3.11 python3.11-venv python3.11-dev (virtual environment)
sudo apt install pkg-config (install config for mysql)
sudo apt install libmysqlclient-dev (install lib for mysql)
sudo apt update (update again)
sudo apt install libssl-dev (install missed dependency mysql)
sudo apt install libpq-dev (install missed dependency psycopg2)
pip install --upgrade pip (update pip)

setup instructions:
python3.11 -m venv venv (create virtual environment)
source venv/bin/activate (activate virtual environment)
pip install -r requirements.txt (to install requirements)
sudo apt install screen (Install screen to run the session)
screen -S Pandora (start session)
python main.py (to run the bot)
ctrl+a then d (detatch session)
screen -r #.Pandora (reattach to the session. ctrl + c to terminate the process while attached)
screen -ls (check sessions)
ps aux | grep main.py (check processes)
screen -S Pandora -X quit (kill the session)