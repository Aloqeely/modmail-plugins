import asyncio
import emoji
import re
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
        
    @reactionrole.command(name="add", aliases=["make"])
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
        
    @reactionrole.command(name="remove", aliases=["delete"])
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
            
#     @reactionrole.command(name="make")
#     @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
#     async def rr_make(self, ctx):
#         """
#         Make a reaction role interactively
#         Note: You can only use the emoji once, you can't use the emoji multiple times.
#         """

#         # checks 
#         def check(msg):
#             return ctx.author == msg.author and ctx.channel == msg.channel

#         def channel_check(msg):
#             return check(msg) and len(msg.channel_mentions) != 0

#         def emoji_and_role_check(msg):
#             return check(msg) and (discord.utils.get(ctx.guild.roles, name=msg.content.strip()[1:].strip()) is not None and 
        
#         # getting the values (inputs) from the user
#         await ctx.send("Alright! In which channel would you like the announcement to be sent? (Make sure to mention the channel)")
#         try:
#             channel_msg = await self.bot.wait_for("message", check=channel_check, timeout=30.0)
#             channel = channel_msg.channel_mentions[0]
#         except asyncio.TimeoutError:
#             return await ctx.send("Too late! The reaction role is canceled.", delete_after=10.0)
#         await ctx.send(f"Ok, so the channel is {channel.mention}. what do you want the message to be? Use | to seperate the title "
#                         "from the description\n **Example:** `This is my title. | This is my description!`")
#         try:
#             title_and_description = await self.bot.wait_for("message", check=check, timeout=120.0)
#             title = ("".join(title_and_description.split("|", 1)[0])).strip()
#             description = ("".join(title_and_description.split("|", 1)[1])).strip()
#         except asyncio.TimeoutError:
#             return await ctx.send("Too late! The reaction role is canceled.", delete_after=10.0)
                
#         await ctx.send("Sweet! Would you like the message to have a color? respond with a hex code if you'd like to or if you don't "
#                        f"Type `{ctx.prefix}none`\nConfused what a hex code is? Check out https://htmlcolorcodes.com/color-picker/")
#         # getting a valid hex
#         valid_hex = False                      
#         while not valid_hex:
#             try:
#                 hex_code = await self.bot.wait_for("message", check=check, timeout=60.0)
#                 if hex_code.content.lower() == "none" or hex_code.content.lower() == f"{ctx.prefix}none":
#                     color = self.bot.main_color
#                     break
#                 valid_hex = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", hex_code.content)
#             except asyncio.TimeoutError:
#                 return await ctx.send("Too late! The reaction role is canceled.", delete_after=10.0)
#             if not valid_hex:
#                 embed = discord.Embed(description="""This doesn't seem like a valid Hex Code!
#                                                    Please enter a **valid** [hex code](https://htmlcolorcodes.com/color-picker)""")
#                 await ctx.send(embed=embed)
#             else:
#                 color = hex_code.content.replace("#", "0x")

#         # forming the embed and sending it to the user
#         embed = discord.Embed(title=title, description=description, timestamp=datetime.datetime.utcnow(), color=color)
#         await ctx.send("Great! the embed should now look like this:", embed=embed)
        

#         await ctx.send("The last step we need to do is picking the roles, The format for adding roles is the emoji then the name of "
#                        f"the role, When you're done type `{ctx.prefix}done`\n**Example:** `🎉 Giveaways`")
#         emojis = []
#         roles = []
#         while True:
#             try:
#                 emoji_and_role = await self.bot.wait_for("message", check=emoji_and_role_check, timeout=60.0)
#                 if emoji_and_role.content.lower() == "done" or emoji_and_role.content.lower() == f"{ctx.prefix}done":
#                     if len(roles) == 0:
#                         await ctx.send("You need to at least specify 1 role for the reaction role")
#                     else:
#                        break
#                 else:
#                     emoji = emoji_and_role.content[0]
#                     role = emoji_and_role.content[1:].strip()
#                     if 
#             except asyncio.TimeoutError:
#                 return await ctx.send("Too late! The reaction role is canceled.", delete_after=10.0)
                  

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
            if state == "locked":
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
