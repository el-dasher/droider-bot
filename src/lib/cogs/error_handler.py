from discord.ext import commands

from src.lib.utils.basic_utils import ready_up_cog


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        ready_up_cog(self.bot, __name__)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, exc: Exception):
        if isinstance(exc, commands.CommandNotFound):
            await ctx.reply("Esse comando não existe..., cê ta bem mano?")
        elif isinstance(exc, commands.MemberNotFound):
            await ctx.reply("Não possivel encontrar esse membro!")
        elif isinstance(exc, commands.MissingPermissions):
            await ctx.reply("Você não tem permissão para usar esse comando!")
        elif isinstance(exc, commands.BotMissingPermissions):
            await ctx.reply("Eu não tenho permissões para fazer isso!")
        elif isinstance(exc, commands.MissingRequiredArgument):
            await ctx.reply("Você esqueceu de algum argumento necessário para o comando")
        elif isinstance(exc, commands.ChannelNotFound):
            await ctx.reply("Não foi possivel encontrar o canal especificado!")
        elif hasattr(exc, "original"):
            raise exc.original
        else:
            raise exc


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
