import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils.memory import get_user_memory, update_user_memory, update_user_profile
from utils.ai import get_ai_response
from utils.media import get_gif, save_gif_for_user, extract_gif_url
from utils.vision import describe_image
from utils.tts import generate_tts
from flask import Flask
import threading
import random

load_dotenv()
TTS_MODEL = os.getenv("TTS_MODEL", "bark")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

GABRIEL_PHRASES = [
    "TO STAND AGAINST ME IS TO BE DESTROYED!",
    "I SERVE THE WILL OF THE HEAVENS.",
    "I AM THE JUDGEMENT.",
    "TREMBLE BEFORE DIVINE WRATH!",
    "BLASPHEMER. REPENT.",
    "YOU DARE SPEAK MY NAME IN VAIN?",
    "THE MISSION. THE WORD. THE WILL.",
]

@bot.event
async def on_ready():
    print(f"{bot.user} is online.", flush=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    user = message.author
    user_id = str(user.id)
    content = message.content.strip().lower()

    is_mentioned = bot.user in message.mentions or "gabriel" in content or "holy one" in content
    is_reply = (
        message.reference and
        isinstance(message.reference.resolved, discord.Message) and
        message.reference.resolved.author.id == bot.user.id
    )
    random_chance = random.random() < 0.075  # 7.5% random interjection
    tts_requested = content.startswith("!speak") or "[tts]" in content

    triggered = any([is_mentioned, is_reply, random_chance, tts_requested])
    if not triggered:
        return

    try:
        if tts_requested and not (is_mentioned or is_reply or random_chance):
            prompt = message.content.replace("!speak", "").replace("[tts]", "").strip()
        else:
            prompt = f"{user.display_name} says: {message.content}"

        update_user_profile(user_id, {
            "username": user.name,
            "nickname": user.display_name,
            "bio": getattr(user, "bio", "Unavailable"),
            "status": str(user.status),
            "account_created": user.created_at.strftime("%Y-%m-%d"),
            "joined_server": message.guild.get_member(user.id).joined_at.strftime("%Y-%m-%d") if message.guild else "Unknown",
            "avatar_url": user.avatar.url if user.avatar else None
        })

        media_urls = [word for word in content.split() if word.startswith("http") and any(ext in word for ext in ['.gif', '.jpg', '.jpeg', '.png', '.mp4', '.webm'])]
        for attachment in message.attachments:
            if attachment.content_type and any(mt in attachment.content_type for mt in ['gif', 'image', 'video']):
                media_urls.append(attachment.url)

        media_description = ""
        if media_urls:
            media_description += "\n\nMedia shared:\n" + "\n".join(media_urls)
            vision_descriptions = [f"{url}: {describe_image(url)}" for url in media_urls]
            media_description += "\n\nImage captions:\n" + "\n".join(vision_descriptions)

        memory = get_user_memory(user_id)
        full_prompt = prompt + media_description

        reply = get_ai_response(memory, full_prompt)
        print(f"Gabriel says: {reply}", flush=True)

        update_user_memory(user_id, {"role": "user", "content": full_prompt})
        update_user_memory(user_id, {"role": "assistant", "content": reply})

        await message.channel.send(reply)

        if extract_gif_url(content):
            save_gif_for_user(user_id, extract_gif_url(content))
        for attachment in message.attachments:
            if attachment.content_type and 'gif' in attachment.content_type:
                save_gif_for_user(user_id, attachment.url)

        if tts_requested:
            audio_data = generate_tts(reply, model=TTS_MODEL)
            if audio_data:
                with open("tts_output.mp3", "wb") as f:
                    f.write(audio_data)
                await message.channel.send(file=discord.File("tts_output.mp3"))

    except Exception as e:
        print("Error in on_message:", e)

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
    await ctx.send(random.choice(GABRIEL_PHRASES))

# Web ping (Render compatibility)
app = Flask(__name__)

@app.route('/')
def home():
    return "Gabriel is watching..."

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

bot.run(os.getenv("DISCORD_TOKEN"))
