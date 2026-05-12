import discord
from discord.ext import commands
from discord.ui import Button, View
import os, io
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from flask import Flask
from threading import Thread

# تشغيل السيرفر للبقاء أونلاين
app = Flask('')
@app.route('/')
def home(): return "Eye Bot is Live!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def create_noir_design(avatar_bytes, banner_bytes):
    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    banner = Image.open(io.BytesIO(banner_bytes)).convert("RGBA")
    
    canvas_w, canvas_h = 1000, 600
    background = banner.copy().resize((canvas_w, canvas_h))
    background = background.filter(ImageFilter.GaussianBlur(radius=25)) 
    
    banner_w, banner_h = 800, 280
    banner_main = ImageOps.fit(banner, (banner_w, banner_h))
    banner_final = ImageOps.expand(banner_main, border=6, fill='white')
    
    av_size = 280
    avatar = ImageOps.fit(avatar, (av_size, av_size))
    mask = Image.new('L', (av_size, av_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, av_size, av_size), fill=255)
    
    avatar_round = Image.new('RGBA', (av_size, av_size), (0, 0, 0, 0))
    avatar_round.paste(avatar, (0, 0), mask=mask)
    
    avatar_with_border = Image.new('RGBA', (av_size + 20, av_size + 20), (0,0,0,0))
    draw_border = ImageDraw.Draw(avatar_with_border)
    draw_border.ellipse((0, 0, av_size + 19, av_size + 19), fill='white')
    avatar_with_border.paste(avatar_round, (10, 10), avatar_round)

    background.paste(banner_final, (150, 80), banner_final)
    background.paste(avatar_with_border, (100, 230), avatar_with_border)
    
    buf = io.BytesIO()
    background.save(buf, format='PNG')
    buf.seek(0)
    return buf

class DownloadView(View):
    def __init__(self, av_url, bn_url):
        super().__init__(timeout=None)
        self.av_url = av_url
        self.bn_url = bn_url

    @discord.ui.button(label="Eye افتار", style=discord.ButtonStyle.green, emoji="📥")
    async def download_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.user.send(f"تفضل يا وحش، هذي صورك الأصلية:\n**الافتار:** {self.av_url}\n**البنر:** {self.bn_url}")
            await interaction.response.send_message("أرسلت لك الصور في الخاص!", ephemeral=True)
        except:
            await interaction.response.send_message("تأكد إنك فاتح الخاص لاستلام الصور!", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot: return
    if len(message.attachments) >= 2:
        av_att = message.attachments[0]
        bn_att = message.attachments[1]
        
        av_data = await av_att.read()
        bn_data = await bn_att.read()
        
        final_img = create_noir_design(av_data, bn_data)
        file = discord.File(final_img, filename="eye_design.png")
        
        view = DownloadView(av_att.url, bn_att.url)
        # تم إزالة سطر الحذف (message.delete)
        await message.channel.send(content=f"From: {message.author.mention}", file=file, view=view)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))

