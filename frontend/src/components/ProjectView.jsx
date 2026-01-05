import { useState, useEffect, useRef } from 'react'
import './ProjectView.css'
import BlueprintReview from './BlueprintReview'
import PipelineProgress from './PipelineProgress'
import WebsitePreview from './WebsitePreview'

function ProjectView({ projectId, onBack }) {
  const [project, setProject] = useState(null)
  const [blueprint, setBlueprint] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentPhase, setCurrentPhase] = useState('blueprint') // blueprint, content, render, preview
  const [isGenerating, setIsGenerating] = useState(false)
  const [events, setEvents] = useState([])
  const abortControllerRef = useRef(null)

  useEffect(() => {
    fetchProject()
  }, [projectId])

  const fetchProject = async (updatePhase = true) => {
    try {
      setLoading(true)
      const response = await fetch(`/api/projects/${projectId}`)
      if (!response.ok) throw new Error('Failed to fetch project')
      const data = await response.json()
      setProject(data)

      // Only update phase if not actively generating
      if (updatePhase && !isGenerating) {
        // Determine current phase based on project status
        if (data.status === 'created') {
          setCurrentPhase('blueprint')
        } else if (data.status === 'blueprint_generated') {
          setCurrentPhase('blueprint')
          fetchBlueprint(data)
        } else if (data.status === 'blueprint_approved') {
          setCurrentPhase('content')
        } else if (data.status === 'generating_content') {
          // Content generation in progress - stay on content phase
          setCurrentPhase('content')
        } else if (data.status === 'schema_generated') {
          setCurrentPhase('render')
        } else if (data.status === 'rendering') {
          // Website rendering in progress - stay on render phase
          setCurrentPhase('render')
        } else if (data.status === 'completed') {
          setCurrentPhase('preview')
        }
      } else if (data.status === 'blueprint_generated') {
        // Always fetch blueprint if available, even during generation
        fetchBlueprint(data)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchBlueprint = async (proj = project) => {
    try {
      const response = await fetch(`/api/projects/${projectId}/blueprint`)
      if (response.ok) {
        const data = await response.json()
        setBlueprint(data)
      }
    } catch (err) {
      console.error('Failed to fetch blueprint:', err)
    }
  }

  const handleCancelGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setIsGenerating(false)
      setEvents((prev) => [
        ...prev,
        {
          event_type: 'error',
          message: 'Generation cancelled by user',
          data: { cancelled: true },
        },
      ])
    }
  }

  const handleGenerateBlueprint = async () => {
    setIsGenerating(true)
    setEvents([])
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch(`/api/projects/${projectId}/generate/blueprint`, {
        signal: abortControllerRef.current.signal,
      })
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const eventData = JSON.parse(line.slice(6))
            setEvents((prev) => [...prev, eventData])

            if (eventData.event_type === 'blueprint_complete') {
              await fetchProject(false)
              await fetchBlueprint()
            }
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        // Cancellation is already handled
        return
      }
      setError(`Blueprint generation failed: ${err.message}`)
    } finally {
      abortControllerRef.current = null
      setIsGenerating(false)
      // Always fetch project status after generation ends to sync with backend
      await fetchProject(true)
    }
  }

  const handleApproveBlueprint = async () => {
    try {
      const response = await fetch(`/api/projects/${projectId}/blueprint/approve`, {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to approve blueprint')
      await fetchProject()
      setCurrentPhase('content')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleGenerateContent = async () => {
    // Prevent starting if already generating
    if (isGenerating) {
      return
    }

    setIsGenerating(true)
    setEvents([])
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch(`/api/projects/${projectId}/generate/content`, {
        signal: abortControllerRef.current.signal,
      })
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const eventData = JSON.parse(line.slice(6))
            setEvents((prev) => [...prev, eventData])

            if (eventData.event_type === 'chapter_schema_complete' && eventData.progress === 100) {
              await fetchProject(false)
              setCurrentPhase('render')
            }
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        return
      }
      setError(`Content generation failed: ${err.message}`)
    } finally {
      abortControllerRef.current = null
      setIsGenerating(false)
      // Always fetch project status after generation ends to sync with backend
      await fetchProject(true)
    }
  }

  const handleRenderWebsite = async () => {
    setIsGenerating(true)
    setEvents([])
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch(`/api/projects/${projectId}/generate/website`, {
        signal: abortControllerRef.current.signal,
      })
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const eventData = JSON.parse(line.slice(6))
            setEvents((prev) => [...prev, eventData])

            if (eventData.event_type === 'export_ready') {
              await fetchProject(false)
              setCurrentPhase('preview')
            }
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        return
      }
      setError(`Website rendering failed: ${err.message}`)
    } finally {
      abortControllerRef.current = null
      setIsGenerating(false)
      // Always fetch project status after generation ends to sync with backend
      await fetchProject(true)
    }
  }

  if (loading) return <div className="loading">Loading project...</div>
  if (error && !project) return <div className="error">Error: {error}</div>
  if (!project) return null

  return (
    <div className="project-view">
      <div className="project-header">
        <button className="btn btn-secondary" onClick={onBack}>
          ← Back to Projects
        </button>
        <div className="project-info">
          <h2>{project.topic}</h2>
          <div className="project-meta">
            <span>Depth: {project.config.depth}</span>
            <span>Tone: {project.config.tone}</span>
            <span>Status: {project.status}</span>
          </div>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="project-content">
        {currentPhase === 'blueprint' && (
          <div className="phase-section">
            <h3>Blueprint Phase</h3>
            <p>
              Generate a structural blueprint for your website. This defines the chapters
              and sections without generating content yet.
            </p>

            {!blueprint && !isGenerating && (
              <button
                className="btn btn-primary"
                onClick={handleGenerateBlueprint}
              >
                Generate Blueprint
              </button>
            )}

            {isGenerating && (
              <PipelineProgress events={events} onCancel={handleCancelGeneration} />
            )}

            {blueprint && !blueprint.approved && (
              <BlueprintReview
                blueprint={blueprint}
                onApprove={handleApproveBlueprint}
                onRegenerate={handleGenerateBlueprint}
              />
            )}
          </div>
        )}

        {currentPhase === 'content' && (
          <div className="phase-section">
            <h3>Content Generation Phase</h3>
            <p>
              Generate all website content including prose, timelines, tables, and other
              structured content blocks.
            </p>

            {blueprint && (
              <details className="blueprint-collapsible">
                <summary>View Blueprint Structure</summary>
                <BlueprintReview blueprint={blueprint} readOnly={true} />
              </details>
            )}

            {!isGenerating && (
              <button
                className="btn btn-primary"
                onClick={handleGenerateContent}
              >
                Generate Content
              </button>
            )}

            {isGenerating && (
              <PipelineProgress events={events} onCancel={handleCancelGeneration} />
            )}
          </div>
        )}

        {currentPhase === 'preview' && (
          <div className="phase-section">
            <div className="preview-header-section">
              <div>
                <h3>Website Preview</h3>
                <p>Your website has been generated and is ready for download</p>
              </div>
              <button
                className="btn btn-secondary"
                onClick={() => setCurrentPhase('render')}
              >
                Re-render Website
              </button>
            </div>
            <WebsitePreview projectId={projectId} project={project} />
          </div>
        )}

        {currentPhase === 'render' && (project.status === 'schema_generated' || project.status === 'completed') && (
          <div className="phase-section">
            <h3>{project.status === 'completed' ? 'Re-render Website' : 'Website Rendering Phase'}</h3>
            <p>
              {project.status === 'completed'
                ? 'Re-render the static website from your existing content. This will update the HTML pages with the latest styles and layout without regenerating content.'
                : 'Render the static website from the generated content schema. This creates all HTML pages and assets.'
              }
            </p>

            {!isGenerating && (
              <button
                className="btn btn-primary"
                onClick={handleRenderWebsite}
              >
                {project.status === 'completed' ? 'Re-render Website' : 'Render Website'}
              </button>
            )}

            {isGenerating && (
              <PipelineProgress events={events} onCancel={handleCancelGeneration} />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ProjectView
