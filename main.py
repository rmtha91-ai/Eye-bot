import discord
from discord.ext import commands
import os
import asyncio

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # ضروري جداً عشان يشوف الأعضاء
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ضع هنا الـ ID الخاص بحسابك في ديسكورد
OWNER_ID = 517961002214752257  # استبدل هذا الرقم بـ ID حسابك

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} Is Online!')

@bot.command()
async def bc(ctx, *, message):
    # التحقق من المطور
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ هذا الأمر للمطور فقط!")
        return

    # التأكد أن الأمر أُرسل من سيرفر
    if ctx.guild is None:
        await ctx.send("❌ استخدم الأمر داخل السيرفر")
        return

    success = 0
    failed = 0
    members = ctx.guild.members

    await ctx.send(f"⏳ جاري الإرسال إلى {len(members)} عضو في الخاص...")

    for member in members:
        if member.bot: continue # يتخطى البوتات
        
        try:
            embed = discord.Embed(title=f"📢 رسالة من {ctx.guild.name}", description=message, color=0x00ff00)
            await member.send(embed=embed)
            success += 1
            await asyncio.sleep(1) # تأخير ثانية بين كل رسالة لتجنب الحظر
        except Exception:
            failed += 1

    await ctx.send(f"✅ تم الانتهاء!\n🚀 وصلت لـ: {success}\n⚠️ فشل الإرسال لـ: {failed} (غالباً مقفلين الخاص)")

# تشغيل البوت
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
