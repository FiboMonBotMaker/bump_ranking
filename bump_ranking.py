from copy import copy
from email.policy import default
from googletrans import Translator
from datetime import datetime
import json
import os
import random
import discord
from discord import Option, OptionChoice
from discord.ext import commands
from dotenv import load_dotenv
import re
import bump_guild
from bump_guild import ja_time
import urllib.parse
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
    await ctx.interaction.edit_original_message(content='', file=discord.File('bumpdate.csv'))


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
                await ctx.respond('ちょ待てよ', ephemeral=True)
        else:
            await ctx.respond('設定チャネルが違います', ephemeral=True)
    else:
        await ctx.respond('チャンネル設定まだよ', ephemeral=True)


@bot.slash_command(description="ランクを表示します", guild_ids=guild_ids)
@commands.cooldown(rate=1, per=10, type=commands.BucketType.guild)
async def rank(ctx):
    await bump_command_base(ctx, process=send_rank)


@bot.slash_command(description="CSVを取得します", guild_ids=guild_ids)
@commands.cooldown(rate=1, per=10, type=commands.BucketType.guild)
async def csv(ctx):
    await bump_command_base(ctx, process=send_csv)


setcommand = bot.create_group(
    name="set", description="使用する場所を登録します", guild_ids=guild_ids)


@setcommand.command(name="bump_channel", description="bump channelを設定します")
@commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
async def set_bump_channel(ctx):
    global bumper_guilds
    bumper_guilds[ctx.guild.id].set_bump_channel(ctx.channel.id)
    await ctx.respond(f'Bumpチャンネルを{ctx.channel.name}にセットしたよ')


@bot.slash_command(description='褒められたときに名前を入れて使いましょう', guild_ids=guild_ids)
async def get_home(
        ctx,
        name: Option(str, default='NB', required=False, description='ない場合はNBさんになります'),
        homenai: Option(str, default='褒められる', required=False, description='もし、褒めないられない場合はここで変更'),
        nanika: Option(str, default='自信', required=False, description='もし、自信以外の場合はここで変更')):

    up = f'{name}さんに{homenai}と'
    down = f'{nanika}になります！'

    await ctx.respond(f'https://gsapi.cyberrex.jp/image?top={urllib.parse.quote(up)}&bottom={urllib.parse.quote(down)}')


values = [
    OptionChoice(name='悲報', value='【悲報wwwwwwwwww】'),
    OptionChoice(name='朗報', value='【朗報wwwwwwwwww】'),
    OptionChoice(name='良報', value='【良報WWwwwWwWwWww】')
]


@bot.slash_command(description='NB構文Y型', guild_ids=guild_ids)
async def get_nb2(
    ctx,
    any_hou: Option(str, default=values[0].value, choices=values, required=False, description='何報ですか？'),
    honbun: Option(str, default='ワイ氏パチスロにいって', required=False,
                   description='本文を入力しよう→{本文}しまうwwwwwwwwww')):
    down = f'{honbun}しまうwwwwwwwwww'
    await ctx.respond(f'https://gsapi.cyberrex.jp/image?top={urllib.parse.quote(any_hou)}&bottom={urllib.parse.quote(down)}')

itudokocommand = setcommand = bot.create_group(
    name="itudoko", description="いつどこします", guild_ids=guild_ids)

itudoko = [
    OptionChoice(name='いつ', value=0),
    OptionChoice(name='どこで', value=1),
    OptionChoice(name='だれが', value=2),
    OptionChoice(name='何をした', value=3)
]

FILE_NAME = 'itudoko.json'

with open(FILE_NAME, mode='rt', encoding='utf-8') as file:
    stack: list[list[str]] = json.load(file)


def wright_json(stack: list[list[str]]):
    with open(FILE_NAME, mode='wt', encoding='utf-8') as file:
        json.dump(stack, file, ensure_ascii=False)


@itudokocommand.command(name="set", description="いつどこワードを追加します")
async def itudokoset(ctx, choise: Option(int, choices=itudoko), value: Option(str, description='リテラルを決定してね')):
    stack[choise].append(value)
    wright_json(stack=stack)
    await ctx.respond(f'{value}をセットしました', ephemeral=True)


@itudokocommand.command(name='get', description='今まで貯めた文字列でランダムにいつどこいます')
async def itudokoget(ctx):
    await ctx.respond(
        f'{random.choice(stack[0])}{random.choice(stack[1])}{random.choice(stack[2])}{random.choice(stack[3])}')


tr = Translator()

lang_codes: list[str] = ['en', 'it', 'ne', 'ko', 'de']


def random_transe(word: str, lang: str, loop: int, lang_codes: list[str]) -> str:
    if loop == 0:
        return tr.translate(word, src=lang, dest='ja').text
    else:
        random.shuffle(lang_codes)
        tmp_lang = lang_codes.pop()
        return random_transe(
            word=tr.translate(word, src=lang, dest=tmp_lang).text,
            lang=tmp_lang,
            loop=loop - 1,
            lang_codes=lang_codes)


@ itudokocommand.command(name='trans', description='再翻訳で支離滅裂な文章に変換します')
async def itudokotrans(ctx, loop: Option(int, description='再翻訳回数を上げて精度を低めます デフォルト loop=1', min_value=1, max_value=5, default=1, required=False)):
    word = f'{random.choice(stack[0])}{random.choice(stack[1])}{random.choice(stack[2])}{random.choice(stack[3])}'
    await ctx.respond(f'翻訳前 : {word}')
    dest_word = random_transe(
        word=word,
        lang='ja',
        loop=loop,
        lang_codes=copy(lang_codes)
    )
    await ctx.interaction.edit_original_message(content=f'翻訳前 : {word}\n翻訳後 : {dest_word}')


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error, ephemeral=True)
    else:
        raise error


bot.run(TOKEN)
