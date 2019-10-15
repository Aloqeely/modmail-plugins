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
    async def add(self, ctx, channel: discord.TextChannel, role: discord.Role, emoji: typing.Union[discord.PartialEmoji, UnicodeEmoji]):
        """Sets Up the Reaction Role
        **Note**: the reaction role **ONLY** works for one channel, you **Cannot** set it for multiple channels!
        """
        await ctx.send("Send the Message ID of the message that you want to hold the reaction role")
        
        def check(id: int):
            return id.author == ctx.author and id.channel == ctx.channel

        try:
            id = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send('Reaction Role Canceled!')
        
        await self.db.find_one_and_update(
                {"_id": "config"}, {"$set": {str(emoji.id): role.id}}, upsert=True
            )
        await self.db.find_one_and_update(
                {"_id": "config"}, {"$set": {"rr_channel": channel.id}}, upsert=True
            )         

        msg = await channel.fetch_message(int(id.content))
        await msg.add_reaction(emoji)
        await ctx.send("Successfuly set the Reaction Role!")
        
    @reactionrole.command(aliases=["delete"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def remove(self, ctx, role: discord.Role, emoji: typing.Union[discord.PartialEmoji, UnicodeEmoji]):
        """remove something from the reaction-role
        """
        config = await self.db.find_one({"_id": "config"})
        
        if config is None:
            return await ctx.send("successfully removed the role from the reaction-role")
        
        await self.db.delete_one({str(emoji.id): role.id})

        await ctx.send("successfully removed the role from the reaction-role")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        config = await self.db.find_one({"_id": "config"})
        channel_id = config["rr_channel"]
        if payload.channel_id == int(channel_id):
            guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
            rrole = config[str(payload.emoji.id)]
            role = discord.utils.get(guild.roles, id=int(rrole))

            if role is not None:
                member = discord.utils.get(guild.members, id=payload.user_id)
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        config = await self.db.find_one({"_id": "config"})
        channel_id = config["rr_channel"]
        if payload.channel_id == int(channel_id):
            guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
            rrole = config[str(payload.emoji.id)]
            role = discord.utils.get(guild.roles, id=int(rrole))

            if role is not None:
                member = discord.utils.get(guild.members, id=payload.user_id)
                await member.remove_roles(role)

                
def setup(bot):
    bot.add_cog(ReactionRoles(bot))
