import { useCallback, useEffect, useState } from 'react'
import { getProducts } from './api.js'
import FilterPanel from './components/FilterPanel.jsx'
import ProductCard from './components/ProductCard.jsx'

const emptyFilters = { search: '', brand: '', retailer: '', min_price: '', max_price: '' }

function normaliseProducts(data) {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.products)) return data.products
  return []
}

export default function App() {
  const [filters, setFilters] = useState(emptyFilters)
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadProducts = useCallback(async (params = {}) => {
    setLoading(true)
    setError('')
    try {
      const data = await getProducts({ ...params, limit: 100, offset: 0 })
      setProducts(normaliseProducts(data))
    } catch (requestError) {
      setProducts([])
      setError(requestError.message || 'We could not load fridge prices right now.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadProducts() }, [loadProducts])

  const handleChange = (name, value) => setFilters((current) => ({ ...current, [name]: value }))
  const handleSubmit = (event) => {
    event.preventDefault()
    if (filters.min_price && filters.max_price && Number(filters.min_price) > Number(filters.max_price)) {
      setError('Minimum price cannot be greater than maximum price.')
      return
    }
    loadProducts(filters)
  }
  const handleClear = () => {
    setFilters(emptyFilters)
    loadProducts()
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <nav className="nav container" aria-label="Main navigation">
          <a className="logo" href="#top" aria-label="FridgeSpy home"><span className="logo-mark">F</span>FridgeSpy</a>
          <span className="nav-tagline">Australian fridge price intelligence</span>
        </nav>
        <div id="top" className="hero-content container">
          <span className="eyebrow">Compare with confidence</span>
          <h1>Find the right fridge<br />at the right price.</h1>
          <p>Compare refrigerator prices across major Australian retailers.</p>
          <a className="hero-link" href="#results">Explore current prices <span aria-hidden="true">↓</span></a>
        </div>
        <div className="hero-glow" aria-hidden="true" />
      </header>

      <main className="container main-content">
        <FilterPanel filters={filters} onChange={handleChange} onSubmit={handleSubmit} onClear={handleClear} loading={loading} />
        <section id="results" className="results-section" aria-live="polite">
          <div className="results-heading">
            <div><span className="eyebrow dark">Live market data</span><h2>Available fridges</h2></div>
            {!loading && !error && <p>{products.length} {products.length === 1 ? 'result' : 'results'} found</p>}
          </div>

          {loading && <div className="status-card"><div className="spinner" /><h3>Checking the latest prices…</h3><p>This may take a moment while the market data loads.</p></div>}
          {!loading && error && <div className="status-card error"><span className="status-icon">!</span><h3>Something went wrong</h3><p>{error}</p><button className="secondary-button" onClick={() => loadProducts(filters)}>Try again</button></div>}
          {!loading && !error && products.length === 0 && <div className="status-card"><span className="status-icon">⌕</span><h3>No matching fridges</h3><p>Try widening your price range or removing a filter.</p><button className="secondary-button" onClick={handleClear}>Clear filters</button></div>}
          {!loading && !error && products.length > 0 && <div className="product-grid">{products.map((product, index) => <ProductCard key={`${product.retailer || 'retailer'}-${product.model || product.title || index}-${index}`} product={product} />)}</div>}
        </section>
      </main>
      <footer><div className="container"><a className="logo footer-logo" href="#top"><span className="logo-mark">F</span>FridgeSpy</a><p>Smarter refrigerator shopping, powered by Australian market data.</p></div></footer>
    </div>
  )
}
