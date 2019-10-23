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
        self.Emoji = typing.Union[discord.PartialEmoji, UnicodeEmoji]
        
    @commands.group(name="reactionrole", aliases=["rr"], invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def reactionrole(self, ctx: commands.Context):
        """Assign roles to your members with Reactions"""
        await ctx.send_help(ctx.command)
        
    @reactionrole.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def add(self, ctx, msg_id: int, role: discord.Role, emoji: self.Emoji, *, ignored_roles: commands.Greedy[discord.Role]):
        """Sets Up the Reaction Role"""

        for channel in ctx.guild.channels:
            try:
                msg = await channel.fetch_message(msg_id)
            except:
                pass
        emote = emoji.name if emoji.id is None else str(emoji.id)
        await self.db.find_one_and_update(
            {"_id": "config"}, {"$set": {emote: {"role": role.id, "msg_id": msg_id, "ignored_roles": ignored_roles}}}, upsert=True)
        await msg.add_reaction(emoji)
        await ctx.send("Successfuly set the Reaction Role!")
        
    @reactionrole.command(aliases=["delete"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def remove(self, ctx, emoji: self.Emoji):
        """remove something from the reaction-role"""
        emote = emoji.name if emoji.id is None else str(emoji.id)
            
        await self.db.find_one_and_update({"_id": "config"}, {"$unset": {emote: ""}})
        await ctx.send("Successfully removed the role from the reaction-role")
        
    @reactionrole.group(name="blacklist", aliases=["ignore"], invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def blacklist(self, ctx: commands.Context):
        """ignore certain roles from reacting on a reaction-role"""
        await ctx.send_help(ctx.command)
        
    @blacklist.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def add(self, ctx, emoji: self.Emoji, *, roles: commands.Greedy[discord.role]):
        """ignore certain roles from reacting."""
        emote = emoji.name if emoji.id is None else str(emoji.id)
        config = await self.db.find_one({"_id": "config"})
        blacklisted_roles = config[emoji]["ignored_roles"]
        
        new_blacklist = [role.id for role in roles if role.id not in blacklisted_roles]
        blacklist = blacklisted_roles + new_blacklist
        config[emote]["ignored_roles"] = blacklist
        
        ignored_roles = [f"<@&{role}>" for role in blacklist]
        
        embed = discord.Embed(title="Blacklist", description=f"Successfully added to the blacklist!", color=discord.Color.green())
        embed.add_field(name=f"Current Ignored Roles for {emoji}", value=" ".join(ignored_roles))
        await ctx.send(embed=embed)
        
    @blacklist.command(aliases=["delete"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def remove(self, ctx, emoji: self.Emoji, *, roles: commands.Greedy[discord.role]):
        """allow certain roles to react on a reaction-role they have been blacklisted from."""
        emote = emoji.name if emoji.id is None else str(emoji.id)
        config = await self.db.find_one({"_id": "config"})
        blacklisted_roles = config[emoji]["ignored_roles"]
        blacklist = blacklisted_roles.copy()
        [blacklist.remove(role.id) for role in roles if role.id in blacklisted_roles]
        config[emote]["ignored_roles"] = blacklist
        
        ignored_roles = [f"<@&{role}>" for role in blacklist]
        
        embed = discord.Embed(title="Blacklist", description=f"Successfully removed from the blacklist!", color=discord.Color.green())
        embed.add_field(name=f"Current Ignored Roles for {emoji}", value=" ".join(ignored_roles))
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        config = await self.db.find_one({"_id": "config"})
        emote = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        guild = self.bot.get_guild(payload.guild_id)
        member = discord.utils.get(guild.members, id=payload.user_id)
        try:
            msg_id = config[emote]["msg_id"]
        except (KeyError, TypeError):
            return
        try:
            ignored_roles = config[emote]["ignored_roles"]
            for role_id in ignored_roles
                role = discord.utils.get(guild.roles, id=role_id)
                if role in ctx.author.roles: return
        except:
            pass
        if payload.message_id == int(msg_id):
            rrole = config[emote]["role"]
            role = discord.utils.get(guild.roles, id=int(rrole))
            
            if role is not None:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        config = await self.db.find_one({"_id": "config"})
        emote = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        try:
            msg_id = config[emote]["msg_id"]
        except (KeyError, TypeError):
            return
                                                              
        if payload.message_id == int(msg_id):
            guild = self.bot.get_guild(payload.guild_id)
            rrole = config[emote]["role"]
            role = discord.utils.get(guild.roles, id=int(rrole))

            if role is not None:
                member = discord.utils.get(guild.members, id=payload.user_id)
                await member.remove_roles(role)
                
def setup(bot):
    bot.add_cog(ReactionRoles(bot))
