import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class ServerStats(commands.Cog): 
    """Interesting and accurate statistics about your server."""
    
    def __init__(self, bot):
        self.bot = bot
        self.c_name = "📊 | Server Info"
        self.db = bot.plugin_db.get_partition(self)
        
    @commands.command() 
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def vcsetup(self, ctx):
        """Sets up all the server stats Voice Channels."""

        if discord.utils.find(lambda c: c.name == self.c_name, ctx.guild.categories) is None:
            category = await ctx.guild.create_category(name=self.c_name, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)})

            await self.create_channel(ctx, "Member Count", ctx.guild.member_count)
            await self.create_channel(ctx, "Role Count", len(ctx.guild.roles))
            await self.create_channel(ctx, "Channel Count", len(ctx.guild.channels))

            self.db.find_one_and_update({"_id": "config"}, {"$set": {"mChannel": "Member Count"}}, upsert=True)
            self.db.find_one_and_update({"_id": "config"}, {"$set": {"rChannel": "Role Count"}}, upsert=True)
            self.db.find_one_and_update({"_id": "config"}, {"$set": {"cChannel": "Channel Count"}}, upsert=True)
            
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def membercount(self, ctx, *, name: str = None):
        """Sets up the Member Count Voice Channel."""

        if name is None:
            name = "Member Count"

        message = await self.create_channel(ctx, name, ctx.guild.member_count)
        await ctx.send(message)

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"mChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def rolecount(self, ctx, *, name: str=None):
        """Sets up the Role Count Voice Channel.""" 

        if name is None:
            name = "Role Count"

        message = await self.create_channel(ctx, name, len(ctx.guild.roles))
        await ctx.send(message)

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"rChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def channelcount(self, ctx, *, name: str=None):
        """Sets up the Channel Count Voice Channel"""

        if name is None:
            name = "Channel Count"

        message = await self.create_channel(ctx, name, len(ctx.guild.channels))
        await ctx.send(message)

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"cChannel": name}}, upsert=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        voice_channels = await self.db.find_one({"_id": "config"})
        try:
            member_vc = voice_channels["mChannel"]
        except:
            return

        await self.update_channel(member, member_vc, member.guild.member_count)  
        
    @commands.Cog.listener()   
    async def on_member_remove(self, member):
        voice_channels = await self.db.find_one({"_id": "config"})
        try:
            member_vc = voice_channels["mChannel"]
        except:
            return
        
        await self.update_channel(member, member_vc, member.guild.member_count)  

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        voice_channels = await self.db.find_one({"_id": "config"})
        try:
            role_vc = voice_channels["rChannel"]
        except:
            return
        
        await self.update_channel(role, role_vc, len(role.guild.roles))

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        voice_channels = await self.db.find_one({"_id": "config"})
        try:
            role_vc = voice_channels["rChannel"]
        except:
            return

        await self.update_channel(role, role_vc, len(role.guild.roles))

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        voice_channels = await self.db.find_one({"_id": "config"})
        try:
            channel_vc = voice_channels["cChannel"]
        except:
            return
        await self.update_channel(channel, channel_vc, len(channel.guild.channels))

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        voice_channels = await self.db.find_one({"_id": "config"})
        try:
            channel_vc = voice_channels["cChannel"]
        except:
            return
        
        await self.update_channel(channel, channel_vc, len(channel.guild.channels))
    
    async def create_channel(self, ctx, name, count): 
        if discord.utils.find(lambda c: c.name.startswith(f"{name}:"), ctx.guild.channels) is None:
            category = discord.utils.find(lambda c: c.name == self.c_name, ctx.guild.categories)
            if category is None:
                category = await ctx.guild.create_category(name=self.c_name, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)})

            await ctx.guild.create_voice_channel(name=f"{name}: {count}", category=category)
            return f"The {name.lower()} channel has been set up."
        
        return f"The {name.lower()} channel has already been set up."
    
    async def update_channel(self, ctx, name, count):
        category = discord.utils.find(lambda c: c.name == self.c_name, ctx.guild.categories)
        if category is None:
            return

        channel = discord.utils.find(lambda c: c.name.startswith(f"{name}:"), ctx.guild.channels)
        if channel is None or not isinstance(channel, discord.VoiceChannel):
            return
        
        if channel.category != category:
            return
        
        await channel.edit(name=f"{name}: {count}")


def setup(bot):
    bot.add_cog(ServerStats(bot))
