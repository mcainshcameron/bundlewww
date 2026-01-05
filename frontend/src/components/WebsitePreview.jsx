import './WebsitePreview.css'

function WebsitePreview({ projectId, project }) {
  const handleDownload = () => {
    window.open(`/api/projects/${projectId}/download`, '_blank')
  }

  const previewUrl = `/api/projects/${projectId}/preview/index.html`

  return (
    <div className="website-preview">
      <div className="preview-info">
        <p>
          Preview your website below or download the complete static website as a ZIP file.
        </p>
        <div className="preview-features">
          <span>✓ Fully offline-capable</span>
          <span>✓ No external dependencies</span>
          <span>✓ Complete with navigation</span>
          <span>✓ Mobile responsive</span>
        </div>
        <div className="preview-actions">
          <button className="btn btn-success" onClick={handleDownload}>
            Download Website
          </button>
        </div>
      </div>

      <div className="preview-container">
        <iframe
          src={previewUrl}
          title="Website Preview"
          className="preview-iframe"
        />
      </div>

      <div className="preview-footer">
        <p>
          The website preview shows the exact same files you'll receive in the
          download. It works completely offline once downloaded.
        </p>
      </div>
    </div>
  )
}

export default WebsitePreview
