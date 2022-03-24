from datetime import datetime
import os
import discord
from dotenv import load_dotenv
import re
import bump_guild
from bump_guild import ja_time

# おまじない
load_dotenv()
TOKEN = os.getenv('NTOKEN')
bot = discord.Bot()

guild_ids = [879288794560471050]

# bumpとdissokuのID定義と各掲示板のポイント比率
bump_id = 0
dissoku_id = 1
category_point = [1.5, 1.0]

# 連続回数ごとのポイントの配分
table = [1.0, 1.2, 1.5, 2.0, 2.7, 3.8]

# ランク
apex_rank: list[str] = ['Predator', 'Master', 'Diamond', 'Platinum',
                        'Gold', 'Silver', 'Bronze']

# guild毎に情報を登録する
bumper_guilds: dict[int, bump_guild.Bump_guild] = {}

# ユーザーIDを取得する正規表現
namept = re.compile('<.*>')


async def add_bump(ctx, _ctx):
    """
    /bumpコマンドを利用した後のDisboardのレスポンスから利用者を検出し、各ギルドのリストに登録します。
    """
    try:
        if('アップしたよ' in _ctx.embeds[0].description):
            bumper_guilds[ctx.guild.id].get_bumper().append(
                [str(namept.search(_ctx.embeds[0].description).group()), _ctx.created_at + ja_time, bump_id])
    except:
        ...


async def add_dissoku(ctx, _ctx):
    """
    /dissoku upコマンドを利用した後のディス速のレスポンスから利用者を検出し、各ギルドのリストに登録します。
    """
    if('アップしたよ' in (_ctx.embeds[0].fields[0].name if len(_ctx.embeds[0].fields) != 0 else '')):
        bumper_guilds[ctx.guild.id].get_bumper().append([
            str(namept.search(_ctx.embeds[0].description).group()).replace('!', ''), _ctx.created_at + ja_time, dissoku_id])


# 各掲示板のBOTのIDと関数をdictに定義したもの
bbs_dict = {
    302050872383242240: add_bump,
    761562078095867916: add_dissoku
}


async def set_bumper_id(ctx):
    """
    bump系コマンドから呼び出す関数
    discord.ctxからチャンネルIDを取得して前回取得分のデータを除いた過去データを取得する
    """
    global bumper_guilds

    bump_channel = bot.get_channel(
        bumper_guilds[ctx.guild.id].get_bump_channel())

    tmp_ctxs = bump_channel.history(
        limit=None, after=bumper_guilds[ctx.guild.id].get_date())

    # bbs_dictに登録されたユーザーIDかを確認して、そうであればbbs_dictの関数を呼び出す
    async for _ctx in tmp_ctxs:
        if(_ctx.author.id in bbs_dict.keys()):
            await bbs_dict[_ctx.author.id](ctx=ctx, _ctx=_ctx)


# bump系コマンドの定義


async def send_rank(ctx):
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
        return (table[count] if count < len(table) else table[-1]) * category_point[int(id)]

    global bumper_guilds
    bumper_guilds[ctx.guild.id].success = False
    await set_bumper_id(ctx)
    bumper_guilds[ctx.guild.id].set_date(datetime.now())
    tmp_map = dict()
    flg = None
    count = 0
    for lit in bumper_guilds[ctx.guild.id].get_bumper():
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
            (apex_rank[i] if i < len(apex_rank) else apex_rank[-1]), n[0], n[1])
        text += word
    # print(text)
    embed = discord.Embed(
        title='＜月間bumpランキング＞',
        color=0x00ff00,
        description=text)
    await ctx.interaction.edit_original_message(content='', embed=embed)
    bumper_guilds[ctx.guild.id].success = True


async def send_csv(ctx):
    global bumper_guilds
    await set_bumper_id(ctx)
    bumper_guilds[ctx.guild.id].set_date(datetime.now())
    csv = open('bumpdate.csv', 'w', encoding='UTF-8')
    for bumper in bumper_guilds[ctx.guild.id].get_bumper():
        csv.write(f'{bumper[0]},{bumper[1]},{bumper[2]}\n')
    csv.close()
    await ctx.respond(file=discord.File('bumpdate.csv'))


# デフォルト系コマンドを定義


# 起動時に実行される処理
@bot.event
async def on_ready():
    global bumper_guilds
    # print(bot.guilds)
    for guild in bot.guilds:
        bumper_guilds[guild.id] = bump_guild.Bump_guild()
    for guild in bumper_guilds.keys():
        print(guild)

# ギルドに追加された際に実行される処理


@bot.event
async def on_guild_join(guild):
    global bumper_guilds
    if not (guild.id in bumper_guilds.keys()):
        bumper_guilds[guild.id] = bump_guild.Bump_guild()
    print(f'add {guild.id}')
    await guild.text_channels[0].send('追加された旨のメッセージ')


async def bump_command_base(ctx, process):
    global bumper_guilds
    if bumper_guilds[ctx.interaction.guild_id].get_bump_channel() != None:
        if bumper_guilds[ctx.interaction.guild_id].get_bump_channel() == ctx.channel.id:
            if bumper_guilds[ctx.interaction.guild_id].success:
                await ctx.respond('ちょっとまってろ')
                await process(ctx)
            else:
                await ctx.respond('ちょ待てよ')
        else:
            await ctx.respond('設定チャネルが違います')
    else:
        await ctx.respond('チャンネル設定まだよ')


@bot.slash_command(description="ランクを表示します", guild_ids=guild_ids)
async def rank(ctx):
    await bump_command_base(ctx, process=send_rank)


@bot.slash_command(description="CSVを取得します", guild_ids=guild_ids)
async def csv(ctx):
    await bump_command_base(ctx, process=send_csv)


setcommand = bot.create_group(
    name="set", description="使用する場所を登録します", guild_ids=guild_ids)


@setcommand.command(name="bump_channel", description="bump channelを設定します")
async def set_bump_channel(ctx):
    global bumper_guilds
    bumper_guilds[ctx.guild.id].set_bump_channel(ctx.channel.id)
    await ctx.respond(f'Bumpチャンネルを{ctx.channel.name}にセットしたよ')


bot.run(TOKEN)
