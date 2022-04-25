import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('NTOKEN')

bot = discord.Bot(debug_guilds=[879288794560471050])  # main file

path = "./cogs"

filies = os.listdir(path=path)
for file_name in filies:
    tmp = file_name.split('.')
    if len(tmp) == 2:
        print(tmp[0])
        bot.load_extension(f'cogs.{tmp[0]}')

# 起動時に実行される処理


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error, ephemeral=True)
    else:
        raise error


bot.run(TOKEN)  # main file
