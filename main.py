import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils.memory import get_user_memory, update_user_memory
from utils.ai import get_ai_response
from utils.media import get_gif, save_gif_for_user, extract_gif_url
from flask import Flask
import threading

# Load environment variables
load_dotenv()

# Setup Discord bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user = message.author
    user_id = str(user.id)
    username = user.name
    display_name = user.display_name
    avatar_url = user.avatar.url if user.avatar else None
    created_at = user.created_at.strftime("%Y-%m-%d")
    joined_at = message.guild.get_member(user.id).joined_at.strftime("%Y-%m-%d") if message.guild else "Unknown"
    bio = getattr(user, "bio", "Unavailable")  # bio is only accessible in user profile, not always available
    status = str(user.status)

    content = message.content

    # Detect media
    media_urls = []
    for word in content.split():
        if word.startswith("http") and any(ext in word for ext in ['.gif', '.jpg', '.jpeg', '.png', '.mp4', '.webm']):
            media_urls.append(word)

    for attachment in message.attachments:
        if attachment.content_type and any(mt in attachment.content_type for mt in ['gif', 'image', 'video']):
            media_urls.append(attachment.url)

    # Describe media
    media_description = ""
    if media_urls:
        media_description = "\n\nMedia shared:\n" + "\n".join(media_urls)

    # Update memory
    update_user_memory(user_id, {
        "role": "user",
        "username": username,
        "nickname": display_name,
        "avatar_url": avatar_url,
        "account_created": created_at,
        "joined_server": joined_at,
        "bio": bio,
        "status": status,
        "content": content + media_description
    })

    memory = get_user_memory(user_id)
    prompt = f"{display_name} says: {content}" + (media_description if media_description else "")
    reply = get_ai_response(memory, prompt)

    update_user_memory(user_id, {"role": "assistant", "content": reply})
    await message.channel.send(reply)

    # Save GIFs
    if gif_url := extract_gif_url(content):
        save_gif_for_user(user_id, gif_url)
    for attachment in message.attachments:
        if attachment.content_type and 'gif' in attachment.content_type:
            save_gif_for_user(user_id, attachment.url)

    await bot.process_commands(message)

@bot.command()
async def gif(ctx, *, query):
    url = get_gif(query)
    await ctx.send(url)

@bot.command()
async def nick(ctx, *, new_name):
    await ctx.guild.me.edit(nick=new_name)
    await ctx.send(f"My new name is **{new_name}**!")

# Web server setup for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Run web server in background
threading.Thread(target=run_web).start()

# Start the bot
bot.run(os.getenv("DISCORD_TOKEN"))
