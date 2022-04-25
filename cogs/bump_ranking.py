import os
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from dotenv import load_dotenv
import re
import datetime

ja_time = datetime.timedelta(hours=9)


class Bump_guild():

    def __init__(self):
        self.success: bool = True
        self.bumpers = []
        self.channels = {'bump': None, 'chat': None}
        global ja_time
        tmpdate = datetime.datetime.now()
        self.date = datetime.datetime(
            year=tmpdate.year, month=tmpdate.month, day=1) - ja_time

    def get_bumper(self):
        return self.bumpers

    def set_bump_channel(self, bump_channel):
        self.channels['bump'] = bump_channel

    def get_bump_channel(self):
        return self.channels['bump']

    def set_chat_channel(self, chat_channel):
        self.channels['chat'] = chat_channel

    def get_chat_channel(self):
        return self.channels['chat']

    def set_date(self, date: datetime.datetime):
        self.date = date

    def get_date(self):
        return self.date

    def check_channels(self, command, channel_id):
        return channel_id == self.channels[command[1]]


class BumpRanking(commands.Cog):

    def __init__(self, bot,):
        print('bumpRanking')
        self.bot = bot
        self.bumper_guilds: dict[int, Bump_guild] = {}
        # bumpとdissokuのID定義と各掲示板のポイント比率
    bump_id = 0
    dissoku_id = 1
    category_point = [1.5, 1.0]

    rank = SlashCommandGroup('rank', '順位を取得します')

    # 連続回数ごとのポイントの配分
    table = [1.0, 1.2, 1.5, 2.0, 2.7, 3.8]

    # ランク
    apex_rank: list[str] = ['Predator', 'Master', 'Diamond', 'Platinum',
                            'Gold', 'Silver', 'Bronze']

    # ユーザーIDを取得する正規表現
    namept = re.compile('<.*>')

    async def add_bump(self, ctx, _ctx):
        """
        /bumpコマンドを利用した後のDisboardのレスポンスから利用者を検出し、各ギルドのリストに登録します。
        """
        try:
            if('アップしたよ' in _ctx.embeds[0].description):
                self.bumper_guilds[ctx.guild.id].get_bumper().append(
                    [str(BumpRanking.namept.search(_ctx.embeds[0].description).group()), _ctx.created_at + ja_time, BumpRanking.bump_id])
        except:
            ...

    async def add_dissoku(self, ctx, _ctx):
        """
        /dissoku upコマンドを利用した後のディス速のレスポンスから利用者を検出し、各ギルドのリストに登録します。
        """
        if('アップしたよ' in (_ctx.embeds[0].fields[0].name if len(_ctx.embeds[0].fields) != 0 else '')):
            self.bumper_guilds[ctx.guild.id].get_bumper().append([
                str(BumpRanking.namept.search(_ctx.embeds[0].description).group()).replace('!', ''), _ctx.created_at + ja_time, BumpRanking.dissoku_id])

    # 各掲示板のBOTのIDと関数をdictに定義したもの
    bbs_dict = {
        302050872383242240: add_bump,
        761562078095867916: add_dissoku
    }

    async def set_bumper_id(self, ctx):
        """
        bump系コマンドから呼び出す関数
        discord.ctxからチャンネルIDを取得して前回取得分のデータを除いた過去データを取得する
        """

        bump_channel = self.bot.get_channel(
            self.bumper_guilds[ctx.guild.id].get_bump_channel())

        tmp_ctxs = bump_channel.history(
            limit=None, after=self.bumper_guilds[ctx.guild.id].get_date())

        # bbs_dictに登録されたユーザーIDかを確認して、そうであればbbs_dictの関数を呼び出す
        async for _ctx in tmp_ctxs:
            if(_ctx.author.id in BumpRanking.bbs_dict.keys()):
                await BumpRanking.bbs_dict[_ctx.author.id](self, ctx=ctx, _ctx=_ctx)

    # bump系コマンドの定義

    async def send_rank(self, ctx):
        """
        rankコマンドで利用する関数です。
        利用チャンネルに対して今月の現在のポイントをメッセージとして送信します。
        """
        async def get_point(count, brocker, id) -> float:
            """
            ポイントの計算に利用します。
            category_pointのポイントはbumpとdissokuで分けられています。
            """
            if brocker != 0:
                count = brocker
            return (BumpRanking.table[count] if count < len(BumpRanking.table) else BumpRanking.table[-1]) * BumpRanking.category_point[int(id)]

        self.bumper_guilds[ctx.guild.id].success = False
        await BumpRanking.set_bumper_id(self, ctx)
        self.bumper_guilds[ctx.guild.id].set_date(datetime.datetime.now())
        tmp_map = dict()
        flg = None
        count = 0
        for lit in self.bumper_guilds[ctx.guild.id].get_bumper():
            brocker = 0
            if lit[0] == flg:
                count += 1
            else:
                brocker = count
                count = 0
            if(lit[0] in tmp_map):
                tmp_map[lit[0]] += await get_point(count, brocker, lit[2])
            else:
                tmp_map[lit[0]] = await get_point(count, brocker, lit[2])
            flg = lit[0]
        text = ''
        for i, n in enumerate(sorted(tmp_map.items(), key=lambda x: x[1], reverse=True)):
            word = '【{:^10}】   {:>30}   {:>5.02f}point\n'.format(
                (BumpRanking.apex_rank[i] if i < len(BumpRanking.apex_rank) else BumpRanking.apex_rank[-1]), n[0], n[1])
            text += word
        # print(text)
        embed = discord.Embed(
            title='＜月間bumpランキング＞',
            color=0x00ff00,
            description=text)
        await ctx.interaction.edit_original_message(content='', embed=embed)
        self.bumper_guilds[ctx.guild.id].success = True

    async def send_csv(self, ctx):
        await BumpRanking.set_bumper_id(self, ctx)
        self.bumper_guilds[ctx.guild.id].set_date(datetime.now())
        csv = open('bumpdate.csv', 'w', encoding='UTF-8')
        for bumper in self.bumper_guilds[ctx.guild.id].get_bumper():
            csv.write(f'{bumper[0]},{bumper[1]},{bumper[2]}\n')
        csv.close()
        await ctx.interaction.edit_original_message(content='', file=discord.File('bumpdate.csv'))

    # デフォルト系コマンドを定義

    async def bump_command_base(self, ctx, process):
        if self.bumper_guilds[ctx.interaction.guild_id].get_bump_channel() != None:
            if self.bumper_guilds[ctx.interaction.guild_id].get_bump_channel() == ctx.channel.id:
                if self.bumper_guilds[ctx.interaction.guild_id].success:
                    await ctx.respond('ちょっとまってろ')
                    await process(self, ctx)
                else:
                    await ctx.respond('ちょ待てよ', ephemeral=True)
            else:
                await ctx.respond('設定チャネルが違います', ephemeral=True)
        else:
            await ctx.respond('チャンネル設定まだよ', ephemeral=True)

    @rank.command(description="ランクを表示します")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.guild)
    async def get(self, ctx):
        await BumpRanking.bump_command_base(self, ctx=ctx, process=BumpRanking.send_rank)

    @rank.command(description="CSVを取得します")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.guild)
    async def csv(self, ctx):
        await BumpRanking.bump_command_base(self, ctx=ctx, process=BumpRanking.send_csv)

    @rank.command(name="set_channel", description="bump channelを設定します")
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def set_bump_channel(self, ctx):
        self.bumper_guilds[ctx.guild.id].set_bump_channel(ctx.channel.id)
        await ctx.respond(f'Bumpチャンネルを{ctx.channel.name}にセットしたよ')

    @commands.Cog.listener(name='on_ready')
    async def on_ready(self):
        # print(bot.guilds)
        for guild in self.bot.guilds:
            self.bumper_guilds[guild.id] = Bump_guild()
        for guild in self.bumper_guilds.keys():
            print(guild)


def setup(bot):
    bot.add_cog(BumpRanking(bot))
