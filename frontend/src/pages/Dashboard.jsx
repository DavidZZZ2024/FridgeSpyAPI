import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'
import {
  getBrandStatistics, getPriceDistribution, getPriceTrend,
  getRetailerStatistics, getStatisticsSummary,
} from '../api.js'
import ChartCard from '../components/ChartCard.jsx'
import ErrorState from '../components/ErrorState.jsx'
import LoadingState from '../components/LoadingState.jsx'
import StatCard from '../components/StatCard.jsx'

const endpointConfig = {
  summary: getStatisticsSummary,
  distribution: getPriceDistribution,
  brands: getBrandStatistics,
  retailers: getRetailerStatistics,
  trend: getPriceTrend,
}

const currency = new Intl.NumberFormat('en-AU', {
  style: 'currency', currency: 'AUD', maximumFractionDigits: 0,
})
const integer = new Intl.NumberFormat('en-AU', { maximumFractionDigits: 0 })

function formatCurrency(value) {
  const number = Number(value)
  return Number.isFinite(number) ? currency.format(number) : '—'
}

function formatCount(value) {
  const number = Number(value)
  return Number.isFinite(number) ? integer.format(number) : '—'
}

function formatDate(value, options = { day: 'numeric', month: 'short', year: 'numeric' }) {
  if (!value) return ''
  const date = new Date(`${String(value).slice(0, 10)}T00:00:00Z`)
  return Number.isNaN(date.getTime()) ? '' : new Intl.DateTimeFormat('en-AU', { ...options, timeZone: 'UTC' }).format(date)
}

function ChartState({ loading, error, emptyMessage, isEmpty, children }) {
  if (loading) return <LoadingState compact />
  if (error) return <ErrorState message={error} />
  if (isEmpty) return <div className="inline-state"><p>{emptyMessage}</p></div>
  return children
}

function MarketTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const item = payload[0]?.payload || {}
  return (
    <div className="chart-tooltip">
      <strong>{label}</strong>
      {payload.map((entry) => (
        <span key={entry.dataKey}>{entry.name}: {entry.dataKey === 'average_price' ? formatCurrency(entry.value) : formatCount(entry.value)}</span>
      ))}
      {payload.every((entry) => entry.dataKey !== 'average_price') && item.average_price != null && <span>Average price: {formatCurrency(item.average_price)}</span>}
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState({ summary: null, distribution: [], brands: [], retailers: [], trend: [] })
  const [loading, setLoading] = useState(Object.fromEntries(Object.keys(endpointConfig).map((key) => [key, true])))
  const [errors, setErrors] = useState({})

  const loadDashboard = useCallback(async () => {
    const entries = Object.entries(endpointConfig)
    setLoading(Object.fromEntries(entries.map(([key]) => [key, true])))
    setErrors({})
    const results = await Promise.allSettled(entries.map(([, request]) => request()))
    const nextData = {}
    const nextErrors = {}
    results.forEach((result, index) => {
      const key = entries[index][0]
      if (result.status === 'fulfilled') nextData[key] = result.value
      else {
        console.error(`Dashboard request failed: ${key}`, result.reason)
        nextErrors[key] = `Unable to load ${key === 'summary' ? 'market summary' : `${key} statistics`}.`
      }
    })
    setData((current) => ({ ...current, ...nextData }))
    setErrors(nextErrors)
    setLoading(Object.fromEntries(entries.map(([key]) => [key, false])))
  }, [])

  useEffect(() => { loadDashboard() }, [loadDashboard])

  const topBrands = useMemo(
    () => (Array.isArray(data.brands) ? [...data.brands].sort((a, b) => Number(b.product_count) - Number(a.product_count)).slice(0, 10) : []),
    [data.brands],
  )
  const distribution = useMemo(
    () => (Array.isArray(data.distribution) ? [...data.distribution].sort((a, b) => Number(a.sort_order) - Number(b.sort_order)) : []),
    [data.distribution],
  )
  const retailers = Array.isArray(data.retailers) ? data.retailers : []
  const trend = Array.isArray(data.trend) ? data.trend : []
  const summary = data.summary

  return (
    <main className="dashboard-page">
      <div className="container">
        <header className="dashboard-header">
          <div><span className="eyebrow dark">Market intelligence</span><h1>Market Dashboard</h1><p>Track pricing, brands and retailer activity across the Australian fridge market.</p></div>
          {summary?.latest_date && <span className="freshness"><i />Data updated: {formatDate(summary.latest_date)}</span>}
        </header>

        {errors.summary ? <div className="summary-error"><ErrorState message={errors.summary} onRetry={loadDashboard} /></div> : loading.summary ? <LoadingState label="Loading market summary…" /> : (
          <section className="stats-grid" aria-label="Market summary">
            <StatCard label="Total Products" value={formatCount(summary?.total_products)} />
            <StatCard label="Total Brands" value={formatCount(summary?.total_brands)} />
            <StatCard label="Retailers Tracked" value={formatCount(summary?.total_retailers)} />
            <StatCard label="Average Price" value={formatCurrency(summary?.average_price)} />
            <StatCard label="Median Price" value={formatCurrency(summary?.median_price)} />
          </section>
        )}

        <div className="dashboard-grid">
          <ChartCard title="Price Distribution" subtitle="Products in each price band">
            <ChartState loading={loading.distribution} error={errors.distribution} isEmpty={!distribution.some((item) => Number(item.count) > 0)} emptyMessage="No price distribution data available.">
              <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><BarChart data={distribution} margin={{ top: 8, right: 8, left: -15, bottom: 22 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="range" tick={{ fontSize: 11 }} angle={-18} textAnchor="end" interval={0} /><YAxis allowDecimals={false} tick={{ fontSize: 12 }} /><Tooltip content={<MarketTooltip />} /><Bar dataKey="count" name="Products" fill="#1769e8" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer></div>
            </ChartState>
          </ChartCard>

          <ChartCard title="Top Brands by Product Count" subtitle="Leading brands in the latest snapshot">
            <ChartState loading={loading.brands} error={errors.brands} isEmpty={!topBrands.length} emptyMessage="No brand statistics available.">
              <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><BarChart data={topBrands} layout="vertical" margin={{ top: 4, right: 18, left: 8, bottom: 4 }}><CartesianGrid strokeDasharray="3 3" horizontal={false} /><XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} /><YAxis type="category" dataKey="brand" width={92} tick={{ fontSize: 12 }} /><Tooltip content={<MarketTooltip />} /><Bar dataKey="product_count" name="Products" fill="#0b3978" radius={[0, 5, 5, 0]} /></BarChart></ResponsiveContainer></div>
            </ChartState>
          </ChartCard>

          <ChartCard title="Average Price Trend" subtitle="Daily average across unique retailer products" className="chart-card-wide">
            <ChartState loading={loading.trend} error={errors.trend} isEmpty={trend.length < 2} emptyMessage="Not enough historical data yet to show a price trend.">
              <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><LineChart data={trend} margin={{ top: 8, right: 18, left: 5, bottom: 4 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="date" tickFormatter={(value) => formatDate(value, { day: 'numeric', month: 'short' })} tick={{ fontSize: 12 }} minTickGap={25} /><YAxis domain={['auto', 'auto']} tickFormatter={(value) => `$${integer.format(value)}`} width={68} tick={{ fontSize: 12 }} /><Tooltip content={<MarketTooltip />} labelFormatter={(value) => formatDate(value)} /><Line type="monotone" dataKey="average_price" name="Average price" stroke="#1769e8" strokeWidth={3} dot={false} activeDot={{ r: 5 }} /></LineChart></ResponsiveContainer></div>
            </ChartState>
          </ChartCard>

          <ChartCard title="Products by Retailer" subtitle="Latest product coverage by retailer" className="chart-card-wide">
            <ChartState loading={loading.retailers} error={errors.retailers} isEmpty={!retailers.length} emptyMessage="No retailer data available.">
              <div className="chart-wrap retailer-chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={retailers} margin={{ top: 8, right: 12, left: -10, bottom: 10 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="retailer" tick={{ fontSize: 12 }} interval={0} /><YAxis allowDecimals={false} tick={{ fontSize: 12 }} /><Tooltip content={<MarketTooltip />} /><Bar dataKey="product_count" name="Products" fill="#2e7df5" radius={[5, 5, 0, 0]} maxBarSize={90} /></BarChart></ResponsiveContainer></div>
            </ChartState>
          </ChartCard>
        </div>
      </div>
    </main>
  )
}
