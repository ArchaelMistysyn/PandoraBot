import discord
import multiprocessing
import pandorabot
import eleuiabot
import battleengine
import vouchbot
import logging

logging.getLogger('discord').setLevel(logging.WARNING)
logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)


if __name__ == '__main__':
    processes = [multiprocessing.Process(target=pandorabot.run_discord_bot),
                 # multiprocessing.Process(target=eleuiabot.run_discord_bot),
                 multiprocessing.Process(target=vouchbot.run_discord_bot),
                 multiprocessing.Process(target=battleengine.run_discord_bot)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
