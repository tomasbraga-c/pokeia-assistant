import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import SugerirTime from './pages/SugerirTime'
import Chat from './pages/Chat'
import CompararTimes from './pages/CompararTimes'

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/sugerir" element={<SugerirTime />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/comparar" element={<CompararTimes />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App