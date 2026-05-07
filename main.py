import os
import io
import asyncio
import aiohttp
import discord
from discord.ext import commands
from PIL import Image, ImageDraw
from flask import Flask
from threading import Thread

# --- إعداد صفحة الويب لمنع التوقف ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is Online!"

@app.route('/healthz')
def health():
    return "ok", 200

def run():
    app.run(host='0.0.0.0', port=8080)

# --- إعدادات دمج الصور ---
CANVAS_W, BANNER_W, BANNER_H, AVATAR_SIZE = 620, 580, 220, 120
BG_COLOR = (8, 8, 10, 255)

def build_merged_image(avatar_bytes, banner_bytes):
    av_src = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    ba_src = Image.open(io.BytesIO(banner_bytes)).convert("RGBA")
    canvas = Image.new("RGBA", (CANVAS_W, 368), BG_COLOR)
    ba_res = ba_src.resize((BANNER_W, BANNER_H), Image.LANCZOS)
    mask = Image.new("L", ba_res.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, BANNER_W-1, BANNER_H-1], 22, 255)
    ba_res.putalpha(mask)
    canvas.paste(ba_res, (20, 16), ba_res)
    av_res = av_src.resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)
    mask_av = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
    ImageDraw.Draw(mask_av).ellipse([0, 0, AVATAR_SIZE-1, AVATAR_SIZE-1], 255)
    canvas.paste(av_res, (25, 176), mask_av)
    out = io.BytesIO()
    canvas.convert("RGB").save(out, format="PNG")
    out.seek(0)
    return out.read()

# --- كود البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot: return
    images = [a for a in message.attachments if "image" in (a.content_type or "")]
    if len(images) == 2:
        async with message.channel.typing():
            async with aiohttp.ClientSession() as session:
                av_b = await (await session.get(images[0].url)).read()
                ba_b = await (await session.get(images[1].url)).read()
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, build_merged_image, av_b, ba_b)
            await message.channel.send(file=discord.File(io.BytesIO(res), "noir.png"))

# --- التشغيل النهائي ---
if __name__ == "__main__":
    Thread(target=run).start()
    token = os.getenv("DISCORD_TOKEN")
    bot.run(token)
