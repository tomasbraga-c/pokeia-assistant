import { NavLink } from 'react-router-dom'

function Navbar() {
  const linkBase = 'px-3 py-2 rounded-md text-sm text-gray-400 hover:bg-gray-800 hover:text-white transition-colors'
  const linkAtivo = 'px-3 py-2 rounded-md text-sm bg-gray-800 text-white'

  return (
    <nav className="flex items-center justify-between px-6 py-3 border-b border-gray-700 bg-gray-900">
      
      <NavLink to="/" className="text-base font-medium flex items-center gap-2 text-white">
        PokeIA
      </NavLink>

      <div className="flex gap-1">
        <NavLink 
            to="/sugerir"
            className={({ isActive }) => isActive ? linkAtivo : linkBase}
            >
            Sugerir time
        </NavLink>

        <NavLink 
            to="/chat"
            className={({ isActive }) => isActive ? linkAtivo : linkBase}
            >
            Chat
        </NavLink>

        <NavLink 
            to="/comparar"
            className={({ isActive }) => isActive ? linkAtivo : linkBase}
            >
            Comparar times
        </NavLink>
      </div>

    </nav>
  )
}

export default Navbar