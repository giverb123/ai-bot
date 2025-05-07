
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils.memory import get_user_memory, update_user_memory
from utils.ai import get_ai_response
from utils.media import get_gif

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    user_id = str(message.author.id)
    content = message.content
    update_user_memory(user_id, {"role": "user", "content": content})
    memory = get_user_memory(user_id)
    reply = get_ai_response(memory, content)
    update_user_memory(user_id, {"role": "assistant", "content": reply})
    await message.channel.send(reply)

@bot.command()
async def gif(ctx, *, query):
    url = get_gif(query)
    await ctx.send(url)

@bot.command()
async def nick(ctx, *, new_name):
    await ctx.guild.me.edit(nick=new_name)
    await ctx.send(f"My new name is **{new_name}**!")

bot.run(os.getenv("DISCORD_TOKEN"))
