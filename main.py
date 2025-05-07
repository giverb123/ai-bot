import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils.memory import get_user_memory, update_user_memory
from utils.ai import get_ai_response
from utils.media import get_gif, save_gif_for_user, extract_gif_url
from utils.vision import describe_image
from utils.tts import generate_tts  # Import the TTS module
from flask import Flask
import threading

# Load environment variables
load_dotenv()

# Load the TTS model choice from environment
TTS_MODEL = os.getenv("TTS_MODEL", "bark")  # Default to 'bark', switchable to 'tortoise'

# Setup Discord bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online.", flush=True)

@bot.event
async def on_message(message):
    await bot.process_commands(message)  # Allow commands to be processed

    if message.author.bot:
        return

    try:
        print(f"Received message from {message.author}: {message.content}", flush=True)

        user = message.author
        user_id = str(user.id)
        username = user.name
        display_name = user.display_name
        avatar_url = user.avatar.url if user.avatar else None
        created_at = user.created_at.strftime("%Y-%m-%d")
        joined_at = message.guild.get_member(user.id).joined_at.strftime("%Y-%m-%d") if message.guild else "Unknown"
        bio = getattr(user, "bio", "Unavailable")
        status = str(user.status)
        content = message.content

        # Detect media (images, GIFs, videos, etc.)
        media_urls = [
            word for word in content.split()
            if word.startswith("http") and any(ext in word for ext in ['.gif', '.jpg', '.jpeg', '.png', '.mp4', '.webm'])
        ]
        for attachment in message.attachments:
            if attachment.content_type and any(mt in attachment.content_type for mt in ['gif', 'image', 'video']):
                media_urls.append(attachment.url)

        media_description = ""
        if media_urls:
            media_description += "\n\nMedia shared:\n" + "\n".join(media_urls)

            # Generate image captions using vision model
            vision_descriptions = []
            for url in media_urls:
                vision = describe_image(url)
                vision_descriptions.append(f"{url}: {vision}")
            if vision_descriptions:
                media_description += "\n\nImage captions:\n" + "\n".join(vision_descriptions)

        # Update memory with user and message details
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
        prompt = f"{display_name} says: {content}" + media_description

        print(f"Prompt sent to AI: {prompt}", flush=True)

        try:
            # Get the AI's response
            reply = get_ai_response(memory, prompt)
            print(f"AI reply: {reply}", flush=True)
        except Exception as e:
            reply = "Sorry, I had trouble generating a response."
            print("Error in get_ai_response:", e, flush=True)

        update_user_memory(user_id, {"role": "assistant", "content": reply})
        await message.channel.send(reply)

        # Save GIFs (if any)
        if gif_url := extract_gif_url(content):
            save_gif_for_user(user_id, gif_url)
        for attachment in message.attachments:
            if attachment.content_type and 'gif' in attachment.content_type:
                save_gif_for_user(user_id, attachment.url)

        # Generate TTS response
        audio_data = generate_tts(reply, model=TTS_MODEL)
        if audio_data:
            with open("tts_output.mp3", "wb") as f:
                f.write(audio_data)
            await message.channel.send(file=discord.File("tts_output.mp3"))

    except Exception as e:
        print("Error in on_message:", e, flush=True)

@bot.command()
async def gif(ctx, *, query):
    url = get_gif(query)
    await ctx.send(url)

@bot.command()
async def nick(ctx, *, new_name):
    await ctx.guild.me.edit(nick=new_name)
    await ctx.send(f"My new name is **{new_name}**!")

@bot.command()
async def test(ctx):
    await ctx.send("I'm alive and responding!")

# Web server setup for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# Start the Discord bot
bot.run(os.getenv("DISCORD_TOKEN"))
