import asyncio
import emoji
import typing

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class UnicodeEmoji(commands.Converter):
    async def convert(self, ctx, argument):
        if argument in emoji.UNICODE_EMOJI:
            return discord.PartialEmoji(name=argument, animated=False)
        raise commands.BadArgument('Unknown emoji')

class ReactionRoles(commands.Cog):
    """Assign roles to your members with Reactions"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
    @commands.group(name="reactionrole", aliases=["rr"], invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def reactionrole(self, ctx: commands.Context):
        """Assign roles to your members with Reactions
        """
        await ctx.send_help(ctx.command)
        
    @reactionrole.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def add(self, ctx, msg_id: int, role: discord.Role, emoji: typing.Union[discord.PartialEmoji, UnicodeEmoji]):
        """Sets Up the Reaction Role
        """

        for channel in ctx.guild.channels:
            try:
                msg = await channel.fetch_message(msg_id)
            except:
                pass
        await self.db.find_one_and_update(
                {"_id": "config"}, {"$set": {str(emoji.id): {"role": role.id, "msg_id": msg_id}}}, upsert=True
            )
        await msg.add_reaction(emoji)
        await ctx.send("Successfuly set the Reaction Role!")
        
    @reactionrole.command(aliases=["delete"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def remove(self, ctx, emoji: typing.Union[discord.PartialEmoji, UnicodeEmoji]):
        """remove something from the reaction-role
        """
        
        await self.db.find_one_and_update({"_id": "config"}, {"$unset": {str(emoji.id): ""}})

        await ctx.send("Successfully removed the role from the reaction-role")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        config = await self.db.find_one({"_id": "config"})
        try:
            msg_id = config[str(payload.emoji.id)]["msg_id"]
        except KeyError:
            return
                                                              
        if payload.message_id == int(msg_id):
            guild = self.bot.get_guild(payload.guild_id)
            rrole = config[str(payload.emoji.id)]["role"]
            role = discord.utils.get(guild.roles, id=int(rrole))

            if role is not None:
                member = self.bot.get_user(payload.user_id)
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        config = await self.db.find_one({"_id": "config"})
        try:
            msg_id = config[str(payload.emoji.id)]["msg_id"]
        except KeyError:
            return
                                                              
        if payload.message_id == int(msg_id):
            guild = self.bot.get_guild(payload.guild_id)
            rrole = config[str(payload.emoji.id)]["role"]
            role = discord.utils.get(guild.roles, id=int(rrole))

            if role is not None:
                member = self.bot.get_user(payload.user_id)
                await member.remove_roles(role)

                
def setup(bot):
    bot.add_cog(ReactionRoles(bot))
