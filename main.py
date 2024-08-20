# General imports
import discord
# Bot imports
import pandorabot
# Logging imports
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)


if __name__ == '__main__':
    try:
        pandorabot.run_discord_bot()
    except KeyboardInterrupt:
        print("Bot stopped due to KeyboardInterrupt.")
