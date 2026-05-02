import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

DESTEK_ROL_ID = 1499363289929351288
YETKILI_ID = 1438202822897434738


# ---------------- BUTTON VIEW ---------------- #

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Destek Aç", style=discord.ButtonStyle.green)
    async def ticket_ac(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        user = interaction.user

        kategori = interaction.channel.category

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.get_role(DESTEK_ROL_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        kanal_adi = f"destekisteyen-{user.name}".lower().replace(" ", "-")

        kanal = await guild.create_text_channel(
            name=kanal_adi,
            category=kategori,
            overwrites=overwrites
        )

        await kanal.send(f"{user.mention} destek talebi oluşturdu.\n<@&{DESTEK_ROL_ID}>")

        await interaction.response.send_message(
            f"Destek kanalın oluşturuldu: {kanal.mention}",
            ephemeral=True
        )


# ---------------- KOMUTLAR ---------------- #

@bot.command()
async def ticketkur(ctx):
    if ctx.author.id != YETKILI_ID and ctx.author != ctx.guild.owner:
        return await ctx.send("Bunu kullanamazsın.")

    embed = discord.Embed(
        title="Nova Lig Destek",
        description="Destek almak için aşağıdaki butona bas.",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed, view=TicketView())


@bot.command()
async def delete(ctx):
    rol = ctx.guild.get_role(DESTEK_ROL_ID)

    if rol not in ctx.author.roles:
        return await ctx.send("Yetkin yok.")

    await ctx.channel.delete()


@bot.command(name="ticketkullanıcı-ekle")
async def ticket_kullanici_ekle(ctx, member: discord.Member):
    rol = ctx.guild.get_role(DESTEK_ROL_ID)

    if rol not in ctx.author.roles:
        return await ctx.send("Yetkin yok.")

    await ctx.channel.set_permissions(member, view_channel=True, send_messages=True)

    await ctx.send(f"{member.mention} artık bu ticketı görebilir.")


# ---------------- READY ---------------- #

@bot.event
async def on_ready():
    print(f"{bot.user} aktif!")


# ---------------- RUN ---------------- #

bot.run(os.getenv("TOKEN"))