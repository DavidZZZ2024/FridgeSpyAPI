export default function ChartCard({ title, subtitle, className = '', children }) {
  return (
    <section className={`chart-card ${className}`.trim()}>
      <div className="chart-heading"><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>
      {children}
    </section>
  )
}
