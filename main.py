import os
import discord
from discord.ext import commands, tasks

# Cria o bot com o prefixo !
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")
    enviar_mensagem.start()  # inicia a tarefa automática

# Tarefa automática que envia mensagem a cada 1 hora
@tasks.loop(hours=1)
async def enviar_mensagem():
    canal = bot.get_channel(123456789012345678)  # coloque o ID do canal aqui
    if canal:
        await canal.send("Oi! Estou online e funcionando automaticamente 😄")

# 🚀 Inicia o bot com o token vindo da variável de ambiente
bot.run(os.getenv("TOKEN"))
