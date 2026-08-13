export default function LoadingState({ label = 'Loading market data…', compact = false }) {
  return <div className={`loading-state${compact ? ' compact' : ''}`} role="status"><div className="spinner" /><span>{label}</span></div>
}
