import os
import discord
import datetime
from dotenv import load_dotenv
import re
load_dotenv()
TOKEN = os.getenv('TOKEN')
client = discord.Client()

# 新しい日付を取得する必要があるのでworkを定義する予定
tmpdate = datetime.datetime.now()
last_message_time = datetime.datetime(
    year=tmpdate.year, month=tmpdate.month, day=1)

apex_rank = ["Predator", "Master", "Diamond", "Platinum",
             "Gold", "Silver", "Bronze"]

namept = re.compile('<.*>')

bump_channels = dict()
chat_channels = dict()

bumper_id = []

# bump_channelからidをリストにする関数


async def set_bumper_id(message):
    global last_message_time
    global bump_channels

    bump_channel = client.get_channel(bump_channels[message.guild.id])

    tmp_messages = bump_channel.history(
        limit=None, after=last_message_time)

    async for _message in tmp_messages:
        if (_message.author.id == 302050872383242240):
            if("アップしたよ" in _message.embeds[0].description):
                bumper_id.append(
                    [_message.embeds[0].description[0:21], _message.created_at])
        if (_message.author.id == 761562078095867916):
            if("アップしたよ" in (_message.embeds[0].fields[0].name if len(_message.embeds[0].fields[0].value) != 0 else "")):
                bumper_id.append([
                    str(namept.search(_message.embeds[0].description).group()).replace("!", ""), _message.created_at])

# bump系コマンドの定義


async def send_rank(message):
    global last_message_time
    await set_bumper_id(message)
    last_message_time = message.created_at
    tmp_map = dict()
    for lit in bumper_id:
        if(lit[0] in tmp_map):
            tmp_map[lit[0]] += 1
        else:
            tmp_map[lit[0]] = 1
    text = ""
    for i, n in enumerate(sorted(tmp_map.items(), key=lambda x: x[1], reverse=True)):
        word = "【" + (apex_rank[i] if i < len(apex_rank) else apex_rank[-1]) + "】 "+n[0] +\
            " "+str(n[1])+"回\n"
        text += word
    embed = discord.Embed(
        title="＜月間bumpランキング＞",
        color=0x00ff00,
        description=text)
    await message.channel.send(embed=embed)


async def send_csv(message):
    global last_message_time
    await set_bumper_id(message)
    last_message_time = message.created_at
    # print(bumper_id)
    csv = open('bumpdate.csv', 'w', encoding='UTF-8')
    for bumper in bumper_id:
        csv.write(f'{bumper[0]},{bumper[1]}\n')
    csv.close()
    await message.channel.send(file=discord.File('bumpdate.csv'))

bump_commands = {
    '/rank': send_rank,
    '/csv': send_csv
}

# chat系コマンドの定義


async def send_test(message):
    await message.channel.send("pong!")

chat_commands = {
    "/test": send_test
}

# デフォルト系コマンドを定義


async def set_bump_channel(message):
    global bump_channels
    bump_channels[message.guild.id] = message.channel.id
    # print(bump_channels)
    await message.channel.send(f"bumpチャンネルを{message.channel.name}にセットしたよ")


async def set_chat_channel(message):
    global chat_channels
    chat_channels[message.guild.id] = message.channel.id
    # print(bump_channels)
    await message.channel.send(f"chatチャンネルを{message.channel.name}にセットしたよ")

basic_commands = {
    '/set_bump_channel': set_bump_channel,
    '/set_chat_channel': set_chat_channel
}


# メッセージを受け取った時に実行するコマンド


@client.event
async def on_message(message):
    global last_message_time
    if(message.author.bot):
        return
    # chat系のコマンド呼び出し部
    if(message.content in chat_commands):
        if(message.guild.id in chat_channels.keys() and message.channel.id == chat_channels[message.guild.id]):
            await chat_commands[message.content](message)
        else:
            await message.channel.send(f"{message.content} を利用するには、まだチャンネルを設定していないようです")
    # bump系のコマンド呼び出し部
    elif(message.content in bump_commands):
        if(message.guild.id in bump_channels.keys() and message.channel.id == bump_channels[message.guild.id]):
            await bump_commands[message.content](message)
            last_message_time = message.created_at
        else:
            await message.channel.send(f"{message.content} を利用するには、まだチャンネルを設定していないようです")
    # 設定項目系のチャンネル指定しないコマンド呼び出し部
    else:
        if(message.content in basic_commands):
            await basic_commands[message.content](message)


client.run(TOKEN)
