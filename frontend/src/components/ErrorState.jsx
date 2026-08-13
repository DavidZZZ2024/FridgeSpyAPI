export default function ErrorState({ message, onRetry }) {
  return (
    <div className="inline-state error-state" role="alert">
      <span className="status-icon">!</span><p>{message}</p>
      {onRetry && <button className="secondary-button" type="button" onClick={onRetry}>Try again</button>}
    </div>
  )
}
