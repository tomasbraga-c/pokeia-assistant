import os
from fastapi import FastAPI
import requests
from dotenv import load_dotenv

load_dotenv("Anthropic.env")
load_dotenv("groq.env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()

# Tabela de fraquezas por tipo
FRAQUEZAS = {
    "normal":   ["fighting"],
    "fire":     ["water", "ground", "rock"],
    "water":    ["electric", "grass"],
    "electric": ["ground"],
    "grass":    ["fire", "ice", "poison", "flying", "bug"],
    "ice":      ["fire", "fighting", "rock", "steel"],
    "fighting": ["flying", "psychic", "fairy"],
    "poison":   ["ground", "psychic"],
    "ground":   ["water", "grass", "ice"],
    "flying":   ["electric", "ice", "rock"],
    "psychic":  ["bug", "ghost", "dark"],
    "bug":      ["fire", "flying", "rock"],
    "rock":     ["water", "grass", "fighting", "ground", "steel"],
    "ghost":    ["ghost", "dark"],
    "dragon":   ["ice", "dragon", "fairy"],
    "dark":     ["fighting", "bug", "fairy"],
    "steel":    ["fire", "fighting", "ground"],
    "fairy":    ["poison", "steel"],
}


VANTAGENS = {
    "normal":   [],
    "fire":     ["grass", "ice", "bug", "steel"],
    "water":    ["fire", "ground", "rock"],
    "electric": ["water", "flying"],
    "grass":    ["water", "ground", "rock"],
    "ice":      ["grass", "ground", "flying", "dragon"],
    "fighting": ["normal", "ice", "rock", "dark", "steel"],
    "poison":   ["grass", "fairy"],
    "ground":   ["fire", "electric", "poison", "rock", "steel"],
    "flying":   ["grass", "fighting", "bug"],
    "psychic":  ["fighting", "poison"],
    "bug":      ["grass", "psychic", "dark"],
    "rock":     ["fire", "ice", "flying", "bug"],
    "ghost":    ["psychic", "ghost"],
    "dragon":   ["dragon"],
    "dark":     ["psychic", "ghost"],
    "steel":    ["ice", "rock", "fairy"],
    "fairy":    ["fighting", "dragon", "dark"],
}


@app.get("/")
def inicio():
    return {"mensagem": "PokeIA Assistant funcionando!"}

@app.get("/pokemon/{nome}")
def busca_pokemon(nome: str):
    
    # Busca o pokemon na api do pokeapi
    resposta = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nome.lower()}")

    if resposta.status_code != 200:
        return {"erro": f"Pokemon, {nome} não encontrado"}
    
    dados = resposta.json()

   
    return {
        "nome": dados["name"],
        "id": dados["id"],
        "tipos": [t["type"]["name"] for t in dados["types"]],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in dados["stats"]},
        "altura": dados["height"],
        "peso": dados["weight"]
    }

@app.get("/jogo/{nome}")
def buscar_jogo(nome: str):
    # Buscar o jogo na PokéAPI
    resposta = requests.get(f"https://pokeapi.co/api/v2/version/{nome.lower()}")
    
    if resposta.status_code != 200:
        return {"erro": f"Jogo '{nome}' não encontrado"}
    
    dados = resposta.json()
    

    
    version_grupo = dados["version_group"]["url"]
    resposta_grupo = requests.get(version_grupo)
    dados_group = resposta_grupo.json()

    # Pega o nome do Pokédex regional
    pokedexes = [p["name"] for p in dados_group["pokedexes"]]
    
    return {
        "jogo": dados["name"],
        "pokedexes": pokedexes
    }


@app.get("/pokedex/{nome}")
def buscar_pokedex(nome: str):
    resposta = requests.get(f"https://pokeapi.co/api/v2/pokedex/{nome.lower()}")
    
    if resposta.status_code != 200:
        return {"erro": f"Pokédex '{nome}' não encontrada"}
    
    dados = resposta.json()
    
    pokemons = [p["pokemon_species"]["name"] for p in dados["pokemon_entries"]]
    
    return {
        "pokedex": dados["name"],
        "total": len(pokemons),
        "pokemons": pokemons
    }

@app.get("/jogo/{nome}/pokemons")
def buscar_pokemons_jg(nome:str):
    resposta = requests.get(f"https://pokeapi.co/api/v2/version/{nome.lower()}")


    if resposta.status_code != 200:
        return {"erro": f"Jogo '{nome}' não encontrado"}
    
    dados = resposta.json()

    
    dados_group = requests.get(dados["version_group"]["url"]).json()

    # vamos pegar TODAS as pokédexes do jogo
    
    pokemons = []
    pokedexes_usadas = []
    
    for pokedex in dados_group["pokedexes"]:
        nome_pokedex = pokedex["name"]
        dados_pokedex = requests.get(f"https://pokeapi.co/api/v2/pokedex/{nome_pokedex}").json()
        
        novos = [p["pokemon_species"]["name"] for p in dados_pokedex["pokemon_entries"]]
        
        # Evita duplicatas
        for p in novos:
            if p not in pokemons:
                pokemons.append(p)
        
        pokedexes_usadas.append(nome_pokedex)


    return {
        "jogo": nome,
        "pokedexes": pokedexes_usadas,
        "total": len(pokemons),
        "pokemons": pokemons
    }

@app.post("/analisar-time")

def analisar_time(time: list[str]):
    contagem_fraquezas = {}
    contagem_vantagens = {}
    tipos_no_time = []
    detalhes_por_pokemon = []


    for nome_pokemon in time:
        resposta = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nome_pokemon.lower()}")
        if resposta.status_code != 200:
            return {"erro": f"Pokemon '{nome_pokemon}' não encontrado"}
        
        dados = resposta.json()
        tipos = [t["type"]["name"] for t in dados["types"]]
        tipos_no_time.extend(tipos)


        fraquezas_pokemon = []
        vantagens_pokemon = []
 
        for tipo in tipos:
            for f in FRAQUEZAS.get(tipo, []):
                if f not in fraquezas_pokemon:
                    fraquezas_pokemon.append(f)
            for v in VANTAGENS.get(tipo, []):
                if v not in vantagens_pokemon:
                    vantagens_pokemon.append(v)

        detalhes_por_pokemon.append({
            "pokemon": nome_pokemon.lower(),
            "tipos": tipos,
            "fraquezas": fraquezas_pokemon,
            "vantagens": vantagens_pokemon,
        })


        for tipo in tipos:
            fraquezas = FRAQUEZAS.get(tipo, [])
            for f in fraquezas:
                contagem_fraquezas[f] = contagem_fraquezas.get(f, 0) + 1
            for v in VANTAGENS.get(tipo, []):
                contagem_vantagens[v] = contagem_vantagens.get(v, 0) + 1

    fraquezas_ordenadas = dict(sorted(contagem_fraquezas.items(), key=lambda x: x[1], reverse=True))
    vantagens_ordenadas = dict(sorted(contagem_vantagens.items(), key=lambda x: x[1], reverse=True))

    return {
        "time": time,
        "tipos_no_time": list(set(tipos_no_time)),
        "fraquezas_do_time": fraquezas_ordenadas,
        "maior_fraqueza": max(fraquezas_ordenadas, key=fraquezas_ordenadas.get) if fraquezas_ordenadas else None,
        "vantagens_do_time": vantagens_ordenadas,
        "maior_vantagem": max(vantagens_ordenadas, key=vantagens_ordenadas.get) if vantagens_ordenadas else None,
        "detalhes_por_pokemon": detalhes_por_pokemon,
    }