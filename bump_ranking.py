import os
import discord
from dotenv import load_dotenv
import re
import bump_guild
from bump_guild import ja_time
load_dotenv()
TOKEN = os.getenv('TOKEN')
client = discord.Client()

apex_rank = ["Predator", "Master", "Diamond", "Platinum",
             "Gold", "Silver", "Bronze"]


namept = re.compile('<.*>')

# guild毎に情報を登録する
bumper_guilds = dict()


async def add_bump(message, _message):
    if("アップしたよ" in _message.embeds[0].description):
        bumper_guilds[message.guild.id].get_bumper().append(
            [str(namept.search(_message.embeds[0].description).group()), _message.created_at + ja_time, '0'])


async def add_dissoku(message, _message):
    if("アップしたよ" in (_message.embeds[0].fields[0].name if len(_message.embeds[0].fields[0].value) != 0 else "")):
        bumper_guilds[message.guild.id].get_bumper().append([
            str(namept.search(_message.embeds[0].description).group()).replace("!", ""), _message.created_at + ja_time, '1'])

bbs_list = {
    302050872383242240: add_bump,
    761562078095867916: add_dissoku
}


# bump_channelからidをリストにする関数


async def set_bumper_id(message):

    global bumper_guilds

    bump_channel = client.get_channel(
        bumper_guilds[message.guild.id].get_bump_channel())

    tmp_messages = bump_channel.history(
        limit=None, after=bumper_guilds[message.guild.id].get_date())

    async for _message in tmp_messages:
        if(_message.author.id in bbs_list.keys()):
            await bbs_list[_message.author.id](message=message, _message=_message)

            # bump系コマンドの定義


async def send_rank(message):
    async def get_point(count, brocker, id) -> float:
        categorys = [1.5, 1.0]
        table = [1.0, 1.2, 1.5, 2.0, 2.7, 3.8]
        if brocker != 0:
            count = brocker
        return (table[count] if count < len(table) else table[-1]) * categorys[int(id)]

    global bumper_guilds
    await set_bumper_id(message)
    bumper_guilds[message.guild.id].set_date(message.created_at)
    tmp_map = dict()
    flg = None
    count = 0
    for lit in bumper_guilds[message.guild.id].get_bumper():
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
    text = ""
    for i, n in enumerate(sorted(tmp_map.items(), key=lambda x: x[1], reverse=True)):
        word = '【{:^10}】   {:>30}   {:>5.02f}point\n'.format(
            (apex_rank[i] if i < len(apex_rank) else apex_rank[-1]), n[0], n[1])
        text += word
    # print(text)
    embed = discord.Embed(
        title="＜月間bumpランキング＞",
        color=0x00ff00,
        description=text)
    await message.channel.send(embed=embed)


async def send_csv(message):
    global bumper_guilds
    await set_bumper_id(message)
    bumper_guilds[message.guild.id].set_date(message.created_at)
    csv = open('bumpdate.csv', 'w', encoding='UTF-8')
    for bumper in bumper_guilds[message.guild.id].get_bumper():
        csv.write(f'{bumper[0]},{bumper[1]},{bumper[2]}\n')
    csv.close()
    await message.channel.send(file=discord.File('bumpdate.csv'))


# chat系コマンドの定義


async def send_test(message):
    await message.channel.send("pong!")

commands = {
    '/rank': [send_rank, 'bump'],
    '/csv': [send_csv, 'bump'],
    "/test": [send_test, 'chat']
}

# デフォルト系コマンドを定義


async def set_channel(message, channel_name):
    await message.channel.send(f"{channel_name}チャンネルを{message.channel.name}にセットしたよ")


async def set_bump_channel(message):
    global bumper_guilds
    bumper_guilds[message.guild.id].set_bump_channel(message.channel.id)
    await set_channel(message=message, channel_name='bump')


async def set_chat_channel(message):
    global bumper_guilds
    bumper_guilds[message.guild.id].set_chat_channel(message.channel.id)
    await set_channel(message=message, channel_name='chat')


basic_commands = {
    '/set_bump_channel': set_bump_channel,
    '/set_chat_channel': set_chat_channel
}


# 起動時に実行される処理
@client.event
async def on_ready():
    global bumper_guilds
    # print(client.guilds)
    for guild in client.guilds:
        bumper_guilds[guild.id] = bump_guild.Bump_guild()
    for guild in bumper_guilds.keys():
        print(guild)

# ギルドに追加された際に実行される処理


@client.event
async def on_guild_join(guild):
    global bumper_guilds
    if not (guild.id in bumper_guilds.keys()):
        bumper_guilds[guild.id] = bump_guild.Bump_guild()
    print(f"add {guild.id}")
    await guild.text_channels[0].send('追加された旨のメッセージ')


# メッセージを受け取った時に実行するコマンド
@client.event
async def on_message(message):
    global bumper_guilds
    if(message.author.bot):
        return
    # コマンド呼び出し部
    if(message.content in commands):
        if(bumper_guilds[message.guild.id].check_channels(commands[message.content], message.channel.id)):
            await commands[message.content][0](message)
        else:
            await message.channel.send(f"{message.content} を利用するには、まだチャンネルを設定していないようです")
    # 設定項目系のチャンネル指定しないコマンド呼び出し部
    else:
        if(message.content in basic_commands):
            await basic_commands[message.content](message)


client.run(TOKEN)
