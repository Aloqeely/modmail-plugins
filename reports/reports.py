import datetime
import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class Report(commands.Cog): 
    """An easy way for your members to report bad behavior"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def reportchannel(self, ctx, channel: discord.TextChannel):
        """Set the Reports Channel"""
        config = await self.db.find_one({"_id": "config"})

        if config is None:
            await self.db.insert_one({"_id": "config"})
        await self.db.find_one_and_update(
                {"_id": "config"}, {"$set": {"report_channel": channel.name}}
            )
        await ctx.send("Successfully set the Reports channel!")

    @commands.command()
    async def report(self, ctx, user: discord.Member, *, reason):
        """Report a user"""
        config = await self.db.find_one({"_id": "config"})
        report_channel = config["report_channel"]
        if report_channel is not None:
            setchannel = discord.utils.get(ctx.guild.channels, name=report_channel)
        else:
            setchannel = discord.utils.get(ctx.guild.channels, name="reports")
        embed = discord.Embed(
                    color=discord.Color.red())
        embed.set_author(name=ctx.author.name,icon_url=ctx.author.avatar_url)
        embed.set_footer(text=datetime.datetime.today().strftime('%A %b %d | %I:%M %p'))
        embed.add_field(
                name="Reported User", value=f"{user.mention} | ID: {user.id}",inline=False)
        embed.add_field(
                name="Reported By:", value=f"{ctx.author.mention} | ID: {ctx.author.id}",inline=False)
        embed.add_field(
                name="Channel", value=ctx.channel.mention,inline=False)
        embed.add_field(
                name="Reason", value=reason,inline=False)

        await setchannel.send(embed=embed)
        await ctx.send("Succesfully Reported the User!")
                        
def setup(bot):
    bot.add_cog(Report(bot))
