import os
import requests
import json
from groq import Groq
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from difflib import get_close_matches

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

INICIAIS_POR_JOGO = {
    "red": ["bulbasaur", "charmander", "squirtle"],
    "blue": ["bulbasaur", "charmander", "squirtle"],
    "yellow": ["pikachu"],
    "gold": ["chikorita", "cyndaquil", "totodile"],
    "silver": ["chikorita", "cyndaquil", "totodile"],
    "crystal": ["chikorita", "cyndaquil", "totodile"],
    "ruby": ["treecko", "torchic", "mudkip"],
    "sapphire": ["treecko", "torchic", "mudkip"],
    "emerald": ["treecko", "torchic", "mudkip"],
    "firered": ["bulbasaur", "charmander", "squirtle"],
    "leafgreen": ["bulbasaur", "charmander", "squirtle"],
    "diamond": ["turtwig", "chimchar", "piplup"],
    "pearl": ["turtwig", "chimchar", "piplup"],
    "platinum": ["turtwig", "chimchar", "piplup"],
    "heartgold": ["chikorita", "cyndaquil", "totodile"],
    "soulsilver": ["chikorita", "cyndaquil", "totodile"],
    "black": ["snivy", "tepig", "oshawott"],
    "white": ["snivy", "tepig", "oshawott"],
    "black-2": ["snivy", "tepig", "oshawott"],
    "white-2": ["snivy", "tepig", "oshawott"],
    "x": ["chespin", "fennekin", "froakie"],
    "y": ["chespin", "fennekin", "froakie"],
    "omega-ruby": ["treecko", "torchic", "mudkip"],
    "alpha-sapphire": ["treecko", "torchic", "mudkip"],
    "sun": ["rowlet", "litten", "popplio"],
    "moon": ["rowlet", "litten", "popplio"],
    "ultra-sun": ["rowlet", "litten", "popplio"],
    "ultra-moon": ["rowlet", "litten", "popplio"],
    "lets-go-pikachu": ["pikachu"],
    "lets-go-eevee": ["eevee"],
    "sword": ["grookey", "scorbunny", "sobble"],
    "shield": ["grookey", "scorbunny", "sobble"],
    "brilliant-diamond": ["turtwig", "chimchar", "piplup"],
    "shining-pearl": ["turtwig", "chimchar", "piplup"],
    "legends-arceus": ["rowlet", "cyndaquil", "oshawott"],
    "scarlet": ["sprigatito", "fuecoco", "quaxly"],
    "violet": ["sprigatito", "fuecoco", "quaxly"],
    "legends-za": ["chikorita","tepig","totodile"],
}

# Forma final de cada inicial base (para instruir a IA a sugerir o estágio certo)
FORMA_FINAL_INICIAL = {
    "bulbasaur": "venusaur",    "charmander": "charizard",  "squirtle": "blastoise",
    "pikachu": "pikachu",       "eevee": "eevee",
    "chikorita": "meganium",    "cyndaquil": "typhlosion",  "totodile": "feraligatr",
    "treecko": "sceptile",      "torchic": "blaziken",      "mudkip": "swampert",
    "turtwig": "torterra",      "chimchar": "infernape",    "piplup": "empoleon",
    "snivy": "serperior",       "tepig": "emboar",          "oshawott": "samurott",
    "chespin": "chesnaught",    "fennekin": "delphox",      "froakie": "greninja",
    "rowlet": "decidueye",      "litten": "incineroar",     "popplio": "primarina",
    "grookey": "rillaboom",     "scorbunny": "cinderace",   "sobble": "inteleon",
    "sprigatito": "meowscarada","fuecoco": "skeledirge",    "quaxly": "quaquaval",
}

# Legends Arceus usa formas Hisuianas nas evoluções finais
FORMA_FINAL_INICIAL_OVERRIDE = {
    "legends-arceus": {
        "rowlet": "decidueye-hisui",
        "cyndaquil": "typhlosion-hisui",
        "oshawott": "samurott-hisui",
    }
}

