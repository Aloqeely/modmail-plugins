import datetime

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
            humans = 0
            bots = 0
            for user in ctx.guild.members:
                if user.bot:
                    bots += 1
                else:
                    humans += 1
                    
            await self.create_channel(ctx, "Member Count", ctx.guild.member_count)
            await self.create_channel(ctx, "Role Count", len(ctx.guild.roles))
            await self.create_channel(ctx, "Channel Count", len(ctx.guild.channels))
            await self.create_channel(ctx, "Total Humans", int(humans))
            await self.create_channel(ctx, "Total Bots", int(bots))

            self.db.find_one_and_update({"_id": "config"}, {"$set": {"mChannel": "Member Count"}}, upsert=True)
            self.db.find_one_and_update({"_id": "config"}, {"$set": {"rChannel": "Role Count"}}, upsert=True)
            self.db.find_one_and_update({"_id": "config"}, {"$set": {"cChannel": "Channel Count"}}, upsert=True)
            self.db.find_one_and_update({"_id": "config"}, {"$set": {"hChannel": "Total Humans"}}, upsert=True)
            self.db.find_one_and_update({"_id": "config"}, {"$set": {"bChannel": "Total Bots"}}, upsert=True)
            
            embed = discord.Embed(color = discord.Color.green())
            embed.add_field(name="Success", value="Successfully Setup all the Server Info Voice Channels!")
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embed)
            
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def membercount(self, ctx, *, name: str = None):
        """Sets up the Member Count Voice Channel."""

        if name is None:
            name = "Member Count"

        await self.create_channel(ctx, name, ctx.guild.member_count)

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"mChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def rolecount(self, ctx, *, name: str=None):
        """Sets up the Role Count Voice Channel.""" 

        if name is None:
            name = "Role Count"

        await self.create_channel(ctx, name, len(ctx.guild.roles))

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"rChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def channelcount(self, ctx, *, name: str=None):
        """Sets up the Channel Count Voice Channel"""

        if name is None:
            name = "Channel Count"

        await self.create_channel(ctx, name, len(ctx.guild.channels))

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"cChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def totalhuman(self, ctx, *, name: str=None):
        """Sets up the Total Humans Voice Channel"""

        if name is None:
            name = "Total Humans"
        humans = 0
        for user in ctx.guild.members:
            if not user.bot:
                humans += 1
            else:
                continue

        await self.create_channel(ctx, name, int(humans))

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"hChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def totalbot(self, ctx, *, name: str=None):
        """Sets up the Total Bots Voice Channel"""
        
        if name is None:
            name = "Total Bots"
        bots = 0
        for user in ctx.guild.members:
            if user.bot:
                bots += 1
            else:
                continue

        await self.create_channel(ctx, name, int(bots))

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"bChannel": name}}, upsert=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        voice_channels = await self.db.find_one({"_id": "config"})
        humans = 0
        bots = 0
        for user in member.guild.members:
            if user.bot:
                bots += 1
            else:
                humans += 1
        try:
            member_vc = voice_channels["mChannel"]
            await self.update_channel(member, member_vc, member.guild.member_count)  
        except:
            pass
        try:
            human_vc = voice_channels["hChannel"]
            await self.update_channel(member, human_vc, humans)  
        except:
            pass
        try:
            bot_vc = voice_channels["bChannel"]
            await self.update_channel(member, bot_vc, bots)  
        except:
            return
   
    @commands.Cog.listener()   
    async def on_member_remove(self, member):
        voice_channels = await self.db.find_one({"_id": "config"})
        humans = 0
        bots = 0
        for user in member.guild.members:
            if user.bot:
                bots += 1
            else:
                humans += 1
        try:
            member_vc = voice_channels["mChannel"]
            await self.update_channel(member, member_vc, member.guild.member_count)  
        except:
            pass
        try:
            human_vc = voice_channels["hChannel"]
            await self.update_channel(member, human_vc, humans)  
        except:
            pass
        try:
            bot_vc = voice_channels["bChannel"]
            await self.update_channel(member, bot_vc, bots)  
        except:
            return

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
        embed = discord.Embed()
        embed.timestamp = datetime.datetime.utcnow()
        if discord.utils.find(lambda c: c.name.startswith(f"{name}:"), ctx.guild.channels) is None:
            category = discord.utils.find(lambda c: c.name == self.c_name, ctx.guild.categories)
            if category is None:
                category = await ctx.guild.create_category(name=self.c_name, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)})

            await ctx.guild.create_voice_channel(name=f"{name}: {count}", category=category)
            embed.add_field(name="Success", value= f"The {name} Channel has been set up.")
            embed.color = discord.Color.green()
            await ctx.send(embed=embed)
            return
        
        embed.add_field(name="Faliure", value= f"The {name} channel has already been set up.")
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return 
    
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
        
    def get_bots(self, ctx):
        bots = [member for member in ctx.guild.members if member.bot]
        return len(bots)
    
    def get_humans(self, ctx):
        humans = [member for member in ctx.guild.members if not member.bot]
        return len(humans)
    
def setup(bot):
    bot.add_cog(ServerStats(bot))
