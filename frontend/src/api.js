const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

if (!API_BASE_URL) {
  throw new Error('VITE_API_BASE_URL is not configured')
}

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)

  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const body = await response.json()
      if (body?.detail) message = body.detail
    } catch {
      // Keep the status-based message when the response is not JSON.
    }
    throw new Error(message)
  }

  return response.json()
}

export function getHealth() {
  return request('/health')
}

export function getProducts(params = {}) {
  const query = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== '') {
      query.set(key, String(value).trim())
    }
  })

  const queryString = query.toString()
  return request(`/products${queryString ? `?${queryString}` : ''}`)
}

export function getStatisticsSummary() { return request('/statistics/summary') }
export function getRetailerStatistics() { return request('/statistics/retailers') }
export function getBrandStatistics() { return request('/statistics/brands') }
export function getPriceDistribution() { return request('/statistics/price-distribution') }
export function getPriceTrend() { return request('/statistics/price-trend') }