# Mapeia qualquer estágio evolutivo de um inicial de volta ao seu base (para validação)
FAMILIA_INICIAL = {
    "bulbasaur": "bulbasaur",   "ivysaur": "bulbasaur",     "venusaur": "bulbasaur",
    "charmander": "charmander", "charmeleon": "charmander", "charizard": "charmander",
    "squirtle": "squirtle",     "wartortle": "squirtle",    "blastoise": "squirtle",
    "pikachu": "pikachu",       "raichu": "pikachu",
    "eevee": "eevee",
    "chikorita": "chikorita",   "bayleef": "chikorita",     "meganium": "chikorita",
    "cyndaquil": "cyndaquil",   "quilava": "cyndaquil",     "typhlosion": "cyndaquil",
    "typhlosion-hisui": "cyndaquil",
    "totodile": "totodile",     "croconaw": "totodile",     "feraligatr": "totodile",
    "treecko": "treecko",       "grovyle": "treecko",       "sceptile": "treecko",
    "torchic": "torchic",       "combusken": "torchic",     "blaziken": "torchic",
    "mudkip": "mudkip",         "marshtomp": "mudkip",      "swampert": "mudkip",
    "turtwig": "turtwig",       "grotle": "turtwig",        "torterra": "turtwig",
    "chimchar": "chimchar",     "monferno": "chimchar",     "infernape": "chimchar",
    "piplup": "piplup",         "prinplup": "piplup",       "empoleon": "piplup",
    "snivy": "snivy",           "servine": "snivy",         "serperior": "snivy",
    "tepig": "tepig",           "pignite": "tepig",         "emboar": "tepig",
    "oshawott": "oshawott",     "dewott": "oshawott",       "samurott": "oshawott",
    "samurott-hisui": "oshawott",
    "chespin": "chespin",       "quilladin": "chespin",     "chesnaught": "chespin",
    "fennekin": "fennekin",     "braixen": "fennekin",      "delphox": "fennekin",
    "froakie": "froakie",       "frogadier": "froakie",     "greninja": "froakie",
    "rowlet": "rowlet",         "dartrix": "rowlet",        "decidueye": "rowlet",
    "decidueye-hisui": "rowlet",
    "litten": "litten",         "torracat": "litten",       "incineroar": "litten",
    "popplio": "popplio",       "brionne": "popplio",       "primarina": "popplio",
    "grookey": "grookey",       "thwackey": "grookey",      "rillaboom": "grookey",
    "scorbunny": "scorbunny",   "raboot": "scorbunny",      "cinderace": "scorbunny",
    "sobble": "sobble",         "drizzile": "sobble",       "inteleon": "sobble",
    "sprigatito": "sprigatito", "floragato": "sprigatito",  "meowscarada": "sprigatito",
    "fuecoco": "fuecoco",       "crocalor": "fuecoco",      "skeledirge": "fuecoco",
    "quaxly": "quaxly",         "quaxwell": "quaxly",       "quaquaval": "quaxly",
}

############################################################

@app.get("/")
def inicio():
    return {"mensagem": "PokeIA Assistant funcionando!"}

############################################################

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

############################################################

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

############################################################

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

############################################################

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

############################################################

def logica_analisar_time(time: list[str]):
    contagem_fraquezas = {}
    contagem_vantagens = {}
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

############################################################

@app.post("/analisar-time")
def analisar_time(time: list[str]):
    return logica_analisar_time(time)

############################################################

