import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# إعداد سيرفر Flask للبقاء أونلاين
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ المنسق الآلي جاهز باسم: {bot.user.name}')

@bot.event
async def on_message(message):
    # تجاهل رسائل البوتات
    if message.author.bot:
        return

    # التأكد أن الرسالة تحتوي على صورة (Attachment)
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']):
                
                # إنشاء التنسيق (Embed) مثل صورة 1000028358.jpg
                embed = discord.Embed(
                    description=f"**From: {message.author.mention}**",
                    color=0x2b2d31 # لون رمادي غامق فخم
                )
                
                # وضع افتار العضو كأنه Header
                embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                
                # وضع الصورة اللي أرسلها العضو كـ بنر كبير
                embed.set_image(url=attachment.url)
                
                # وضع افتار العضو مرة ثانية كصورة مصغرة (Thumbnail) على الجنب
                embed.set_thumbnail(url=message.author.display_avatar.url)

                # حذف الرسالة الأصلية عشان ما يتكرر الشكل
                try:
                    await message.delete()
                except:
                    pass

                # إرسال التنسيق الجديد مع أزرار (اختياري: تحميل)
                await message.channel.send(embed=embed)
                break # ينسق أول صورة فقط لو أرسل مجموعة

    await bot.process_commands(message)

# تشغيل البوت
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
