import discord
from discord.ext import commands
import requests

from time import sleep


class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["addrole","ar"], pass_context=True)
    async def add_role(self, ctx, arg):
        members = await ctx.guild.fetch_members(limit=None).flatten()
        role_id = int(arg)
        role = ctx.guild.get_role(role_id)
        for member in members:
            #print([role.id for role in member.roles])
            if role_id not in [role.id for role in member.roles]:
                await member.add_roles(role, reason='New Default', atomic=True)
                print(member.name)
                #sleep(1)



def setup(bot):
    bot.add_cog(Role(bot))
