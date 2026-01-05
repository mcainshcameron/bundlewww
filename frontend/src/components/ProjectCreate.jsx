import { useState, useEffect } from 'react'
import './ProjectCreate.css'

function ProjectCreate({ onProjectCreated, onCancel }) {
  const [topic, setTopic] = useState('')
  const [depth, setDepth] = useState('deep_dive')
  const [tone, setTone] = useState('professional')
  const [audienceLevel, setAudienceLevel] = useState('general')
  const [selectedModel, setSelectedModel] = useState('xAI: Grok Code Fast')
  const [generateImages, setGenerateImages] = useState(false)
  const [availableModels, setAvailableModels] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAvailableModels()
  }, [])

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch('/api/models')
      const data = await response.json()
      setAvailableModels(data.models || {})
    } catch (err) {
      console.error('Failed to fetch models:', err)
      setError('Failed to load available models. Please refresh the page.')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!topic.trim()) {
      setError('Please enter a topic')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic.trim(),
          config: {
            depth,
            tone,
            audience_level: audienceLevel,
            model: selectedModel,
            generate_images: generateImages,
          },
        }),
      })

      if (!response.ok) throw new Error('Failed to create project')

      const project = await response.json()
      onProjectCreated(project.id)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="project-create">
      <div className="create-header">
        <h2>Create New Knowledge Website</h2>
        <p>Configure your website generation preferences</p>
      </div>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit} className="create-form">
        <div className="card">
          <h3>Topic</h3>
          <div className="form-group">
            <label htmlFor="topic">
              What topic would you like to create a website about?
            </label>
            <input
              id="topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., History of Coffee, Quantum Computing, Climate Change"
              disabled={loading}
              required
            />
          </div>
        </div>

        <div className="card">
          <h3>Configuration</h3>

          <div className="form-group">
            <label htmlFor="depth">Content Depth</label>
            <select
              id="depth"
              value={depth}
              onChange={(e) => setDepth(e.target.value)}
              disabled={loading}
            >
              <option value="overview">Overview - Quick introduction</option>
              <option value="deep_dive">Deep Dive - Detailed exploration</option>
              <option value="comprehensive">Comprehensive - Complete coverage</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="tone">Writing Tone</label>
            <select
              id="tone"
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              disabled={loading}
            >
              <option value="introductory">Introductory - Beginner-friendly</option>
              <option value="professional">Professional - Clear and formal</option>
              <option value="academic">Academic - Scholarly style</option>
              <option value="casual">Casual - Conversational</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="audience">Target Audience</label>
            <input
              id="audience"
              type="text"
              value={audienceLevel}
              onChange={(e) => setAudienceLevel(e.target.value)}
              placeholder="e.g., general, students, professionals"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="model">AI Model</label>
            <select
              id="model"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={loading}
            >
              {Object.entries(availableModels).map(([id, name]) => (
                <option key={id} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group checkbox-group">
            <label htmlFor="generate-images" className="checkbox-label">
              <input
                id="generate-images"
                type="checkbox"
                checked={generateImages}
                onChange={(e) => setGenerateImages(e.target.checked)}
                disabled={loading}
              />
              <span>Generate AI images for chapters (requires FAL_KEY)</span>
            </label>
            <p className="form-helper">
              One hero image will be generated per chapter to enhance visual appeal
            </p>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ProjectCreate
