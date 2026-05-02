import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# AYARLAR

DESTEK_ROLU_ID       = 1499363289929351288
YETKILI_KULLANICI_ID = 1438202822897434738

# BOT KURULUMU

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=”.”, intents=intents)

# DESTEK BUTONU VIEW

class DestekView(View):
def **init**(self):
super().**init**(timeout=None)

```
@discord.ui.button(
    label="Destek Al",
    style=discord.ButtonStyle.primary,
    custom_id="destek_butonu"
)
async def destek_butonu(self, interaction: discord.Interaction, button: Button):
    guild = interaction.guild
    user  = interaction.user
    role  = guild.get_role(DESTEK_ROLU_ID)

    existing = discord.utils.get(guild.channels, name=f"destek-{user.name.lower()}")
    if existing:
        await interaction.response.send_message(
            f"Zaten acik bir destek kanalin var: {existing.mention}",
            ephemeral=True
        )
        return

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

    kanal = await guild.create_text_channel(
        name=f"destek-{user.name}",
        overwrites=overwrites,
        topic=f"{user.id} tarafindan acilan destek kanali"
    )

    embed = discord.Embed(
        title="Destek Talebi Olusturuldu",
        description=(
            f"Merhaba {user.mention}! Destek talebiniz alindi.\n\n"
            "Destek ekibimiz en kisa surede size yardimci olacak.\n"
            "Kanali kapatmak icin: `.delete`"
        ),
        color=0x5865F2
    )
    embed.set_footer(text="Nova Lig Destek Sistemi")

    await kanal.send(embed=embed)

    tag_msg = await kanal.send(
        f"{user.mention} {role.mention if role else ''}"
    )
    await asyncio.sleep(3)
    await tag_msg.delete()

    await interaction.response.send_message(
        f"Destek kanalin olusturuldu: {kanal.mention}",
        ephemeral=True
    )
```

# KOMUTLAR

@bot.command(name=“ticketkur”)
async def ticketkur(ctx):
if ctx.author.id != YETKILI_KULLANICI_ID and ctx.author.id != ctx.guild.owner_id:
await ctx.send(“Bu komutu kullanma yetkiniz yok.”, delete_after=5)
return

```
embed = discord.Embed(
    title="Nova Lig Destek",
    description=(
        "Herhangi bir konuda yardima ihtiyac duyuyorsaniz\n"
        "asagidaki butona tiklayarak destek talebi olusturabilirsiniz."
    ),
    color=0x5865F2
)
embed.set_footer(text="Nova Lig - Destek Sistemi")

view = DestekView()
await ctx.send(embed=embed, view=view)

try:
    await ctx.message.delete()
except discord.Forbidden:
    pass
```

@bot.command(name=“delete”)
async def delete(ctx):
role = ctx.guild.get_role(DESTEK_ROLU_ID)

```
if role not in ctx.author.roles:
    await ctx.send("Bu komutu kullanma yetkiniz yok.", delete_after=5)
    return

if not ctx.channel.name.startswith("destek-"):
    await ctx.send("Bu komut sadece destek kanallarinda kullanilabilir.", delete_after=5)
    return

embed = discord.Embed(
    title="Kanal Siliniyor",
    description="Bu destek kanali 5 saniye icinde silinecek...",
    color=0xFF4444
)
await ctx.send(embed=embed)
await asyncio.sleep(5)
await ctx.channel.delete(reason=f"{ctx.author} tarafindan silindi.")
```

@bot.command(name=“ticketkullanici-ekle”)
async def ticket_kullanici_ekle(ctx, member: discord.Member):
role = ctx.guild.get_role(DESTEK_ROLU_ID)

```
if role not in ctx.author.roles:
    await ctx.send("Bu komutu kullanma yetkiniz yok.", delete_after=5)
    return

if not ctx.channel.name.startswith("destek-"):
    await ctx.send("Bu komut sadece destek kanallarinda kullanilabilir.", delete_after=5)
    return

await ctx.channel.set_permissions(
    member,
    view_channel=True,
    send_messages=True,
    read_message_history=True
)

embed = discord.Embed(
    description=f"{member.mention} bu kanala eklendi.",
    color=0x57F287
)
await ctx.send(embed=embed)
```

# PERSISTENT VIEW KAYDI

@bot.event
async def on_ready():
bot.add_view(DestekView())
print(f”Bot acildi: {bot.user}”)

bot.run(os.getenv(“DISCORD_TOKEN”))
