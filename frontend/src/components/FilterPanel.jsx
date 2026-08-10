export default function FilterPanel({ filters, onChange, onSubmit, onClear, loading }) {
  const update = (event) => onChange(event.target.name, event.target.value)

  return (
    <form className="filter-panel" onSubmit={onSubmit}>
      <div className="filter-heading">
        <div>
          <span className="eyebrow dark">Smart search</span>
          <h2>Filter the market</h2>
        </div>
        <button className="text-button" type="button" onClick={onClear}>Clear filters</button>
      </div>
      <div className="filter-grid">
        <label className="search-field">
          Search model or product
          <input name="search" value={filters.search} onChange={update} placeholder="e.g. French door or RF522" />
        </label>
        <label>
          Brand
          <input name="brand" value={filters.brand} onChange={update} placeholder="e.g. Samsung" />
        </label>
        <label>
          Retailer
          <input name="retailer" value={filters.retailer} onChange={update} placeholder="e.g. Appliances Online" />
        </label>
        <label>
          Minimum price
          <div className="currency-input"><span>$</span><input name="min_price" type="number" min="0" step="1" value={filters.min_price} onChange={update} placeholder="500" /></div>
        </label>
        <label>
          Maximum price
          <div className="currency-input"><span>$</span><input name="max_price" type="number" min="0" step="1" value={filters.max_price} onChange={update} placeholder="3000" /></div>
        </label>
        <button className="primary-button" type="submit" disabled={loading}>{loading ? 'Searching…' : 'Search fridges'}</button>
      </div>
    </form>
  )
}
