import { useState } from 'react'
import { sugerirTime } from '../services/api'

function SugerirTime() {
  const [form, setForm] = useState({
    jogo: '',
    estilo: '',
    favoritos: [],
    incluir_localizacao: true,
    incluir_lendarios: false
  })

  const [favoritoInput, setFavoritoInput] = useState('')
  const [resultado, setResultado] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState(null)
  const [cardAberto, setCardAberto] = useState(null)

  function adicionarFavorito() {
    const nome = favoritoInput.trim().toLowerCase()
    if (nome && !form.favoritos.includes(nome)) {
      setForm({ ...form, favoritos: [...form.favoritos, nome] })
    }
    setFavoritoInput('')
  }

  function removerFavorito(nome) {
    setForm({ ...form, favoritos: form.favoritos.filter(f => f !== nome) })
  }

  async function handleSubmit() {
    const favoritosPendentes = favoritoInput.trim().toLowerCase()
    const favoritosFinais = favoritosPendentes && !form.favoritos.includes(favoritosPendentes)
      ? [...form.favoritos, favoritosPendentes]
      : form.favoritos

    if (!form.jogo || !form.estilo) {
      setErro('Preencha o jogo e o estilo antes de continuar.')
      return
    }

    setCarregando(true)
    setErro(null)
    setResultado(null)
    setCardAberto(null)

    try {
      const dados = await sugerirTime({ ...form, favoritos: favoritosFinais })
      if (dados.detail) {
        setErro(dados.detail)
      } else {
        setResultado(dados)
        setFavoritoInput('')
      }
    } catch (e) {
      setErro('Erro ao conectar com o servidor.')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">

      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
        <h2 className="text-lg font-medium mb-5 text-white">Configurar sugestão</h2>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-400">Jogo</label>
            <input
              value={form.jogo}
              onChange={(e) => setForm({ ...form, jogo: e.target.value })}
              placeholder="ex: scarlet, red, sword..."
              className="border border-gray-600 rounded-lg px-3 py-2 text-sm bg-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-gray-400"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-gray-400">Estilo de jogo</label>
            <input
              value={form.estilo}
              onChange={(e) => setForm({ ...form, estilo: e.target.value })}
              placeholder="ex: ofensivo, balanceado, defensivo, pokemons formas bases..."
              className="border border-gray-600 rounded-lg px-3 py-2 text-sm bg-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-gray-400"
            />
          </div>
        </div>

        <div className="flex flex-col gap-1 mb-4">
          <label className="text-xs text-gray-400">Pokémons favoritos (opcional)</label>
          <div className="flex gap-2">
            <input
              value={favoritoInput}
              onChange={(e) => setFavoritoInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && adicionarFavorito()}
              placeholder="ex: greninja, charizard..."
              className="flex-1 border border-gray-600 rounded-lg px-3 py-2 text-sm bg-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-gray-400"
            />
            <button
              onClick={adicionarFavorito}
              className="px-4 py-2 text-sm border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-700"
            >
              Adicionar
            </button>
          </div>
          {form.favoritos.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {form.favoritos.map(f => (
                <span key={f} className="flex items-center gap-1 bg-gray-700 text-gray-300 text-xs px-3 py-1 rounded-full capitalize">
                  {f}
                  <button onClick={() => removerFavorito(f)} className="text-gray-500 hover:text-gray-300 ml-1">×</button>
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="border-t border-gray-700 pt-4 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white">Incluir localização</p>
              <p className="text-xs text-gray-500">Mostra onde encontrar cada Pokémon no jogo</p>
            </div>
            <input
              type="checkbox"
              checked={form.incluir_localizacao}
              onChange={(e) => setForm({ ...form, incluir_localizacao: e.target.checked })}
              className="w-4 h-4"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white">Incluir lendários</p>
              <p className="text-xs text-gray-500">Lendários são poderosos mas difíceis de capturar antes de zerar</p>
            </div>
            <input
              type="checkbox"
              checked={form.incluir_lendarios}
              onChange={(e) => setForm({ ...form, incluir_lendarios: e.target.checked })}
              className="w-4 h-4"
            />
          </div>
        </div>

        {erro && <p className="text-red-400 text-sm mt-4">{erro}</p>}

        <button
          onClick={handleSubmit}
          disabled={carregando}
          className="w-full mt-5 bg-white text-gray-900 py-2.5 rounded-lg text-sm hover:bg-gray-100 disabled:opacity-50 transition-colors font-medium"
        >
          {carregando ? 'Gerando time...' : 'Sugerir time'}
        </button>
      </div>

      {resultado && (
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h2 className="text-lg font-medium mb-2 text-white">Time sugerido</h2>
          <p className="text-sm text-gray-400 mb-5">{resultado.time_sugerido.estrategia_geral}</p>

          <div className="grid grid-cols-3 gap-4 mb-6">
            {resultado.time_sugerido.time.map((pokemon) => (
              <div key={pokemon.pokemon} className="bg-gray-700 rounded-xl p-4 flex flex-col items-center text-center">
                <img
                  src={`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${pokemon.id}.png`}
                  alt={pokemon.pokemon}
                  className="w-20 h-20 object-contain"
                  style={{ imageRendering: 'pixelated' }}
                  onError={(e) => e.target.style.display = 'none'}
                />
                <p className="text-sm font-medium capitalize mt-1 text-white">{pokemon.pokemon}</p>
                <p className="text-xs text-gray-400 mb-2">{pokemon.papel}</p>
                <div className="flex flex-wrap gap-1 justify-center mb-2">
                  {pokemon.tipos?.map(tipo => (
                    <span key={tipo} className="text-xs bg-blue-900 text-blue-300 px-2 py-0.5 rounded-full">{tipo}</span>
                  ))}
                </div>
                <p className="text-xs text-gray-400 italic mb-2">{pokemon.destaques}</p>
                <div className="text-xs text-gray-400">
                  {pokemon.movimentos?.join(' · ')}
                </div>
                <p className="text-xs text-gray-500 mt-1">Item: {pokemon.item}</p>

                {pokemon.localizacao && (
                  <>
                    <button
                      onClick={() => setCardAberto(cardAberto === pokemon.pokemon ? null : pokemon.pokemon)}
                      className="mt-3 text-xs text-gray-500 hover:text-gray-300 flex items-center gap-1"
                    >
                      {cardAberto === pokemon.pokemon ? 'Fechar ▲' : 'Ver localização ▼'}
                    </button>

                    {cardAberto === pokemon.pokemon && (
                      <div className="mt-3 w-full text-left border-t border-gray-600 pt-3">
                        <p className="text-xs text-gray-400">
                          <span className="font-medium text-gray-300">Capturar:</span> {pokemon.localizacao.pokemon_base}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          <span className="font-medium text-gray-300">Local:</span> {pokemon.localizacao.localizacao}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          <span className="font-medium text-gray-300">Evolução:</span>{' '}
                          {Array.isArray(pokemon.localizacao.evolucao)
                            ? pokemon.localizacao.evolucao.join(' → ')
                            : pokemon.localizacao.evolucao}
                        </p>
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-4 border-t border-gray-700 pt-4">
            <div className="bg-gray-700 rounded-lg p-4">
              <p className="text-xs text-gray-400 mb-1">Maior fraqueza</p>
              <p className="text-lg font-medium capitalize text-white">{resultado.analise.maior_fraqueza}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <p className="text-xs text-gray-400 mb-1">Maior vantagem</p>
              <p className="text-lg font-medium capitalize text-white">{resultado.analise.maior_vantagem}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SugerirTime