def montar_system_prompt():
    # O que a IA é, quais são as regras, qual o formato de resposta
    return f"""
        O que você é:
        Você é um treinador especialista em Pokémon.
        
        Regras:
        - Você deve montar um time de exatamente 6 Pokémons para o usuário, baseado no jogo que ele quer jogar, no estilo de time que ele deseja e nos pokémons favoritos que ele gostaria de incluir.
        - O time deve ser balanceado, buscando cobrir as fraquezas dos ginasios e das fases de cada jogo.
        - Para cada Pokémon escolhido, você deve explicar por que ele se encaixa no estilo pedido, qual o papel dele no time (atacante, tanque, suporte...), recomendar 4 movimentos, um item recomendado.
        - O campo "estilo" é uma restrição OBRIGATÓRIA e deve ser seguida acima de qualquer outra consideração, inclusive balanceamento. Se o usuário pedir "apenas formas base", NENHUM Pokémon evoluído pode aparecer no time, sem exceções. Se pedir "apenas tipo fogo", todos os 6 devem ser do tipo fogo. O estilo do usuário é lei — não sugira algo "melhor" se não foi pedido.
        - Os nomes dos Pokémons devem ser escritos EXATAMENTE como aparecem
        na lista de disponíveis fornecida, em letras minúsculas e com hífens
        onde necessário. Nunca invente ou modifique nomes.
        - Para formas regionais, use SEMPRE o formato da PokéAPI: nome-região (ex: ninetales-alola, slowpoke-galar, zoroark-hisui). NUNCA use o formato alolan-nome, galarian-nome ou hisuian-nome.
        - Use EXATAMENTE os nomes da lista de Pokémons disponíveis fornecida.
        - REGRA ABSOLUTA DE INICIAIS: Em cada jogo, o jogador só pode obter UM Pokémon inicial. A lista de iniciais do jogo será fornecida. Você DEVE incluir NO MÁXIMO UM deles no time. Incluir dois ou mais iniciais do mesmo jogo é fisicamente impossível no jogo e torna a resposta completamente inválida.
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
                "justificativa": "por que este pokemon"
                }}
            ],
            "estrategia_geral": "descrição da estratégia"
            }}'
        """

############################################################

def montar_user_prompt(jogo: str, estilo: str, favoritos: list[str], pokemons_disponiveis: list[str], iniciais: list[str], incluir_lendarios: bool):

    lista_completa = ', '.join(pokemons_disponiveis)
    favoritos_str = ', '.join(favoritos) if favoritos else "nenhum"

    if iniciais is None:
        iniciais_str = "RESTRIÇÃO DE INICIAIS: Use seu conhecimento para identificar os iniciais deste jogo. Escolha NO MÁXIMO UM. Os demais não podem aparecer no time. Use a forma final da linha evolutiva escolhida."
    elif len(iniciais) == 0:
        iniciais_str = "Este jogo não possui iniciais tradicionais, sem restrição de inicial."
    else:
        if jogo in ["lets-go-pikachu", "lets-go-eevee"]:
            nomes = ', '.join(iniciais)
            iniciais_str = f"INICIAL OBRIGATÓRIO: {nomes}. Bulbasaur, Charmander e Squirtle PODEM aparecer juntos pois são obtidos como presente de NPC."
        else:
            overrides = FORMA_FINAL_INICIAL_OVERRIDE.get(jogo, {})
            formas_finais = [overrides.get(i, FORMA_FINAL_INICIAL.get(i, i)) for i in iniciais]
            pares = ', '.join(f"{base} → {final}" for base, final in zip(iniciais, formas_finais))
            nomes_finais = ', '.join(formas_finais)
            iniciais_str = (
                f"⛔ RESTRIÇÃO ABSOLUTA DE INICIAIS:\n"
                f"Famílias de iniciais deste jogo (base → forma final): {pares}\n"
                f"O jogador SÓ PODE OBTER UMA família durante o jogo.\n"
                f"Escolha EXATAMENTE UMA forma final para o time: {nomes_finais}\n"
                f"Nenhum outro membro dessas famílias pode aparecer no time.\n"
                f"Violar esta regra torna o time inválido."
            )
    
    if incluir_lendarios:
        lendarios_str = "Pokémons lendários e míticos PODEM ser incluídos no time."
    else:
        lendarios_str = "NUNCA inclua Pokémons lendários ou míticos no time, sem exceções."
    
    return f"""
    Jogo: {jogo}
    Estilo desejado: {estilo}
    Pokémons favoritos para incluir obrigatoriamente: {favoritos_str}
    Complete os {6 - len(favoritos)} restantes com as melhores escolhas para o estilo pedido.

    {iniciais_str}
    {lendarios_str}

    ATENÇÃO: Use os nomes EXATAMENTE como estão na lista abaixo.
    Pokémons disponíveis neste jogo (escolha APENAS desta lista):
    {lista_completa}
    
    Monte o time seguindo as regras e o formato definidos.
    """

