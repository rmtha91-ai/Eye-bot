import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import io
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from flask import Flask
from threading import Thread

# تشغيل Flask للبقاء أونلاين على Render
app = Flask('')
@app.route('/')
def home(): return "Designer Bot with Buttons is Online!"

def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def create_exact_noir_style(avatar_bytes, banner_bytes):
    # فتح الصور
    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    banner = Image.open(io.BytesIO(banner_bytes)).convert("RGBA")
    
    # 1. إنشاء الخلفية الكبيرة (المضببة)
    canvas_w, canvas_h = 1000, 600
    background = banner.copy().resize((canvas_w, canvas_h))
    background = background.filter(ImageFilter.GaussianBlur(radius=25)) 
    
    # 2. معالجة البنر (المستطيل الفخم)
    banner_w, banner_h = 750, 250
    banner_main = ImageOps.fit(banner, (banner_w, banner_h))
    banner_final = ImageOps.expand(banner_main, border=6, fill='white')
    
    # 3. معالجة الافتار (الدائرة)
    av_size = 260
    avatar = ImageOps.fit(avatar, (av_size, av_size))
    mask = Image.new('L', (av_size, av_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, av_size, av_size), fill=255)
    
    avatar_round = Image.new('RGBA', (av_size, av_size), (0, 0, 0, 0))
    avatar_round.paste(avatar, (0, 0), mask=mask)
    
    border_size = 10
    avatar_with_border = Image.new('RGBA', (av_size + border_size*2, av_size + border_size*2), (0,0,0,0))
    draw_border = ImageDraw.Draw(avatar_with_border)
    draw_border.ellipse((0, 0, av_size + border_size*2 - 1, av_size + border_size*2 - 1), fill='white')
    avatar_with_border.paste(avatar_round, (border_size, border_size), avatar_round)

    # 4. دمج المكونات (أماكن Noir بالضبط)
    background.paste(banner_final, (180, 100), banner_final)
    background.paste(avatar_with_border, (120, 220), avatar_with_border)
    
    final_buffer = io.BytesIO()
    background.save(final_buffer, format='PNG')
    final_buffer.seek(0)
    return final_buffer

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    if len(message.attachments) >= 2:
        # قراءة البيانات
        av_data = await message.attachments[0].read()
        bn_data = await message.attachments[1].read()
        
        # إنشاء التصميم
        final_img = create_exact_noir_style(av_data, bn_data)
        file = discord.File(final_img, filename="noir_design.png")
        
        # إنشاء الـ Embed
        embed = discord.Embed(description=f"**From: {message.author.mention}**", color=0x2b2d31)
        embed.set_image(url="attachment://noir_design.png")
        
        # إرسال الصورة أولاً للحصول على رابطها (مطلوب للزر)
        msg = await message.channel.send(file=file, embed=embed)
        
        # إضافة زر التحميل
        download_url = msg.embeds[0].image.url
        view = View()
        button = Button(label="Download", url=download_url, style=discord.ButtonStyle.link, emoji="📥")
        view.add_item(button)
        
        # تحديث الرسالة بالزر
        await msg.edit(view=view)
        
        # حذف الرسالة الأصلية
        try: await message.delete()
        except: pass

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))

