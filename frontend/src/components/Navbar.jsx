import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <header className="site-header">
      <nav className="nav container" aria-label="Main navigation">
        <NavLink className="logo" to="/" aria-label="FridgeSpy products">
          <span className="logo-mark">F</span>
          <span>FridgeSpy<small>Australian fridge price intelligence</small></span>
        </NavLink>
        <div className="nav-links">
          <NavLink to="/" end>Products</NavLink>
          <NavLink to="/dashboard">Dashboard</NavLink>
        </div>
      </nav>
    </header>
  )
}
