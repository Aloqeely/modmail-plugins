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

    @commands.command(aliases=["rchannel"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def reportchannel(self, ctx, channel: discord.TextChannel):
        """Set the reports channel"""
        await self.db.find_one_and_update({"_id": "config"}, {"$set": {"report_channel": channel.id}}, upsert=True)
        
        embed = discord.Embed(color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Set Channel", value=f"Successfully set the reports channel to {channel.mention}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=["rmention"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def reportmention(self, ctx, *, mention: str):
        """Sets the report mention"""
        await self.db.find_one_and_update({"_id": "config"}, {"$set": {"report_mention": mention}}, upsert=True)
        
        embed = discord.Embed(color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Changed Mention", value=f"Successfully changed the report mention to {mention}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def report(self, ctx, user: discord.Member, *, reason: str):
        """Report member's bad behavior"""
        config = await self.db.find_one({"_id": "config"})
        report_channel = config["report_channel"]
        setchannel = discord.utils.get(ctx.guild.channels, id=int(report_channel))
        
        try:
            report_mention = config["report_mention"]
        except KeyError:
            report_mention = ""
            
        embed = discord.Embed(color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        
        embed.add_field(name="Reported user", value=f"{user.mention} | ID: {user.id}", inline=False)
        embed.add_field(name="Reported by:", value=f"{ctx.author.mention} | ID: {ctx.author.id}", inline=False)
        embed.add_field(name="Channel", value=ctx.channel.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)

        await setchannel.send(report_mention, embed=embed)
        await ctx.send("Succesfully reported the user!")
                        
def setup(bot):
    bot.add_cog(Report(bot))
