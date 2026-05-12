import discord
from discord.ext import commands
from discord.ui import Button, View
import os, io
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Eye Bot Pro Online!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    Thread(target=run, daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def create_noir_design(avatar_bytes, banner_bytes):
    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    banner = Image.open(io.BytesIO(banner_bytes)).convert("RGBA")
    
    # خلفية مضببة
    canvas_w, canvas_h = 1000, 600
    background = banner.copy().resize((canvas_w, canvas_h))
    background = background.filter(ImageFilter.GaussianBlur(radius=25)) 
    
    # البنر - زوايا دائرية وبدون حواف بيضاء
    banner_w, banner_h = 800, 280
    banner_main = ImageOps.fit(banner, (banner_w, banner_h))
    banner_final = add_corners(banner_main, 30) # زوايا دائرية فخمة
    
    # الافتار - دائري صافي بدون حواف بيضاء
    av_size = 280
    avatar = ImageOps.fit(avatar, (av_size, av_size))
    mask = Image.new('L', (av_size, av_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, av_size - 1, av_size - 1), fill=255)
    
    avatar_round = Image.new('RGBA', (av_size, av_size), (0, 0, 0, 0))
    avatar_round.paste(avatar, (0, 0), mask=mask)

    # الدمج في أماكن نوار بالضبط
    background.paste(banner_final, (150, 80), banner_final)
    background.paste(avatar_round, (110, 230), avatar_round)
    
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
            await interaction.user.send(f"صورك الأصلية:\n**الافتار:** {self.av_url}\n**البنر:** {self.bn_url}")
            await interaction.response.send_message("أرسلتها لك خاص!", ephemeral=True)
        except:
            await interaction.response.send_message("افتح الخاص!", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot: return
    if len(message.attachments) == 2:
        av_att = message.attachments[0]
        bn_att = message.attachments[1]
        
        av_data = await av_att.read()
        bn_data = await bn_att.read()
        
        final_img = create_noir_design(av_data, bn_data)
        file = discord.File(final_img, filename="eye_design.png")
        view = DownloadView(av_att.url, bn_att.url)
        
        await message.channel.send(content=f"From: {message.author.mention}", file=file, view=view)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
