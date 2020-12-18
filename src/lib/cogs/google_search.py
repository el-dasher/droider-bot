import time

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from src.lib.utils.basic_utils import ready_up_cog
from src.setup import GOOGLE_USEFULS

GOOGLE_SEARCH_ID = GOOGLE_USEFULS["id"]
GOOGLE_API = GOOGLE_USEFULS["api_key"]


class GoogleSearch(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.command()
    async def googlesearch(self, ctx: discord.ext.commands.Context, *query):
        query = list(query)

        if not query:
            return await ctx.reply("Mas e o contexto?")

        if query[-1] != "+":
            query.append("")

        url = (
            "https://www.googleapis.com/customsearch/"
            f"v1?key={GOOGLE_API}&cx={GOOGLE_SEARCH_ID}&q={query[:-1]}"
        )

        result_embed = discord.Embed()

        try:
            results = requests.get(url).json()["items"]
        except KeyError:
            return await ctx.reply(f"Não foi possivel encontrar nada sobre: {query}")

        if query[-1] != "+":
            results = results[:1]
        query.pop(-1)
        for result in results:
            description = "Não especificada."
            try:
                description = (BeautifulSoup(result["snippet"], features="html.parser")).get_text()
            except KeyError:
                pass
            finally:
                result_embed.add_field(name=result['title'], value=f"[link]({result['link']}) {description}")

        return await ctx.reply(content=f"<@{ctx.author.id}>", embed=result_embed)

    @commands.command()
    async def im(self, ctx, *query) -> None:
        if not query:
            return await ctx.reply("Você esqueceu de por os parâmetros para a pesquisa!")
        query = " ".join(query)

        url = (
            "https://www.googleapis.com/customsearch/"
            f"v1?key={GOOGLE_API}&cx={GOOGLE_SEARCH_ID}&q={query}"
        )

        request_data: dict = requests.get(url).json()

        image_url = None
        first_img_data = None

        try:
            image_url = (first_img_data := request_data["items"][0])["pagemap"]["cse_image"][0]["src"]
        except KeyError:
            try:
                if request_data["error"]["code"] == 429:
                    return await ctx.reply("Infelizmente o limite de buscas de hoje foi atingido...")
            except KeyError:
                return await ctx.reply(f"Não foi possivel encontrar resultados para: {query}")
        title = first_img_data["title"]
        link = first_img_data["link"]

        im_embed = discord.Embed()

        im_embed.set_author(name=title, url=link)
        im_embed.set_image(url=image_url)

        message: discord.Message = await ctx.reply(content=f"<@{ctx.author.id}>", embed=im_embed)

        await message.add_reaction("⬅")
        await message.add_reaction("➡")

        counter = 0
        timeout = time.time() + 60
        while time.time() < timeout:
            valid_reaction: tuple = await self.bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in ("⬅", "➡")
            )

            if valid_reaction:
                if valid_reaction[0].emoji == "➡":
                    counter += 1
                else:
                    counter -= 1

                next_im_embed = discord.Embed()

                try:
                    current_request = (
                        (current_img_data := request_data["items"][counter])["pagemap"]["cse_image"][0]["src"]
                    )
                except (IndexError, KeyError):
                    pass
                else:
                    title = current_img_data["title"]
                    link = current_img_data["link"]

                    next_im_embed.set_author(name=title, url=link)
                    next_im_embed.set_image(url=current_request)

                    await message.edit(embed=next_im_embed)


def setup(bot):
    bot.add_cog(GoogleSearch(bot))
