import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────

# AYARLAR

# ─────────────────────────────────────────────

DESTEK_ROLU_ID      = 1499363289929351288   # Destek ekibi rolü
YETKILI_KULLANICI_ID = 1438202822897434738  # .ticketkur yapabilecek kullanıcı

# ─────────────────────────────────────────────

# BOT KURULUMU

# ─────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=”.”, intents=intents)

# ─────────────────────────────────────────────

# DESTEK BUTONU VIEW

# ─────────────────────────────────────────────

class DestekView(View):
def **init**(self):
super().**init**(timeout=None)  # Kalıcı view

```
@discord.ui.button(
    label="📩 Destek Al",
    style=discord.ButtonStyle.primary,
    custom_id="destek_butonu"
)
async def destek_butonu(self, interaction: discord.Interaction, button: Button):
    guild  = interaction.guild
    user   = interaction.user
    role   = guild.get_role(DESTEK_ROLU_ID)

    # Zaten açık bir ticket var mı kontrol et
    existing = discord.utils.get(guild.channels, name=f"destek-{user.name.lower()}")
    if existing:
        await interaction.response.send_message(
            f"❌ Zaten açık bir destek kanalın var: {existing.mention}",
            ephemeral=True
        )
        return

    # Kanal izinleri
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        ),
    }
    if role:
        overwrites[role] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )

    # Kanalı oluştur
    kanal = await guild.create_text_channel(
        name=f"destek-{user.name}",
        overwrites=overwrites,
        topic=f"{user.id} tarafından açılan destek kanalı"
    )

    # Ticket mesajı
    embed = discord.Embed(
        title="🎫 Destek Talebi Oluşturuldu",
        description=(
            f"Merhaba {user.mention}! Destek talebiniz alındı.\n\n"
            "Destek ekibimiz en kısa sürede size yardımcı olacak.\n"
            f"Kanalı kapatmak için: `.delete`"
        ),
        color=0x5865F2
    )
    embed.set_footer(text="Nova Lig Destek Sistemi")

    await kanal.send(
        content=f"{user.mention} {role.mention if role else ''}",
        embed=embed
    )

    # Tag mesajı — hemen arkasından sil ki kanalı kirletmesin
    tag_msg = await kanal.send(f"🔔 {user.mention} {role.mention if role else ''}")
    await asyncio.sleep(3)
    await tag_msg.delete()

    await interaction.response.send_message(
        f"✅ Destek kanalın oluşturuldu: {kanal.mention}",
        ephemeral=True
    )
```

# ─────────────────────────────────────────────

# KOMUTLAR

# ─────────────────────────────────────────────

@bot.command(name=“ticketkur”)
async def ticketkur(ctx):
“”“Destek panelini komutu yazılan kanala kurar.”””
# Yetki kontrolü: sunucu sahibi VEYA belirtilen kullanıcı
if ctx.author.id != YETKILI_KULLANICI_ID and ctx.author.id != ctx.guild.owner_id:
await ctx.send(“❌ Bu komutu kullanma yetkiniz yok.”, delete_after=5)
return

```
embed = discord.Embed(
    title="🛡️ Nova Lig Destek",
    description=(
        "Herhangi bir konuda yardıma ihtiyaç duyuyorsanız\n"
        "aşağıdaki butona tıklayarak destek talebi oluşturabilirsiniz."
    ),
    color=0x5865F2
)
embed.set_footer(text="Nova Lig • Destek Sistemi")

view = DestekView()
await ctx.send(embed=embed, view=view)

try:
    await ctx.message.delete()
except discord.Forbidden:
    pass
```

@bot.command(name=“delete”)
async def delete(ctx):
“”“Bulunulan ticket kanalını siler. Sadece destek rolü kullanabilir.”””
role = ctx.guild.get_role(DESTEK_ROLU_ID)

```
if role not in ctx.author.roles:
    await ctx.send("❌ Bu komutu kullanma yetkiniz yok.", delete_after=5)
    return

# Kanal bir ticket kanalı mı?
if not ctx.channel.name.startswith("destek-"):
    await ctx.send("❌ Bu komut sadece destek kanallarında kullanılabilir.", delete_after=5)
    return

embed = discord.Embed(
    title="🗑️ Kanal Siliniyor",
    description="Bu destek kanalı 5 saniye içinde silinecek...",
    color=0xFF4444
)
await ctx.send(embed=embed)
await asyncio.sleep(5)
await ctx.channel.delete(reason=f"{ctx.author} tarafından silindi.")
```

@bot.command(name=“ticketkullanıcı-ekle”)
async def ticket_kullanici_ekle(ctx, member: discord.Member):
“”“Bir kullanıcıyı ticket kanalına ekler. Sadece destek rolü yapabilir.”””
role = ctx.guild.get_role(DESTEK_ROLU_ID)

```
if role not in ctx.author.roles:
    await ctx.send("❌ Bu komutu kullanma yetkiniz yok.", delete_after=5)
    return

if not ctx.channel.name.startswith("destek-"):
    await ctx.send("❌ Bu komut sadece destek kanallarında kullanılabilir.", delete_after=5)
    return

await ctx.channel.set_permissions(
    member,
    view_channel=True,
    send_messages=True,
    read_message_history=True
)

embed = discord.Embed(
    description=f"✅ {member.mention} bu kanala eklendi.",
    color=0x57F287
)
await ctx.send(embed=embed)
```

# ─────────────────────────────────────────────

# PERSISTENT VIEW KAYDI (bot yeniden başlayınca)

# ─────────────────────────────────────────────

@bot.event
async def on_ready():
bot.add_view(DestekView())  # Kalıcı view’i kaydet
print(f”✅ {bot.user} olarak giriş yapıldı.”)
print(f”   Prefix  : .”)
print(f”   Destek Rol ID: {DESTEK_ROLU_ID}”)

# ─────────────────────────────────────────────

# BOTU ÇALIŞTIR

# ─────────────────────────────────────────────

bot.run(os.getenv(“TOKEN”))
