import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Home from './pages/Home.jsx'
import SubmitSolution from './pages/SubmitSolution.jsx'
import Feedback from './pages/Feedback.jsx'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/submit" element={<SubmitSolution />} />
          <Route path="/feedback" element={<Feedback />} />
        </Routes>
      </main>
    </div>
  )
}
