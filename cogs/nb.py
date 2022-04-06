import discord
from discord.ext import commands
from discord.commands import slash_command
from discord import Option

class NbCog(commands.cog):


    def __init__(self, bot):
        print('NBさんの初期化')
        self.bot = bot

            
    nb = bot.create_group(
                        name="nb",
                        description="nb高文系",
                        guild_ids=guild_ids)

    @nb.ommand(name='home',description='褒められたときに名前を入れて使いましょう')
    async def nb_home(
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
        OptionChoice(name='良報', value='【良報WWwwwWwWwWww】'),
        OptionChoice(name='速報', value='【速報wwwwwwwwwww】')
    ]


    @nb.command(name='youtube',description='NB構文Y型')
    async def get_nb2(
        ctx,
        any_hou: Option(str, default=values[0].value, choices=values, required=False, description='何報ですか？'),
        honbun: Option(str, default='ワイ氏パチスロにいって', required=False,
                    description='本文を入力しよう→{本文}しまうwwwwwwwwww')):
        down = f'{honbun}しまうwwwwwwwwww'
        await ctx.respond(f'https://gsapi.cyberrex.jp/image?top={urllib.parse.quote(any_hou)}&bottom={urllib.parse.quote(down)}')


def setup(bot):
    bot.add_cog(NbCog(bot))
