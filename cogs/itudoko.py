import json
import discord
from discord.ext import commands
from discord import Option, OptionChoice, SlashCommandGroup
from googletrans import Translator
import random
import copy


class ItudokoCog(commands.Cog):

    def __init__(self, bot):
        print('いつどこ初期化')
        self.bot = bot

    tr = Translator()

    FILE_NAME = 'itudoko.json'
    lang_codes: list[str] = ['en', 'it', 'ne', 'ko', 'de']
    itudoko_list = [
        OptionChoice(name='いつ', value=0),
        OptionChoice(name='どこで', value=1),
        OptionChoice(name='だれが', value=2),
        OptionChoice(name='何をした', value=3)
    ]

    with open(FILE_NAME, mode='rt', encoding='utf-8') as file:
        stack: list[list[str]] = json.load(file)

    def wright_json(stack: list[list[str]]):
        with open(ItudokoCog.FILE_NAME, mode='wt', encoding='utf-8') as file:
            json.dump(stack, file, ensure_ascii=False)

    def random_transe(word: str, lang: str, loop: int, lang_codes: list[str]) -> str:
        if loop == 0:
            return ItudokoCog.tr.translate(word, src=lang, dest='ja').text
        else:
            random.shuffle(lang_codes)
            tmp_lang = lang_codes.pop()
            return ItudokoCog.random_transe(
                word=ItudokoCog.tr.translate(
                    word, src=lang, dest=tmp_lang).text,
                lang=tmp_lang,
                loop=loop - 1,
                lang_codes=lang_codes
            )

    itudoko = SlashCommandGroup('itudoko', 'test')

    @itudoko.command(name='trans', description='再翻訳で支離滅裂な文章に変換します')
    async def itudokotrans(self, ctx, loop: Option(int, description='再翻訳回数を上げて精度を低めます デフォルト loop=1', min_value=1, max_value=5, default=1, required=False)):
        word = f'{random.choice(ItudokoCog.stack[0])}{random.choice(ItudokoCog.stack[1])}{random.choice(ItudokoCog.stack[2])}{random.choice(ItudokoCog.stack[3])}'
        await ctx.respond(f'翻訳前 : {word}')
        dest_word = ItudokoCog.random_transe(
            word=word,
            lang='ja',
            loop=loop,
            lang_codes=copy(ItudokoCog.lang_codes)
        )
        await ctx.interaction.edit_original_message(content=f'翻訳前 : {word}\n翻訳後 : {dest_word}')

    @itudoko.command(name="set", description="いつどこワードを追加します")
    async def itudokoset(self, ctx, choise: Option(int, choices=itudoko_list), value: Option(str, description='リテラルを決定してね')):
        ItudokoCog.stack[choise].append(value)
        ItudokoCog.wright_json(stack=ItudokoCog.stack)
        await ctx.respond(f'{value}をセットしました', ephemeral=True)

    @itudoko.command(name='get', description='今まで貯めた文字列でランダムにいつどこいます')
    async def itudokoget(self, ctx):
        await ctx.respond(
            f'{random.choice(ItudokoCog.stack[0])}{random.choice(ItudokoCog.stack[1])}{random.choice(ItudokoCog.stack[2])}{random.choice(ItudokoCog.stack[3])}')


def setup(bot):
    bot.add_cog(ItudokoCog(bot))
