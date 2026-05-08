import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# --- جزء السيرفر الوهمي عشان ريندر ما يطفي ---
app = Flask('')
@app.route('/')
def home(): return "I am alive!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
OWNER_ID = 517961002214752257 

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} Is Online!')

@bot.command()
async def bc(ctx, *, message):
    if ctx.author.id != OWNER_ID: return
    success = 0
    await ctx.send(f"⏳ جاري الإرسال لـ {len(ctx.guild.members)} عضو...")
    for member in ctx.guild.members:
        if member.bot: continue
        try:
            await member.send(f"📢 **رسالة من الإدارة:**\n\n{message}")
            success += 1
            await asyncio.sleep(1)
        except: pass
    await ctx.send(f"✅ تم الإرسال بنجاح لـ {success} عضو.")

# تشغيل السيرفر الوهمي والبوت
keep_alive()
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
