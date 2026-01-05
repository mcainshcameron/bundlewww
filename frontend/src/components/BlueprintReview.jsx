import './BlueprintReview.css'

function BlueprintReview({ blueprint, onApprove, onRegenerate, readOnly = false }) {
  return (
    <div className="blueprint-review">
      {!readOnly && (
        <div className="blueprint-header">
          <h4>Review Blueprint</h4>
          <p>Review the structure before generating content</p>
        </div>
      )}

      <div className="blueprint-content">
        {blueprint.chapters.map((chapter, idx) => (
          <div key={chapter.id} className="blueprint-chapter">
            <div className="chapter-header">
              <span className="chapter-number">Chapter {idx + 1}</span>
              <h5>{chapter.title}</h5>
            </div>
            <p className="chapter-purpose">{chapter.purpose}</p>

            <div className="chapter-sections">
              {chapter.sections.map((section) => (
                <div key={section.id} className="blueprint-section">
                  <strong>{section.title}</strong>
                  <p>{section.purpose}</p>
                  <div className="content-types">
                    {section.expected_content_types.map((type) => (
                      <span key={type} className="content-type-badge">
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {!readOnly && (
        <div className="blueprint-actions">
          <button className="btn btn-secondary" onClick={onRegenerate}>
            Regenerate Blueprint
          </button>
          <button className="btn btn-success" onClick={onApprove}>
            Approve & Continue
          </button>
        </div>
      )}
    </div>
  )
}

export default BlueprintReview
