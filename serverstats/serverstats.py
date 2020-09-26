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
        self.db = bot.api.get_plugin_partition(self)
        
    @commands.command() 
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def vcsetup(self, ctx):
        """Sets up all the server stats Voice Channels."""

        if discord.utils.find(lambda c: c.name == self.c_name, ctx.guild.categories) is None:
            category = await ctx.guild.create_category(name=self.c_name, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)})
            await category.edit(position=0)
            humans = self.get_humans(ctx)
            bots = self.get_bots(ctx)
            names = ["Member Count", "Role Count", "Channel Count", "Total Humans", "Total Bots"]
            counts = [ctx.guild.member_count, len(ctx.guild.roles), len(ctx.guild.channels), humans, bots]
            checks = ["m", "r", "c", "h", "b"]
            for name, count, check in zip(names, counts, checks):
                await self.create_channel(ctx, name, count)
                self.db.find_one_and_update({"_id": "config"}, {"$set": {f"{check}Channel": name}}, upsert=True)
            
            embed = discord.Embed(color = discord.Color.green())
            embed.add_field(name="Success", value="Successfully Setup all the Server Info Voice Channels!")
            embed.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embed)
            
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def membercount(self, ctx, *, name: str=None):
        """Sets up the Member Count Voice Channel."""

        name = name or "Member Count"
        await self.create_channel(ctx, name, ctx.guild.member_count)

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"mChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def rolecount(self, ctx, *, name: str=None):
        """Sets up the Role Count Voice Channel.""" 

        name = name or "Role Count"
        await self.create_channel(ctx, name, len(ctx.guild.roles))

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"rChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def channelcount(self, ctx, *, name: str=None):
        """Sets up the Channel Count Voice Channel"""

        name = name or "Channel Count"
        await self.create_channel(ctx, name, len(ctx.guild.channels))

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"cChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def totalhuman(self, ctx, *, name: str=None):
        """Sets up the Total Humans Voice Channel"""

        name = name or "Total Humans"
        humans = self.get_humans(ctx)
        await self.create_channel(ctx, name, int(humans))

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"hChannel": name}}, upsert=True)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def totalbot(self, ctx, *, name: str=None):
        """Sets up the Total Bots Voice Channel"""
        
        name = name or "Total Bots"
        bots = self.get_bots(ctx)
        await self.create_channel(ctx, name, int(bots))

        self.db.find_one_and_update({"_id": "config"}, {"$set": {"bChannel": name}}, upsert=True)
        
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def fixvc(self, ctx):
        """Fix broken VC counts"""
        guild = ctx.guild
        humans = self.get_humans(ctx)
        bots = self.get_bots(ctx)
        doc = await self.db.find_one({'_id':'config'})
        setkeys = list(doc.keys())
        checks = ["m", "r", "c", "h", "b"]
        matching = [guild.member_count, len(guild.roles), len(guild.channels), humans, bots]
        for check in checks:
            if f"{check}Channel" in setkeys:
                num = checks.index(check)
                value = matching[num] 
                await self.update_channel(ctx, doc[f'{check}Channel'], value)
        await ctx.send('Fixed all Counts!')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        voice_channels = await self.db.find_one({"_id": "config"})
        humans = self.get_humans(member)
        bots = self.get_bots(member)
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
        humans = self.get_humans(member)
        bots = self.get_bots(member)
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
        embed = discord.Embed(timestamp = datetime.datetime.utcnow())
        if discord.utils.find(lambda c: c.name.startswith(name), ctx.guild.channels) is None:
            category = discord.utils.find(lambda c: c.name == self.c_name, ctx.guild.categories)
            if category is None:
                category = await ctx.guild.create_category(name=self.c_name, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(connect=False)})
                await category.edit(position=0)
            await ctx.guild.create_voice_channel(name=f"{name}: {count}", category=category)
            embed.add_field(name="Success", value= f"The {name} Channel has been set up.")
            embed.color = discord.Color.green()
            await ctx.send(embed=embed)
            return
        
        embed.add_field(name="Failure", value= f"The {name} channel has already been set up.")
        embed.color = discord.Color.red()
        await ctx.send(embed=embed)
        return 
    
    async def update_channel(self, ctx, name, count):
        channel = discord.utils.find(lambda c: c.name.startswith(name), ctx.guild.channels)
        if channel is None or not isinstance(channel, discord.VoiceChannel):
            return
        
        name = "".join([i for i in channel.name if not i.isdigit()])
    
        await channel.edit(name=f"{name.strip()} {count}")
        
    def get_bots(self, ctx):
        bots = [member for member in ctx.guild.members if member.bot]
        return len(bots)
    
    def get_humans(self, ctx):
        humans = [member for member in ctx.guild.members if not member.bot]
        return len(humans)
    
def setup(bot):
    bot.add_cog(ServerStats(bot))
