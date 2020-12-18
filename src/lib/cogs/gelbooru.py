import json
from random import choice
from typing import Union

import discord
from discord.ext import commands

from src.lib.utils.basic_utils import ready_up_cog
from src.paths import WEIRD_TAGS_RESPONSE_PATH
from src.setup import GELBOORU_API as GELBOORU


class Gelbooru(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command()
    async def boorusearch(self, ctx, *query) -> None:

        exclude: tuple = ("loli", "gore", "vore", "furry", "scat", "shota", "piss")

        if len(query) == 0:
            return await ctx.reply("Você esqueceu de por as tags! bobão")
        if ctx.channel.nsfw is False:
            return await ctx.send("Esse comando só pode ser usado em canais nsfw!")
        query: list = list(query)
        number_of_images: Union[int, None] = None
        try:
            number_of_images = int(query[-1])
        except (ValueError, IndexError):
            number_of_images = 3
        else:
            query.pop(-1)
        finally:
            query.append(number_of_images)
            query.pop()
        if number_of_images > 10:
            return await ctx.reply("Você não pode requestar mais de 100 imagens! cê ta bem mano?")
        results = (await GELBOORU.search_posts(tags=[tag for tag in query]))[:number_of_images]
        for tag in query:
            if tag in exclude:
                try:
                    response = choice((json.load(open(WEIRD_TAGS_RESPONSE_PATH, encoding="utf-8")))[tag])
                except KeyError:
                    return await ctx.reply(f"Essa tag é muito feia: {tag}")
                else:
                    return await ctx.reply(response)
        if len(results) == 0:
            bad_request_tags: Union[str, list]
            bad_request_tags = ""
            for tag in query:
                bad_request_tags += f"{tag}, "
            bad_request_tags = (list(bad_request_tags))
            bad_request_tags[-2] = ""
            bad_request_tags = ("".join(bad_request_tags)).strip()
            return await ctx.reply(f'Não tem hentai com as tags "{bad_request_tags}" não mano :(')
        else:
            warn_sent: bool
            bad_query: bool
            warn_sent = False
            for img in results:
                bad_query = False
                for bad_tag in exclude:
                    if bad_tag in img.tags:
                        bad_query = True
                        if warn_sent is not True:
                            warn_sent = True
                            await ctx.reply(
                                "Uma das imagens contém tags feias, eu ignorarei as imagens que contém tags feias"
                            )
                if bad_query is False:

                    booru_embed = discord.Embed()
                    if img.source is not None:
                        sauce_msg = choice(
                            (
                                "Sua sauça.",
                                "Seu link, companheiro.",
                                "Não precisa chamar os cachorro!",
                                "EU TENHO O LINK",
                                "Vou desempregar os cachorro!",
                                "Que cachorro o que!"
                            )
                        )
                        booru_embed.set_author(name=sauce_msg, url=img.source)
                    else:
                        sauce_msg = choice(
                            (
                                "EU TENHO O LINK... eu diria isso se eu tivesse :(",
                                "Os cachorro roubou o link",
                                "Link? não ouço falar disso há muitos anos...",
                                "O link sumiu..."
                            )
                        )
                        booru_embed.set_author(name=sauce_msg)
                    booru_embed.set_image(url=str(img))
                    await ctx.send(embed=booru_embed)
            return await ctx.reply("Acabei, pode fazer o que sei lá o que tu quer fazer com isso")


def setup(bot):
    bot.add_cog(Gelbooru(bot))