############################################################

# sugerir o time de acordo com os prompts e a resposta da IA



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
        iniciais = INICIAIS_POR_JOGO.get(request.jogo.lower(), None)

        system_prompt = montar_system_prompt()
        user_prompt = montar_user_prompt(request.jogo, request.estilo, request.favoritos, pokemons_disponiveis, iniciais, request.incluir_lendarios)

        MAX_TENTATIVAS = 3
        erro_validacao = None

        for tentativa in range(MAX_TENTATIVAS):
            mensagens = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            if tentativa > 0 and erro_validacao:
                mensagens.append({"role": "assistant", "content": texto_resposta})
                mensagens.append({"role": "user", "content": f"❌ Time inválido: {erro_validacao}. Corrija e retorne apenas o JSON corrigido."})

            resposta_ia = cliente_ia.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=mensagens,
                max_tokens=2300,
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            texto_resposta = resposta_ia.choices[0].message.content
            dados_ia = json.loads(texto_resposta)
            nomes_time = [p["pokemon"] for p in dados_ia["time"]]
            erro_validacao = None

            # Corrige nomes próximos via difflib
            nomes_invalidos = [n for n in nomes_time if n not in pokemons_disponiveis]
            if nomes_invalidos:
                for pokemon in dados_ia["time"]:
                    if pokemon["pokemon"] not in pokemons_disponiveis:
                        sugestoes = get_close_matches(pokemon["pokemon"], pokemons_disponiveis, n=1, cutoff=0.6)
                        if sugestoes:
                            pokemon["pokemon"] = sugestoes[0]
                nomes_time = [p["pokemon"] for p in dados_ia["time"]]
                nomes_invalidos = [n for n in nomes_time if n not in pokemons_disponiveis]
                if nomes_invalidos:
                    erro_validacao = f"nomes inválidos: {nomes_invalidos}"
                    continue

            # Valida restrição de iniciais por família
            if iniciais:
                familias_no_time = {}
                for p in dados_ia["time"]:
                    familia = FAMILIA_INICIAL.get(p["pokemon"])
                    if familia and familia in iniciais:
                        familias_no_time[familia] = p["pokemon"]
                if len(familias_no_time) > 1:
                    erro_validacao = f"mais de uma família de inicial incluída: {familias_no_time}. Inclua apenas UMA."
                    continue

            break  # time válido

        if erro_validacao:
            raise HTTPException(status_code=400, detail=f"A IA não conseguiu gerar um time válido após {MAX_TENTATIVAS} tentativas. Último erro: {erro_validacao}")

        analise_time_gerado = logica_analisar_time(nomes_time)
        
        if "erro" in analise_time_gerado:
            raise HTTPException(
            status_code=400,
            detail=f"Erro ao analisar time: {analise_time_gerado['erro']}. A IA pode ter sugerido um Pokémon com nome inválido."
        )

        for i, pokemon in enumerate(dados_ia["time"]):
            pokemon["tipos"] = analise_time_gerado["detalhes_por_pokemon"][i]["tipos"]

            if request.incluir_localizacao:
                loc = buscar_localizacao(pokemon["pokemon"], request.jogo)
                pokemon["localizacao"] = loc


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
    
############################################################

