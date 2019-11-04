import re

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class Role(commands.Cog):
    """easily create roles and add them to your members."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def role(self, ctx, member: discord.Member, role: discord.Role):
        """assign a role to a member."""
        await member.add_roles(role)
        await ctx.send("Successfully added the role to the user!")

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def unrole(self, ctx, member: discord.Member, role: discord.Role):
        """remove a role from a member."""
        await member.remove_roles(role)
        await ctx.send("Successfully removed the role from the user!")

    @commands.command(aliases=["makerole"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def createrole(self, ctx, name, color: str=None):
        """create a role."""
        valid = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color)

        if not valid:
            embed = Embed(
                title="Failure",
                description="Please enter a **valid** [hex code](https://htmlcolorcodes.com/color-picker)",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        color = color.replace("#", "0x")
        await ctx.guild.create_role(name=name, color=discord.Color(int(color, 0)))
        await ctx.send("Successfully created the role!")

def setup(bot):
    bot.add_cog(Role(bot))
    
