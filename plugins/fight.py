import discord
from discord.ext import commands
import requests

import random
from plugins.murders import murders

from utils import database as db

from time import sleep
from PIL import Image, ImageDraw, ImageFont


class Fight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {} #90000001:'bob',2:'frank',3:'joe','111':'boops','1341234':'no name','12345':'Name10','1342345':'Name11','123356345':'Name13','12245245345':'Name14','1232345234545':'Name15','134112345':'Name16','5345612345':'Name17','1746742345':'Name18','123418182735':'Name19'}
        self.player_list = []
        self.next_round = []
        self.owner = None
        self.big = False
        self.delay = 7
        self.canned = False
        self.conn = db.create_connection('stats.db')
        self.message_id = None
        self.channel_id = None
        self.fight_started = False
        self.template = Image.open('./media/template.png')
        self.placeholder = Image.open('./media/placeholder.png')
        self.template_placeholder = Image.open('./media/template_placeholder.png')
        #print('\n'.join(x for x in dir(self.bot)))

    @commands.command(aliases=["makefight","mf"], pass_context=True)
    async def make_fight(self, ctx):
        self.murders = murders.copy()
        if self.bot.game_starting:
            error = await ctx.send("Game in session")
            await error.delete(delay=10)
        else:
            self.bot.game_starting = True
            self.owner = ctx.author.id
            self.channel_id = ctx.channel.id
            self.join_emoji = await ctx.guild.fetch_emoji('945014050067214438')
            self.start_emoji = await ctx.guild.fetch_emoji('945015871607308309')

            with open('./plugins/fightcount','r') as f:
                self.count = f.read().strip()
            self.cur_round = int(self.count)
            self.num = str(self.cur_round) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= self.cur_round % 100 < 20 else self.cur_round % 10, "th")

            #build embed
            embed = discord.Embed(title="The {} Whore Fight!!".format(self.num), description="Welcome to the Whore Fight!\nJoin in by hitting the emote below, start the game with the other one!", color=discord.Color.green())
            embed.set_author(name="The Ring Master")
            embed.set_image(url='https://cdn.discordapp.com/attachments/844059174807797764/944840794332872744/unknown.png')
            #post embed
            self.mess = await ctx.send(embed=embed)
            self.message_id = self.mess.id

            #add reactions
            await self.mess.add_reaction(self.join_emoji)
            await self.mess.add_reaction(self.start_emoji)

            nn = str(self.cur_round + 1)
            with open('./plugins/fightcount','r+') as f:
                f.seek(0)
                f.write(nn)
                try:
                    f.trunicate()
                except:
                    pass


    @commands.command(aliases=["bigfight","bf"], pass_context=True)
    async def big_fight(self, ctx, arg):
        self.big = True
        #print(type(arg))
        if arg == None:
            arg = 50
        else:
            arg = int(arg)
        self.delay = 2
        members = await ctx.guild.fetch_members(limit=None).flatten()
        member_pool = random.sample(members, arg)
        for member in member_pool:
            #print(member.name, member.id)
            self.players[member.id] = member.name
        self.murders = murders.copy()
        if self.bot.game_starting:
            error = await ctx.send("Game in session")
            await error.delete(delay=10)
        else:
            self.bot.game_starting = True
            self.owner = ctx.author.id
            self.channel_id = ctx.channel.id
            self.start_emoji = await ctx.guild.fetch_emoji('945015871607308309')

            with open('./plugins/fightcount','r') as f:
                self.count = f.read().strip()
            self.cur_round = int(self.count)
            self.num = str(self.cur_round) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= self.cur_round % 100 < 20 else self.cur_round % 10, "th")

            #build embed
            embed = discord.Embed(title="The {} Whore Fight!!".format(self.num), description="Welcome to the Whore Fight!\nJoin in by hitting the emote below, start the game with the other one!", color=discord.Color.green())
            embed.set_author(name="The Ring Master", icon_url="https://cdn.discordapp.com/attachments/844059174807797764/944840794332872744/unknown.png")
            embed.set_image(url='https://cdn.discordapp.com/attachments/844059174807797764/944840794332872744/unknown.png')
            #post embed
            self.mess = await ctx.send(embed=embed)
            self.message_id = self.mess.id

            embed = discord.Embed(title="The {} Whore Fight!!".format(self.num), description="We have added {} players to the fight...".format(len(self.players)), color=discord.Color.green())
            embed.set_author(name="The Ring Master", icon_url="https://cdn.discordapp.com/attachments/844059174807797764/944840794332872744/unknown.png")
            #post embed
            self.mess2 = await ctx.send(embed=embed)

            #add reactions
            await self.mess.add_reaction(self.start_emoji)

            nn = str(self.cur_round + 1)
            with open('./plugins/fightcount','r+') as f:
                f.seek(0)
                f.write(nn)
                try:
                    f.trunicate()
                except:
                    pass



    def get_stats(self, players):
        stats = {}
        for player in players:
            data = db.select_player(self.conn, player)
            #print(data)
            if data == []:
                discord_id, wins, kills, died, plays = (player,0,0,0,0)
                db.create_record(self.conn, (player,0,0,0,0))
            else:
                id, discord_id, wins, kills, died, plays = data[0]
            stats[player] = {}
            stats[player]['wins'] = wins
            stats[player]['kills'] = kills
            stats[player]['plays'] = plays
            stats[player]['died'] = plays - wins
        return stats

    def save_stats(self, game_results):
        for k in game_results.keys():
            d = (game_results[k]['wins'], game_results[k]['kills'], game_results[k]['died'], game_results[k]['plays'], k)
            #print(d)
            db.update_stats(self.conn, d)
        self.conn.commit()
        #self.conn.close()
        #self.conn = db.create_connection('stats.db')


    async def play_game(self):
        #set initial settings..
        reroll_count = 0
        game_chan = self.bot.get_channel(self.channel_id)
        stats = self.get_stats(list(self.players.keys()))

        #check if the game is running.. 
        if self.bot.game_running:
            print('game in session')
            await game_chan.send('Game in session')
            return
        else:
            #set running flag
            self.bot.game_running = True

            #build player list
            self.player_list = [self.players[k] for k in self.players.keys()]
            players_remain = (len(self.player_list) + len(self.next_round))

            print('Game Starting now')
            await game_chan.send('Game Starting now')


        #run game based on number of players
        while players_remain > 1:
            #check if we canceled the match
            if self.canned == True:
                print('We ended the game early!')
                break
            if players_remain == 1:
                print('Game Over')
                break
            if len(self.player_list) % 2 == 1:
                sleep(self.delay)
                print('Removing the odd duck')
                victim = random.choice(self.player_list)
                self.player_list.remove(victim)
                embed=discord.Embed(title="Someone was found dead", description="{victim} was discovered hidden in a bush...".format(victim=victim), color=0xff0000)
                embed.set_author(name="The Ring Master")
                embed.add_field(name='Victim',value="__{victim}__ was eleminated".format(victim=victim), inline=True)
                await game_chan.send(embed=embed)
                players_remain = (len(self.player_list) + len(self.next_round))
                continue


            #continue to main game.. this should mean we have at least 2 players left
            name = random.choice(self.player_list)
            victim = random.choice(self.player_list)
            #cant fight yourself...
            while victim == name:
                if reroll_count == 20:
                    print('too many re-rolls')
                    break
                victim = random.choice(self.player_list)
                print('same name, rerolling')
                reroll_count += 1

            if name == victim:
                print('ending game early')
                break

            #pick a murder scenario then remove it
            senario = random.choice(self.murders)
            self.murders.remove(senario)
            #if we are down to 2, reset them :D
            if len(self.murders) < 3:
                self.murders = murders.copy()
                print("refreshed murders")

            #some magic to get their ID
            nid = int(list(self.players.keys())[list(self.players.values()).index(name)])
            vid = int(list(self.players.keys())[list(self.players.values()).index(victim)])

            #get image and build murder card
            n_img = await self.get_image(nid)
            v_img = await self.get_image(vid)

            self.template.paste(n_img, (100,100))
            self.template.paste(v_img, (456,100))
            self.template.save('./media/fight.png',format='png')
            file = discord.File('./media/fight.png', filename='./media/fight.png')

            #update winner kills
            stats[nid]['kills'] += 1

            #update victim plays and dies
            stats[vid]['died'] += 1
            stats[vid]['plays'] += 1

            #add delay for banter...
            sleep(self.delay)
            await game_chan.send("", file=file)

            #remove the two players from the main pool, one for dead, one for winning
            self.player_list.remove(victim)
            self.player_list.remove(name)

            #move up winner
            self.next_round.append(name)

            #if we only have 1 or less players to pick refresh player list
            if len(self.player_list) < 1:
                for x in range(len(self.next_round)):
                    print('-> Re-adding {}'.format(self.next_round[x]))
                    self.player_list.append(self.next_round[x])
                self.next_round = []
                print('Player pool replinished, next round')

            #actually print the results
            print(senario.format(name=name, victim=victim))
            embed=discord.Embed(title="{name} VS {victim}".format(name=name, victim=victim), description=senario.format(name=name, victim=victim), color=0xff0000)
            embed.set_author(name="The Ring Master")
            embed.add_field(name='Victim',value="__{victim}__ was eleminated".format(victim=victim), inline=True)
            if self.big == False:
                embed.add_field(name='{} Players Remian'.format(len(self.player_list) + len(self.next_round)),value="__Players Remaining__\n{}\n{}".format('\n'.join(self.player_list), '\n'.join(self.next_round)), inline=True)
            else:
                embed.add_field(name='{} Players Remian'.format(len(self.player_list) + len(self.next_round)), value="__Players Remaining__\n{}".format(len(self.player_list) + len(self.next_round)), inline=True)
            await game_chan.send(embed=embed)
            players_remain = (len(self.player_list) + len(self.next_round))
            #end of main while


        sleep(6)
        if not self.canned:
            print('did we cancel the game? {}'.format(self.canned))
            winner = ''.join(self.player_list)
            p = int(list(self.players.keys())[list(self.players.values()).index(winner)])
            stats[p]['wins'] += 1
            r_num = random.randint(234562345,9872456543)
            u = await self.bot.fetch_user(p)
            url = u.avatar_url
            kills = stats[p]['kills']
            wins = stats[p]['wins']
            plays = stats[p]['plays']
            embed=discord.Embed(title="Winner Is {}!!".format(winner), description="Winner of the Whore Fight is\n**{}**\n__**STATS**__\n:knife: #Kills: {}\n:tada: Wins: {}\n:video_game: Plays: {}\n:question: Secret Code: {}".format(winner, kills, wins, plays, hex(r_num).lstrip('0x').rstrip('L').upper()), color=0x00ff00)
            embed.set_image(url=url)
            embed.set_author(name="The Ring Master")
            await game_chan.send(embed=embed)
            self.save_stats(stats)
        else:
            await game_chan.send('Game was canceled, play again later')

        self.bot.game_running = False
        self.bot.game_starting = False
        self.player_list = []
        self.players = {}
        self.murders = murders.copy()
        self.big = False
        self.delay = 6
        self.canned = False

    async def get_image(self, did):
        try:
            u = await self.bot.fetch_user(did)
            img_o = Image.open(requests.get(u.avatar_url_as(format='png', size=256), stream=True).raw)
            img = img_o.resize((256,256))
            return img
        except:
            return self.placeholder

    @commands.command(aliases=["cancel","c"], pass_context=True)
    async def cancel_game(self, ctx):
        self.canned = True
    #    self.player_list = []
    #    self.players = {}
    #    self.murders = murders.copy()
    #    self.big = False
    #    self.delay = 6
    #    self.game_running = False
    #    self.game_starting = False


    @commands.command(aliases=["stats","s"], pass_context=True)
    async def get_stats_command(self, ctx):
        p = ctx.author.id
        stats = self.get_stats([ctx.author.id])
        #print(dir(ctx.author))
        url = ctx.author.avatar_url
        kills = stats[p]['kills']
        wins = stats[p]['wins']
        plays = stats[p]['plays']
        #print(ctx)
        embed=discord.Embed(title="Stats For {}!!".format(ctx.author.name), description="__**STATS**__\n:knife: Kills: {}\n:tada: Wins: {}\n:video_game: Plays: {}".format(kills, wins, plays), color=0x00ff00)
        embed.set_image(url=url)
        embed.set_author(name="The Ring Master")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id == self.message_id and payload.member.id != 944727265504297000 and self.bot.game_running == False:
            if payload.event_type == 'REACTION_ADD':
                #this is the add player section
                if payload.emoji.id == 945014050067214438 and self.fight_started == False:
                    self.players[payload.member.id] = payload.member.name
                    #print(self.players)
                #this is the start game section
                if payload.emoji.id == 945015871607308309 and self.fight_started == False:
                    if len(self.players) < 5:
                        chan = self.bot.get_channel(self.channel_id)
                        embed = discord.Embed(title="Not Ready Yet!", description="Need more players!\nMinimum of 5 players needed", color=discord.Color.red())
                        embed.set_author(name='The Ring Master', icon_url="https://cdn.discordapp.com/attachments/844059174807797764/944840794332872744/unknown.png")
                        error = await chan.send(embed=embed)
                        await error.delete(delay=5)
                        await self.mess.remove_reaction(self.start_emoji, payload.member)
                    elif len(self.players) >= 5:
                        if payload.member.id == self.owner or payload.member.guild_permissions.manage_guild==True:
                            p_list = '\n'.join([self.players[x] for x in self.players.keys()])
                            chan = self.bot.get_channel(self.channel_id)
                            embed=discord.Embed(title="Lets Get It On!", description="Let the fight begin!", color=0x260ff4)
                            embed.set_author(name="The Ring Master", icon_url="https://cdn.discordapp.com/attachments/844059174807797764/944840794332872744/unknown.png")
                            if self.big:
                                embed.add_field(name="{} Players in the arena".format(len(self.players)), value="BIG FIGHT", inline=True)
                            else:
                                embed.add_field(name="{} Players in the arena".format(len(self.players)), value="```\n{}```".format(p_list), inline=True)
                            await chan.send(embed=embed)
                            await self.play_game()
                        else:
                            chan = self.bot.get_channel(self.channel_id)
                            embed = discord.Embed(title="Not Ready Yet!", description="Not the owner or a Mod!", color=discord.Color.red())
                            embed.set_author(name='The Ring Master', icon_url="https://cdn.discordapp.com/attachments/844059174807797764/944840794332872744/unknown.png")
                            error = await chan.send(embed=embed)
                            await error.delete(delay=5)
                            await self.mess.remove_reaction(self.start_emoji, payload.member)
                    else:
                        print('some other error')


                        print('some other error')



    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id == self.message_id and payload.emoji.id == 945014050067214438:
            try:
                del self.players[payload.user_id]
            except:
                print('player not found')



def setup(bot):
    bot.add_cog(Fight(bot))
