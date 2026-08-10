function displayValue(value, fallback) {
  return value === null || value === undefined || value === '' ? fallback : String(value)
}

function formatPrice(value) {
  const amount = Number(value)
  if (!Number.isFinite(amount)) return 'Price unavailable'

  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
    maximumFractionDigits: Number.isInteger(amount) ? 0 : 2,
  }).format(amount)
}

export default function ProductCard({ product }) {
  const title = displayValue(product.title, product.model || 'Refrigerator')
  const dealUrl = product.url || product.product_url

  return (
    <article className="product-card">
      <div className="card-topline">
        <span className="retailer">{displayValue(product.retailer, 'Retailer unavailable')}</span>
        {product.brand && <span className="brand">{product.brand}</span>}
      </div>
      <div className="product-copy">
        <h3>{title}</h3>
        {product.model && <p className="model">Model {product.model}</p>}
      </div>
      <div className="card-footer">
        <strong className="price">{formatPrice(product.price_raw ?? product.price)}</strong>
        {dealUrl && (
          <a href={dealUrl} target="_blank" rel="noopener noreferrer" className="deal-link">
            View deal <span aria-hidden="true">↗</span>
          </a>
        )}
      </div>
    </article>
  )
}
