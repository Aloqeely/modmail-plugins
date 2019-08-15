import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

class ServerStats(commands.Cog): 
    """Interesting and accurate statistics about your server."""
    
    def __init__(self, bot):
        self.bot = bot
        self.c_name = "📊 | Server Info"

    @commands.command() 
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def vcsetup(self, ctx):
        """Sets up all the server stats Voice Channels."""

        if discord.utils.find(lambda c: c.name == self.c_name, ctx.guild.categories) is None:
            category = await ctx.guild.create_category(name=self.c_name, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)})

            await self.create_channel(ctx, "Member Count", ctx.guild.member_count)
            await self.create_channel(ctx, "Role Count", len(ctx.guild.roles))
            await self.create_channel(ctx, "Channel Count", len([c for c in channel.guild.channel if isinstance(c, discord.TextChannel)]))

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def membercount(self, ctx):
        """Sets up the Member Count Voice Channel."""

        message = await self.create_channel(ctx, "Member Count", ctx.guild.member_count)
        await ctx.send(message)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def rolecount(self, ctx):
        """Sets up the Role Count Voice Channel."""

        message = await self.create_channel(ctx, "Role Count", len(ctx.guild.roles))
        await ctx.send(message)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def channelcount(self, ctx):
        """Sets up the Channel Count Voice Channel"""

        message = await self.create_channel(ctx, "Channel Count", len([c for c in channel.guild.channel if isinstance(c, discord.TextChannel)]))
        await ctx.send(message)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.update_channel(member, "Member Count", member.guild.member_count)  
        
    @commands.Cog.listener()   
    async def on_member_remove(self, member):
        await self.update_channel(member, "Member Count", member.guild.member_count)  

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await self.update_channel(role, "Role Count", len(role.guild.roles))

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.update_channel(role, "Role Count", len(role.guild.roles))

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await self.update_channel(channel, "Channel Count", len([c for c in channel.guild.channel if isinstance(c, discord.TextChannel)]))

    @commands.Cog.listener()
    async def on_guild_channel_delete(self):
        await self.update_channel(channel, "Channel Count", len([c for c in channel.guild.channel if isinstance(c, discord.TextChannel)]))
    
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
