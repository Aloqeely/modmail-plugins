import re
import typing

from types import SimpleNamespace

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class Role(commands.Cog):
    """Easily create roles and add them to your members."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def role(self, ctx, role: discord.Role, member: discord.Member=None):
        """Assign a role to a member."""
        if member is None:
            try:
                member = ctx.guild.get_member(int(ctx.channel.topic[9:]))
            except (ValueError, TypeError):
                raise commands.MissingRequiredArgument(SimpleNamespace(name="role"))
        
        if role.position > ctx.author.roles[-1].position:
            return await ctx.send("You do not have permissions to give this role.")
        
        await member.add_roles(role)
        await ctx.send(f"Successfully added the role to {member.name}!")

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def unrole(self, ctx, role: discord.Role, member: discord.Member=None):
        """Remove a role from a member."""
        if member is None:
            try:
                member = ctx.guild.get_member(int(ctx.channel.topic[9:]))
            except (ValueError, TypeError):
                raise commands.MissingRequiredArgument(SimpleNamespace(name="unrole"))
            
        if role.position > ctx.author.roles[-1].position:
            return await ctx.send("You do not have permissions to remove this role.")
        
        await member.remove_roles(role)
        await ctx.send(f"Successfully removed the role from {member.name}!")

    @commands.command(aliases=["makerole"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def createrole(self, ctx, name: str, color: str):
        """create a role."""
        color = "#" + color.strip("#")
        
        valid = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color)
        if not valid:
            embed = discord.Embed(title="Failure", color=self.bot.main_color,
                description="Please enter a **valid [hex code](https://htmlcolorcodes.com/color-picker)**")
            return await ctx.send(embed=embed)

        await ctx.guild.create_role(name=name, color=discord.Color(int(color.replace("#", "0x"), 0)))
        await ctx.send("Successfully created the role!")

def setup(bot):
    bot.add_cog(Role(bot))
    
