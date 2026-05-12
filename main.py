import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# 1. إعداد سيرفر Flask
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# 2. إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ المنسق الآلي جاهز: {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']):
                
                embed = discord.Embed(
                    description=f"**From: {message.author.mention}**",
                    color=0x2b2d31
                )
                
                embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                embed.set_image(url=attachment.url)
                embed.set_thumbnail(url=message.author.display_avatar.url)

                # تم إزالة سطر الحذف (await message.delete) بناءً على طلبك
                
                await message.channel.send(embed=embed)
                break 

    await bot.process_commands(message)

# 3. التشغيل
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)
