from random import choice

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands

from src.lib.db.pydata.pydata import bot_presences
from src.lib.utils.basic_utils import ready_up_cog
from src.setup import DATABASE


class Funny(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    @commands.Cog.listener()
    async def on_ready(self):
        self.scheduler.add_job(self.presences, CronTrigger(second=0))
        self.scheduler.start()

        ready_up_cog(self.bot, __name__)

    @commands.command()
    async def owo(self, ctx):
        return await ctx.reply("UwU")

    async def presences(self):
        return await self.bot.change_presence(activity=(choice(bot_presences)))

    @commands.command()
    async def ping(self, ctx):
        return await ctx.reply(
            f"Pingo, tô levando {self.bot.latency:.3f} milissegundos pra responder a api do Discord."
        )

    @commands.command()
    async def follow(self, ctx: commands.Context):
        follower_role = ctx.guild.get_role(789638184048525363)
        await ctx.author.add_roles(follower_role)
        return await ctx.reply("Você agora sera notificado sobre novos videos da osu!droid brasil! poggers?")

    @commands.command()
    async def unfollow(self, ctx: commands.Context):
        follower_role = ctx.guild.get_role(789638184048525363)
        await ctx.author.remove_roles(follower_role)
        return await ctx.reply("Sinceramente, pau no seu cu.")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if type(reaction.emoji) == str:
            reaction_emoji_name = reaction.emoji
        else:
            reaction_emoji_name = reaction.emoji.name
        print(reaction_emoji_name)
        if reaction_emoji_name == "AuTiStIcSoUl":
            valid_reaction_count = len(list(filter(lambda x: x is not False, [
                u != user async for u in reaction.users()
            ])))

            if valid_reaction_count == 3:
                reaction_message: discord.Message = reaction.message
                reaction_guild: discord.Guild = reaction_message.guild
                pearl_creator: discord.User = reaction_message.author

                starboard: discord.TextChannel = reaction_guild.get_channel(
                    DATABASE.child("STARBOARDS").child(str(reaction_guild.id)).child("id").get().val()
                )

                pearl_embed = discord.Embed(title="Nova perola!", color=pearl_creator.color)

                pearl_content = reaction_message.content
                if reaction_message.content == "":
                    pearl_content = "\u200b"

                pearl_embed.add_field(name="Conteúdo", value=pearl_content)

                if len(reaction_message.attachments) != 0:
                    pearl_embed.set_image(url=list(reaction_message.attachments)[0].url)

                pearl_embed.set_author(name=pearl_creator.name, icon_url=pearl_creator.avatar_url)

                return await starboard.send("", embed=pearl_embed)

    @commands.command()
    async def setpearl(self, ctx: commands.Context, pearl_channel: discord.TextChannel = None):
        if pearl_channel is None:
            pearl_channel = ctx.channel

        DATABASE.child("STARBOARDS").child(ctx.guild.id).set({
            "id": pearl_channel.id,
            "name": pearl_channel.name,
            "position": pearl_channel.position,
            "nsfw": str(pearl_channel.nsfw),
            "category_id": pearl_channel.category_id
        })

        return await ctx.reply(f"O novo canal de perolas é o {pearl_channel.mention}")


def setup(bot):
    bot.add_cog(Funny(bot))
