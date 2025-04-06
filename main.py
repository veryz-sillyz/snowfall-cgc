from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands
import os
import json
import re
from datetime import timedelta, timezone, datetime
import pytz

load_dotenv()

bot = commands.Bot(command_prefix=".", intents=nextcord.Intents.all())

with open('guilds.json', 'r') as f:
    guilds = json.load(f)

def format_timestamp(timestamp):
    message_time = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(pytz.timezone('Europe/London'))
    now = datetime.now(timezone.utc).astimezone(pytz.timezone('Europe/London'))
    if message_time.date() == now.date():
        return f"Today at {message_time.strftime('%I:%M %p')}"
    elif message_time.date() == (now - timedelta(days=1)).date():
        return f"Yesterday at {message_time.strftime('%I:%M %p')}"
    else:
        return message_time.strftime('%Y-%m-%d at %I:%M %p')

@bot.command()
async def setchannel(ctx: commands.Context, channel: nextcord.TextChannel):
    if ctx.author.guild_permissions.administrator:
        guild_id = ctx.guild.id
        if str(guild_id) not in guilds:
            guilds[str(guild_id)] = []
        if channel.id not in guilds[str(guild_id)]:
            guilds[str(guild_id)].append(channel.id)
            with open('guilds.json', 'w') as f:
                json.dump(guilds, f, indent=4)
            await ctx.send(f"Channel {channel.mention} has been added.")
        else:
            await ctx.send(f"Channel {channel.mention} is already set.")
    else:
        await ctx.send("You don't have permission to execute this command.")

@bot.event
async def on_message(message: nextcord.Message):
    if message.author.bot:
        return
    
    guild_id = message.guild.id
    if str(guild_id) in guilds and message.channel.id in guilds[str(guild_id)]:
        await message.delete()
        
        for guild_id, channels in guilds.items():
            guild = bot.get_guild(int(guild_id))
            if guild:
                for channel_id in channels:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        embed = nextcord.Embed(description=message.content, colour=nextcord.Colour.greyple())
                        embed.set_thumbnail(url=bot.user.avatar.url)
                        embed.set_footer(icon_url=message.guild.icon.url, text=f"{message.guild.name} - CGC Snowfall - {format_timestamp(message.created_at.timestamp())}")
                        embed.set_author(icon_url=message.author.avatar.url, name=f"{message.author.display_name} | {message.author.id}")

                        if message.attachments:
                            embed.set_image(url=message.attachments[0].url)
                        
                        if re.findall(r'https?://\S+', message.content):
                            await message.author.send(embed=nextcord.Embed(title="Alert!", description="You cannot send links on CGC Snowfall.", color=nextcord.Color.red()))
                            return
                        else:
                            await channel.send(embed=embed)

    await bot.process_commands(message)

bot.run(os.getenv("TOKEN"))
