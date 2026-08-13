import { lazy, Suspense } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Home from './pages/Home.jsx'

const Dashboard = lazy(() => import('./pages/Dashboard.jsx'))

function AppLayout() {
  return (
    <div className="app-shell">
      <Navbar />
      <Suspense fallback={<main className="route-loading"><div className="spinner" /><span>Loading page…</span></main>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Suspense>
      <footer>
        <div className="container">
          <span className="logo footer-logo"><span className="logo-mark">F</span>FridgeSpy</span>
          <p>Smarter refrigerator shopping, powered by Australian market data.</p>
        </div>
      </footer>
    </div>
  )
}

export default function App() {
  return <BrowserRouter><AppLayout /></BrowserRouter>
}
