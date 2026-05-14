import os
from fastapi import FastAPI
import requests
import json
from groq import Groq
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

cliente_ia = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = FastAPI()


class RequestSugestao(BaseModel):
    jogo: str
    estilo: str
    favoritos: list[str] = []       
    incluir_localizacao: bool = True
    incluir_lendarios: bool = False


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


def logica_analisar_time(time: list[str]):
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
        "fraquezas_do_time": fraquezas_ordenadas,
        "maior_fraqueza": max(fraquezas_ordenadas, key=fraquezas_ordenadas.get) if fraquezas_ordenadas else None,
        "vantagens_do_time": vantagens_ordenadas,
        "maior_vantagem": max(vantagens_ordenadas, key=vantagens_ordenadas.get) if vantagens_ordenadas else None,
        "detalhes_por_pokemon": detalhes_por_pokemon,
    }



@app.post("/analisar-time")
def analisar_time(time: list[str]):
    return logica_analisar_time(time)



# Montando o prompt para a IA

def montar_system_prompt():
    # O que a IA é, quais são as regras, qual o formato de resposta
  return f"""
        O que você é:
        Você é um treinador especialista em Pokémon.
        
        Regras:
        - Você deve montar um time de exatamente 6 Pokémons para o usuário, baseado no jogo que ele quer jogar, no estilo de time que ele deseja e nos pokémons favoritos que ele gostaria de incluir.
        - O time deve ser balanceado, buscando cobrir as fraquezas dos ginasios e das fases de cada jogo.
        - Para cada Pokémon escolhido, você deve explicar por que ele se encaixa no estilo pedido, qual o papel dele no time (atacante, tanque, suporte...), recomendar 4 movimentos, um item recomendado e onde encontrar ele no jogo (pode buscar tanto na pokeapi quanto em outras fontes confiáveis, como Bulbapedia, Serebii, Smogon...).
        - Responda em português e seja direto e objetivo.
        - O jogador só pode ter UM pokémon inicial no time. Nunca inclua dois ou mais dos três iniciais do jogo.
        - EXCEÇÃO: Nos jogos "let's-go-pikachu" e "let's-go-eevee" os três iniciais 
        (Bulbasaur, Charmander e Squirtle) podem ser obtidos como presente de NPC 
        durante o jogo, portanto podem aparecer juntos no time. Nestes jogos o 
        inicial obrigatório já está definido pelo título: Pikachu em "let's-go-pikachu" 
        e Eevee(Que não evolui) em "let's-go-eevee".
        - O campo "estilo" é uma restrição OBRIGATÓRIA e deve ser seguida acima de qualquer outra consideração, inclusive balanceamento. Se o usuário pedir "apenas formas base", NENHUM Pokémon evoluído pode aparecer no time, sem exceções. Se pedir "apenas tipo fogo", todos os 6 devem ser do tipo fogo. O estilo do usuário é lei — não sugira algo "melhor" se não foi pedido.
        - O formate a resposta em JSON seguindo o formato do exemplo abaixo, sem adicionar texto extra fora do JSON:
        Formato de resposta:
        '{{
            "time": [
                {{
                "pokemon": "nome",
                "papel": "Atacante físico",
                "destaques": "Extremamente rápido e poderoso no ataque especial",
                "movimentos": ["mv1", "mv2", "mv3", "mv4"],
                "item": "nome do item",
                "localizacao": "onde encontrar no jogo",
                "justificativa": "por que este pokemon"
                }}
            ],
            "estrategia_geral": "descrição da estratégia"
            }}'
        """


def montar_user_prompt(jogo: str, estilo: str, favoritos: list[str], pokemons_disponiveis: list[str]):
    lista_completa = ', '.join(pokemons_disponiveis)
    
    favoritos_str = ', '.join(favoritos) if favoritos else "nenhum"
    
    return f"""
    Jogo: {jogo}
    Estilo desejado: {estilo}
    Pokémons favoritos para incluir obrigatoriamente: {favoritos_str}
    Complete os {6 - len(favoritos)} restantes com as melhores escolhas para o estilo pedido.
    
    Pokémons disponíveis neste jogo (escolha APENAS desta lista):
    {lista_completa}
    
    Monte o time seguindo as regras e o formato definidos.
    """

# Rota para sugerir o time de acordo com os prompts e a resposta da IA

@app.post("/sugerir-time")
def sugerir_time(request: RequestSugestao):
    try:
        jogo_existente = buscar_jogo(request.jogo)
        if "erro" in jogo_existente:
            raise HTTPException(
                status_code=404,
                detail="Jogo não encontrado. Tente usar apenas o final do nome, ex: 'red', 'x', 'sword', 'scarlet'..."
            )
            
        pokemons_disponiveis = buscar_pokemons_jg(request.jogo)["pokemons"]

        resposta_ia = cliente_ia.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": montar_system_prompt()},
                {"role": "user", "content": montar_user_prompt(request.jogo, request.estilo, request.favoritos, pokemons_disponiveis)}
            ],
            max_tokens=2300,
            temperature=0.7,
            response_format={"type": "json_object"}
            
        )
        texto_resposta = resposta_ia.choices[0].message.content

        dados_ia = json.loads(texto_resposta)
        nomes_time = [p["pokemon"] for p in dados_ia["time"]]
        analise_time_gerado = logica_analisar_time(nomes_time)
        for i, pokemon in enumerate(dados_ia["time"]):
           pokemon["tipos"] = analise_time_gerado["detalhes_por_pokemon"][i]["tipos"]

        return {
        "time_sugerido": dados_ia,
        "analise": {
            "maior_fraqueza": analise_time_gerado["maior_fraqueza"],
            "maior_vantagem": analise_time_gerado["maior_vantagem"],
            "fraquezas_do_time": analise_time_gerado["fraquezas_do_time"],
            "vantagens_do_time": analise_time_gerado["vantagens_do_time"],
        }
    }
    except HTTPException:
        raise  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