def extrair_condicao(detalhes: list, nome_pokemon: str) -> str:
    if not detalhes:
        return "condição desconhecida"
    
    d = detalhes[0]  # pega o primeiro detalhe
    trigger = d["trigger"]["name"]
    
    if trigger == "level-up":
        # como pegar o nível?
        nivel = d.get("min_level", "desconhecido")
        
        if d.get("gender") == 1:
            return f"Evoluir {nome_pokemon} fêmea no nível {nivel}"
        
        elif d.get("gender") == 2:
            return f"Evoluir {nome_pokemon} macho no nível {nivel}"
       
        return f"evolui no nível {nivel}"
    
    elif trigger == "use-item":
        # como pegar o item?
        item = d.get("item", {}).get("name", "desconhecido")

        if d.get("gender") == 1:
            return f"Usar {item} em fêmea"

        return f"evolui usando o item {item}"
    
    elif trigger == "trade":
        return "evolui por troca"
    
    else:
        return trigger

############################################################

def buscar_localizacao(nome_pokemon: str, jogo: str):
    try:
        return _buscar_localizacao(nome_pokemon, jogo)
    except Exception:
        return {
            "pokemon_base": nome_pokemon,
            "localizacao": "Localização não disponível. Consulte Bulbapedia ou Serebii.",
            "evolucao": "Não disponível"
        }

############################################################

def _buscar_localizacao(nome_pokemon: str, jogo: str):
    def buscar_na_cadeia(no, nome_alvo, caminho=[]):
        nome_atual = no["species"]["name"]
        
        # Caso base — achou!
        if nome_atual == nome_alvo:
            return caminho
        
        for evolucao in no["evolves_to"]:
            
            detalhes = evolucao["evolution_details"]
            condicao = extrair_condicao(detalhes, nome_pokemon)  
            
            resultado = buscar_na_cadeia(
                evolucao,
                nome_alvo,
                caminho + [condicao]  
            )
            
            if resultado is not None:
                return resultado
        
        return None
    
    especie = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{nome_pokemon}").json()
    url_cadeia = especie["evolution_chain"]["url"]
    cadeia = requests.get(url_cadeia).json()
    
    pokemon_base = cadeia["chain"]["species"]["name"]

    encontros_raw = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_base}/encounters").json() 

    locais=[]

    for encontro in encontros_raw:
        for versao in encontro["version_details"]:
            if versao["version"]["name"] == jogo:
                locais.append(encontro["location_area"]["name"])
                break
    
    if not locais:
        localizacao_str = "Localização não disponível. Consulte Bulbapedia ou Serebii."
    else:
        localizacao_str = ', '.join(locais)
    

    condicoes = buscar_na_cadeia(cadeia["chain"], nome_pokemon)
    
    return {
    "pokemon_base": pokemon_base,
    "localizacao": localizacao_str,
    "evolucao": condicoes if condicoes else "Não precisa evoluir"
    }

############################################################

# Endpoint para comparar dois times

class RequestCompararTimes(BaseModel):
    time_a: list[str] 
    time_b: list[str] 

def logica_comparar_times(time_a, time_b):
    matchups = []  

    for pokemon_b in time_b:
        
        resposta_b = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_b.lower()}").json()
        tipos_b = [t["type"]["name"] for t in resposta_b["types"]]

        
        fraquezas_b = []
        for tipo in tipos_b:
            for f in FRAQUEZAS.get(tipo, []):
                if f not in fraquezas_b:
                    fraquezas_b.append(f)

        
        scores = {}

        for pokemon_a in time_a:
            
            resposta_a = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_a.lower()}").json()
            tipos_a = [t["type"]["name"] for t in resposta_a["types"]]

            # Conta quantos tipos do pokemon_a batem nas fraquezas do pokemon_b
            score = 0
            for tipo in tipos_a:
                if tipo in fraquezas_b:
                    score += 1
            scores[pokemon_a] = score

        top_counters = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        top_counters = [{"pokemon": p, "score": s} for p, s in top_counters if s > 0]
        matchups.append({
            "adversario": pokemon_b,
            "tipos_adversario": tipos_b,
            "fraquezas_adversario": fraquezas_b,
            "counters": top_counters if top_counters else [{"pokemon": "sem counter claro", "score": 0}]
        })
    return {"matchups": matchups}
    
    
@app.post("/comparar-times")
def comparar_times(request: RequestCompararTimes):
    return logica_comparar_times(request.time_a, request.time_b)

