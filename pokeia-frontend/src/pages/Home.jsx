import { useNavigate } from 'react-router-dom'

function Home() {
  const navigate = useNavigate()

  const cards = [
    {
      titulo: 'Sugerir time',
      descricao: 'Informe o jogo e estilo. A IA monta o time com movimentos, itens e localização.',
      rota: '/sugerir',
      sprite: 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/65.png',
      cor: 'bg-purple-900'
    },
    {
      titulo: 'Chat interativo',
      descricao: 'Converse com a IA e monte seu time progressivamente através de perguntas.',
      rota: '/chat',
      sprite: 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png',
      cor: 'bg-yellow-900'
    },
    {
      titulo: 'Comparar times',
      descricao: 'Insira dois times e descubra os melhores matchups e counters para cada batalha.',
      rota: '/comparar',
      sprite: 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/9.png',
      cor: 'bg-blue-900'
    }
  ]

  return (
    <div className="max-w-4xl mx-auto px-6 py-16 text-center">
      <h1 className="text-4xl font-medium mb-4 text-white">Monte o seu time Pokemon perfeito!</h1>
      <p className="text-base text-gray-400 mb-12 max-w-lg mx-auto">
        Descreva seu estilo de jogo e deixe a inteligência artificial sugerir o time ideal para você.
      </p>

      <div className="grid grid-cols-3 gap-4 items-stretch">
        {cards.map((card) => (
          <div
            key={card.rota}
            onClick={() => navigate(card.rota)}
            className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-left cursor-pointer hover:border-gray-500 transition-colors h-full"
          >
            <img
                src={card.sprite}
                alt={card.titulo}
                className="w-20 h-20 object-contain mb-3"
                style={{ imageRendering: 'pixelated' }}
            />
            <h3 className="text-base font-medium mb-2 text-white">{card.titulo}</h3>
            <p className="text-sm text-gray-400 leading-relaxed">{card.descricao}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Home