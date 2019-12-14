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

Emoji = typing.Union[discord.PartialEmoji, UnicodeEmoji]

class ReactionRoles(commands.Cog):
    """Assign roles to your members with Reactions"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        
    @commands.group(name="reactionrole", aliases=["rr"], invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def reactionrole(self, ctx: commands.Context):
        """Assign roles to your members with Reactions"""
        await ctx.send_help(ctx.command)
        
    @reactionrole.command(name="add")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def rr_add(self, ctx, msg_id: int, role: discord.Role, emoji: Emoji, ignored_roles: commands.Greedy[discord.Role]=None):
        """
        Sets Up the Reaction Role
        - Note(s):
        You can only use the emoji once, you can't use the emoji multiple times.
        """

        for channel in ctx.guild.channels:
            try:
                msg = await channel.fetch_message(msg_id)
            except:
                pass
        emote = emoji.name if emoji.id is None else str(emoji.id)
        if ignored_roles:
            blacklist = [role.id for role in ignored_roles]
        else:
            blacklist = None
        await self.db.find_one_and_update(
            {"_id": "config"}, {"$set": {emote: {"role": role.id, "msg_id": msg_id, "ignored_roles": blacklist}}}, upsert=True)
        await msg.add_reaction(emoji)
        await ctx.send("Successfuly set the Reaction Role!")
        
    @reactionrole.command(name="remove")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def rr_remove(self, ctx, emoji: Emoji):
        """delete something from the reaction-role"""
        emote = emoji.name if emoji.id is None else str(emoji.id)
        config = await self.db.find_one({"_id": "config"})
        valid = valid_emoji(emote, config)
        if valid != "valid":
            return await ctx.send(valid)
            
        await self.db.find_one_and_update({"_id": "config"}, {"$unset": {emote: ""}})
        await ctx.send("Successfully removed the role from the reaction-role")
        
    @reactionrole.command(name="lock", aliases="pause", "stop")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def rr_lock(self, ctx, emoji: Emoji, state: str.lower):
        """
        lock a reactionrole to temporary disable it
         - Example(s):
        `{prefix}rr lock 👀 lock`
        `{prefix}rr lock 👀 unlock`
        """
        emote = emoji.name if emoji.id is None else str(emoji.id)
        config = await self.db.find_one({"_id": "config"})
        valid = valid_emoji(emote, config)
        if valid != "valid":
            return await ctx.send(valid)
        
        lock = ["yes", "y", "enable", "true", "lock"]
        unlock = ["no", "n", "disable", "false", "unlock"]
        
        if state in unlock:
            config[emote]["state"] = "unlocked"
            reply = "Succesfully unlocked the reaction role."
        elif state in lock:
            config[emote]["state"] = "locked"
            reply = "Succesfully locked the reaction role."
        else:
            return await ctx.send("invalid state! Valid states: `lock` and `unlock`.")
        
        await self.db.find_one_and_update(
        {"_id": "config"}, {"$set": {emote: config[emote]}}, upsert=True)
        await ctx.send(reply)
            
        
    @reactionrole.group(name="blacklist", aliases=["ignorerole"], invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def blacklist(self, ctx):
        """ignore certain roles from reacting on a reaction-role"""
        await ctx.send_help(ctx.command)
        
    @blacklist.command(name="add")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def blacklist_add(self, ctx, emoji: Emoji, roles: commands.Greedy[discord.Role]):
        """ignore certain roles from reacting."""
        emote = emoji.name if emoji.id is None else str(emoji.id)
        config = await self.db.find_one({"_id": "config"})
        valid = valid_emoji(emote, config)
        if valid != "valid":
            return await ctx.send(valid)
        
        blacklisted_roles = config[emote]["ignored_roles"]
        
        new_blacklist = [role.id for role in roles if role.id not in blacklisted_roles]
        blacklist = blacklisted_roles + new_blacklist
        config[emote]["ignored_roles"] = blacklist
        await self.db.find_one_and_update(
            {"_id": "config"}, {"$set": {emote: config[emote]}}, upsert=True)
        
        ignored_roles = [f"<@&{role}>" for role in blacklist]
        
        embed = discord.Embed(title="Successfully blacklisted the Roles", color=discord.Color.green())
        try:
            embed.add_field(name=f"Current Ignored Roles for {emoji}", value=" ".join(ignored_roles))
        except HTTPException:
            pass
        await ctx.send(embed=embed)
        
    @blacklist.command(name="remove")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def blacklist_remove(self, ctx, emoji: Emoji, roles: commands.Greedy[discord.Role]):
        """allow certain roles to react on a reaction-role they have been blacklisted from."""
        emote = emoji.name if emoji.id is None else str(emoji.id)
        config = await self.db.find_one({"_id": "config"})
        valid = valid_emoji(emote, config)
        if valid != "valid":
            return await ctx.send(valid)
        
        blacklisted_roles = config[emote]["ignored_roles"]
        blacklist = blacklisted_roles.copy()
        [blacklist.remove(role.id) for role in roles if role.id in blacklisted_roles]
        config[emote]["ignored_roles"] = blacklist
        await self.db.find_one_and_update(
            {"_id": "config"}, {"$set": {emote: config[emote]}}, upsert=True)
        
        ignored_roles = [f"<@&{role}>" for role in blacklist]
        
        embed = discord.Embed(title="Succesfully removed the Roles", color=discord.Color.green())
        try:
            embed.add_field(name=f"Current Ignored Roles for {emoji}", value=" ".join(ignored_roles))
        except:
            pass
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.guild_id:
            return
        
        config = await self.db.find_one({"_id": "config"})
        emote = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        emoji = payload.emoji.name if payload.emoji.id is None else payload.emoji
        guild = self.bot.get_guild(payload.guild_id)
        member = discord.utils.get(guild.members, id=payload.user_id)
        try:
            msg_id = config[emote]["msg_id"]
        except (KeyError, TypeError):
            return
        
        if payload.message_id != int(msg_id):
            return
        
        try:
            ignored_roles = config[emote]["ignored_roles"]
            for role_id in ignored_roles:
                role = discord.utils.get(guild.roles, id=role_id)
                if role in member.roles:
                    ch = self.bot.get_channel(payload.channel_id)
                    msg = await ch.fetch_message(payload.message_id)
                    reaction = discord.utils.get(msg.reactions, emoji=emoji)
                    await reaction.remove(member)
                    return
        except (KeyError, TypeError):
            pass
        try:
            state = config[emote]["state"]
            if state == "locked"
            return
        except (KeyError, TypeError):
            pass
        
        rrole = config[emote]["role"]
        role = discord.utils.get(guild.roles, id=int(rrole))

        if role:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id is None:
            return
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

            if role:
                member = discord.utils.get(guild.members, id=payload.user_id)
                await member.remove_roles(role)
                                  
    def valid_emoji(self, emoji, config):
        try:
            emoji = config[emoji]
            return "valid"
        except (KeyError, TypeError):
            return "There's no reaction role set with this emoji"
    
                
def setup(bot):
    bot.add_cog(ReactionRoles(bot))
