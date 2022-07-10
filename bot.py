import sys
import traceback
import os

import logging
import logbook
from logbook import Logger, StreamHandler
from logbook.compat import redirect_logging


import discord
from discord.ext import commands
from discord.ext.commands import Bot, when_mentioned_or

from utils import config_file
from utils.checks import is_owner

import glob


plugins = ['plugins.fight', 'plugins.avatar']

intents = discord.Intents().all()

class WFight(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=when_mentioned_or(config_file["discord"]["command_prefix"]),
                description="Lets get it on!", intents=intents)

        redirect_logging()
        StreamHandler(sys.stderr).push_application()
        self.game_running = False
        self.game_starting = False
        self.logger = Logger("WFight")
        self.logger.level = getattr(logbook, config_file.get("log_level","INFO"), logbook.INFO)
        logging.root.setLevel(self.logger.level)

    async def on_ready(self):
        self.logger.info("Logged in as: {0.user.name}\nBot ID: {0.user.id}".format(self))

    '''async def on_command_error(self, exception, ctx):
        print("IN ERROR")
        print(exception)
        print(exception.message)
        if isinstance(exception, commands.errors.CommandNotFound):
            return
        if isinstance(exception, commands.errors.CheckFailure):
            await sel.send_message(ctx.message.channel, "Missing required permissions")
            return
    '''

    def run(self):
        for plugin in plugins:
            try:
                self.load_extension(plugin)
                self.logger.info("{0} has been loaded".format(plugin))
            except discord.ClientException:
                self.logger.critical("{0} is missing setup function!".format(plugin))
            except ImportError as IE:
                self.logger.critical(IE)
        super().run(config_file["discord"]["token"])


if __name__ == '__main__':
    bot = WFight()
    bot.remove_command('help')
    bot.run()

