import discord
from discord.ext import tasks, commands
import requests
import random
import os
from dotenv import load_dotenv
import datetime

# -------------------- CARREGA VARIÁVEIS --------------------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------- DATAS COMEMORATIVAS --------------------
FERIADOS = {
    "10-31": {"nome": "Halloween", "keywords": ["horror", "thriller"]},
    "12-25": {"nome": "Natal", "keywords": ["family", "christmas"]},
    "01-01": {"nome": "Ano Novo", "keywords": ["comedy", "celebration"]},
    # Você pode adicionar mais datas
}

# -------------------- FUNÇÕES AUXILIARES --------------------
def pegar_generos():
    url = f"{TMDB_BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=pt-BR"
    response = requests.get(url).json()
    generos = response.get("genres", [])
    return {g["id"]: g["name"] for g in generos}

GENERO_DICT = pegar_generos()

def formatar_filme(filme):
    if not filme:
        return None, None, None, None, None
    titulo = filme.get("title")
    sinopse = filme.get("overview") or "Sem sinopse disponível."
    poster = f"{POSTER_BASE_URL}{filme['poster_path']}" if filme.get("poster_path") else None
    ano = filme.get("release_date", "")[:4]
    generos_ids = filme.get("genre_ids", [])
    generos_nomes = [GENERO_DICT.get(gid) for gid in generos_ids if GENERO_DICT.get(gid)]
    return titulo, sinopse, poster, ano, generos_nomes

# -------------------- FUNÇÃO DE BUSCA --------------------
def buscar_filmes_populares_e_conhecidos(keywords=None):
    """Busca filmes populares, conhecidos e com boas notas."""
    params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR",
        "sort_by": "vote_average.desc",
        "vote_average.gte": 7,
        "vote_count.gte": 1000,
        "with_original_language": "en",
        "page": random.randint(1,5)
    }
    
    if keywords:
        # Buscar filmes por palavra-chave
        # Para simplificar, usamos `with_keywords` como lista de nomes (TMDb aceita IDs, mas simplificamos)
        params["with_keywords"] = ",".join(keywords)
    
    url = f"{TMDB_BASE_URL}/discover/movie"
    response = requests.get(url, params=params).json()
    filmes = response.get("results", [])
    return random.choice(filmes) if filmes else None

def buscar_filme_do_dia():
    hoje = datetime.datetime.now().strftime("%m-%d")
    feriado = FERIADOS.get(hoje)
    
    if feriado:
        filme = buscar_filmes_populares_e_conhecidos(keywords=feriado["keywords"])
    else:
        filme = buscar_filmes_populares_e_conhecidos()
    
    return formatar_filme(filme)

# -------------------- EVENTOS DO BOT --------------------
@bot.event
async def on_ready():
    print(f"✅ {bot.user} está online!")
    enviar_filme.start()

# -------------------- TAREFA DIÁRIA --------------------
@tasks.loop(hours=24)
async def enviar_filme():
    canal = bot.get_channel(CHANNEL_ID)
    titulo, sinopse, poster, ano, generos = buscar_filme_do_dia()
    if not titulo:
        await canal.send("❌ Nenhum filme encontrado.")
        return
    
    generos_texto = ", ".join(generos) if generos else "Sem gênero definido"
    
    # Verificar se hoje é feriado
    hoje = datetime.datetime.now().strftime("%m-%d")
    feriado = FERIADOS.get(hoje)
    prefixo = f"🎉 {feriado['nome']}! Filme recomendado:" if feriado else "🎬 Filme do dia:"
    
    embed = discord.Embed(
        title=f"{prefixo} {titulo} ({ano})",
        description=f"{sinopse}\n\n**Gêneros:** {generos_texto}",
        color=0x2ecc71
    )
    if poster:
        embed.set_image(url=poster)
    await canal.send(embed=embed)

# -------------------- COMANDO MANUAL --------------------
@bot.command()
async def filme(ctx):
    titulo, sinopse, poster, ano, generos = buscar_filme_do_dia()
    if not titulo:
        await ctx.send("❌ Nenhum filme encontrado.")
        return
    
    generos_texto = ", ".join(generos) if generos else "Sem gênero definido"
    
    hoje = datetime.datetime.now().strftime("%m-%d")
    feriado = FERIADOS.get(hoje)
    prefixo = f"🎉 {feriado['nome']}! Filme recomendado:" if feriado else "🎬 Filme sugerido:"
    
    embed = discord.Embed(
        title=f"{prefixo} {titulo} ({ano})",
        description=f"{sinopse}\n\n**Gêneros:** {generos_texto}",
        color=0x3498db
    )
    if poster:
        embed.set_image(url=poster)
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)

