import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class ReactionRoles(commands.Cog):
    """Assign roles to your members with Reactions"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @commands.command(aliases=["rr"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def reactionrole(self, ctx, channel_id, role: discord.Role, emoji: discord.Emoji):
        """Sets Up the Reaction Role\nNote: the reaction role **ONLY** works in one channel, you **Cannot** use multiple Channels for it!"""
        await self.db.find_one_and_update(
                {"_id": "config"}, {"$set": {emoji.name: role.id}}, upsert=True
            )
        await self.db.find_one_and_update(
                {"_id": "config"}, {"$set": {"rr_channel": channel_id}}, upsert=True
            )            
        channel = discord.utils.get(ctx.guild.text_channels, id=int(channel_id))
        msg = await channel.fetch_message(message_id)
        await msg.add_reaction(emoji)
        await ctx.send("Successfuly set the Reaction Role!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        config = await self.db.find_one({"_id": "config"})
        channel_id = config["rr_channel"]
        if payload.channel_id == int(channel_id):
            guild = discord.utils.get(self.bot.guilds, id=payload.guild_id)
            rrole = config[payload.emoji.name]
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
            rrole = config[payload.emoji.name]
            role = discord.utils.get(guild.roles, id=rrole)

            if role is not None:
                member = discord.utils.get(guild.members, id=payload.user_id)
                await member.remove_roles(role)

                
def setup(bot):
    bot.add_cog(ReactionRoles(bot))
