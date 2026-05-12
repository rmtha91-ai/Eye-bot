import discord
from discord.ext import commands
import os
import io
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from flask import Flask
from threading import Thread

# تشغيل Flask للبقاء أونلاين
app = Flask('')
@app.route('/')
def home(): return "Designer Bot is Online!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def create_pro_design(avatar_bytes, banner_bytes):
    # 1. فتح الصور
    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    banner_img = Image.open(io.BytesIO(banner_bytes)).convert("RGBA")
    
    # 2. إنشاء الخلفية المضببة (الخلفية الكبيرة)
    background = banner_img.copy()
    background = background.resize((1000, 500)) # حجم اللوحة كاملة
    background = background.filter(ImageFilter.GaussianBlur(radius=15)) # تضبيب الخلفية
    
    # 3. تجهيز البنر الصغير (اللي في النص)
    small_banner = ImageOps.fit(banner_img, (700, 300))
    # إضافة حواف مستديرة للبنر (اختياري للفخامة)
    
    # 4. تجهيز الافتار الدائري
    avatar_size = (250, 250)
    avatar_img = ImageOps.fit(avatar_img, avatar_size)
    mask = Image.new('L', avatar_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + avatar_size, fill=255)
    
    circular_avatar = Image.new('RGBA', avatar_size, (0, 0, 0, 0))
    circular_avatar.paste(avatar_img, (0, 0), mask=mask)
    
    # 5. تركيب المكونات فوق الخلفية المضببة
    background.paste(small_banner, (250, 100), small_banner) # البنر في النص
    background.paste(circular_avatar, (50, 125), circular_avatar) # الافتار عالجنب
    
    # حفظ النتيجة
    final_buffer = io.BytesIO()
    background.save(final_buffer, format='PNG')
    final_buffer.seek(0)
    return final_buffer

@bot.event
async def on_message(message):
    if message.author.bot: return

    if len(message.attachments) >= 2:
        # بنعتبر أول صورة هي الافتار والثانية هي البنر
        avatar_data = await message.attachments[0].read()
        banner_data = await message.attachments[1].read()
        
        # معالجة الصورة
        final_design = create_pro_design(avatar_data, banner_data)
        
        file = discord.File(final_design, filename="pro_design.png")
        embed = discord.Embed(
            description=f"**From: {message.author.mention}**",
            color=0x2b2d31
        )
        embed.set_image(url="attachment://pro_design.png")
        
        await message.channel.send(file=file, embed=embed)
        
        try: await message.delete()
        except: pass

    await bot.process_commands(message)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
