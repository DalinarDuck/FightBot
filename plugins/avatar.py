import discord
from discord.ext import commands
from discord import Message

import requests


class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["avatar","av"], pass_context=True)
    @commands.has_permissions(administrator=True)
    async def custom_avatar(self, ctx):
        url = ctx.message.content.split(' ')[1]
        try:
            r = requests.get(url)
            with open('avatar.png', 'wb') as f:
                f.write(r.content)
            with open('avatar.png', 'rb') as f:
                ava = f.read()
                await ctx.bot.user.edit(avatar=ava)
        except:
            print('error')


def setup(bot):
    bot.add_cog(Avatar(bot))
