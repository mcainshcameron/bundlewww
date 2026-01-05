import './PipelineProgress.css'

function PipelineProgress({ events, onCancel }) {
  // Find the latest event that has a progress value
  const latestProgressEvent = [...events].reverse().find(e => typeof e.progress === 'number')

  const getEventIcon = (eventType) => {
    const icons = {
      blueprint_start: '🏗️',
      blueprint_complete: '✓',
      chapter_schema_start: '📝',
      chapter_schema_complete: '✓',
      render_start: '🎨',
      render_complete: '✓',
      export_ready: '✓',
      error: '❌',
      progress: '⏳',
    }
    return icons[eventType] || '•'
  }

  const getEventClass = (eventType) => {
    if (eventType === 'error') return 'event-error'
    if (eventType.includes('complete') || eventType === 'export_ready') return 'event-success'
    if (eventType.includes('start')) return 'event-info'
    return 'event-progress'
  }

  return (
    <div className="pipeline-progress">
      <div className="progress-header">
        <h4>Generation Progress</h4>
        {latestProgressEvent && (
          <span className="progress-percentage">{Math.round(latestProgressEvent.progress)}%</span>
        )}
      </div>

      {latestProgressEvent && (
        <div className="progress-bar-container">
          <div
            className="progress-bar-fill"
            style={{ width: `${latestProgressEvent.progress}%` }}
          />
        </div>
      )}

      <div className="events-list">
        {events
          .filter(event => {
            // Hide "start" events once the corresponding "complete" event exists
            if (event.event_type === 'chapter_schema_start') {
              const chapterId = event.data?.chapter_id
              return !events.some(e =>
                e.event_type === 'chapter_schema_complete' &&
                e.data?.chapter_id === chapterId
              )
            }
            return true
          })
          .map((event, idx) => (
            <div key={idx} className={`event-item ${getEventClass(event.event_type)}`}>
              <span className="event-icon">{getEventIcon(event.event_type)}</span>
              <span className="event-message">{event.message}</span>
              {typeof event.progress === 'number' && (
                <span className="event-progress">{Math.round(event.progress)}%</span>
              )}
            </div>
          ))
        }
      </div>

      <div className="loading-indicator">
        <div className="spinner"></div>
        <span>Generating...</span>
      </div>

      {onCancel && (
        <div className="cancel-section">
          <button className="btn-cancel" onClick={onCancel}>
            Cancel Generation
          </button>
        </div>
      )}
    </div>
  )
}

export default PipelineProgress
