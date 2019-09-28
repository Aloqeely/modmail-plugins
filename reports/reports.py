import discord
from discord.ext import commands
import datetime

from core import checks
from core.models import PermissionLevel

class Report(commands.Cog): 
    """An easy system for your members to report bad behavior"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def reportchannel(self, ctx, channel: discord.TextChannel):
        """Set the Reports Channel"""
        await self.db.find_one_and_update(
                {"_id": "config"}, {"$set": {"report_channel": channel.name}}
            )
        await ctx.send("Successfully set the Reports channel!")

    @commands.command()
    async def report(self, ctx, user: discord.Member, *, reason):
        """Report a user"""
        embed = discord.Embed(
                    color=discord.Color.red())
        embed.set_author(name=f"{ctx.author.name}",icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"{datetime.datetime.today().strftime('%A %b %d | %I:%M %p')}")
        embed.add_field(
                name="Reported User", value=f"{user.mention} | ID: {user.id}",inline=False)
        embed.add_field(
                name="Reported by:", value=f"{ctx.author.mention} | ID: {ctx.author.id}",inline=False)
        embed.add_field(
                name="Channel", value=f"{ctx.channel.mention}",inline=False)
        embed.add_field(
                name="Reason", value=reason,inline=False)
                         
        config = await self.db.find_one({"_id": "config"})
        report_channel = config["report_channel"]
        if report_channel is not None:
            setchannel = discord.utils.get(ctx.guild.channels, name=report_channel)
        else:
            setchannel = discord.utils.get(ctx.guild.channels, name="reports")
        await setchannel.send(embed=embed)
        await ctx.send("Succesfully Reported the User!")
                        
def setup(bot):
    bot.add_cog(Report(bot))
