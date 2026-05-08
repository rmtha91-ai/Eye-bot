import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "I am alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True # ضروري عشان يشوف حالة الأعضاء

bot = commands.Bot(command_prefix="!", intents=intents)
OWNER_ID = 517961002214752257 

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} Is Online!')

@bot.command()
async def bc(ctx, *, message):
    if ctx.author.id != OWNER_ID: return
    
    # تصفية الأعضاء الأونلاين فقط (متصل، خامل، عدم الإزعاج)
    online_members = [m for m in ctx.guild.members if not m.bot and m.status != discord.Status.offline]
    
    success = 0
    await ctx.send(f"🚀 جاري الإرسال السريع لـ {len(online_members)} عضو متصل الآن...")
    
    for member in online_members:
        try:
            await member.send(f"📢 **رسالة من الإدارة:**\n\n{message}")
            success += 1
            await asyncio.sleep(0.1) # الانتظار اللي طلبته
        except:
            continue
            
    await ctx.send(f"✅ انتهى الإرسال! وصل لـ {success} عضو من المتصلين.")

keep_alive()
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
