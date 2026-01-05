import { useState, useEffect } from 'react'
import './ProjectList.css'

function ProjectList({ onCreateProject, onProjectSelect }) {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/projects')
      if (!response.ok) throw new Error('Failed to fetch projects')
      const data = await response.json()
      setProjects(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (projectId, e) => {
    e.stopPropagation()
    if (!confirm('Are you sure you want to delete this project?')) return

    try {
      const response = await fetch(`/api/projects/${projectId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to delete project')
      }
      fetchProjects()
    } catch (err) {
      alert(`Error deleting project: ${err.message}`)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      created: { label: 'Created', class: 'status-created' },
      blueprint_generated: { label: 'Blueprint Ready', class: 'status-blueprint' },
      blueprint_approved: { label: 'Blueprint Approved', class: 'status-approved' },
      schema_generated: { label: 'Content Generated', class: 'status-schema' },
      completed: { label: 'Completed', class: 'status-completed' },
    }
    const info = statusMap[status] || { label: status, class: 'status-default' }
    return <span className={`status-badge ${info.class}`}>{info.label}</span>
  }

  if (loading) return <div className="loading">Loading projects...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="project-list">
      <div className="list-header">
        <h2>Your Projects</h2>
        <button className="btn btn-primary" onClick={onCreateProject}>
          Create New Project
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state">
          <p>No projects yet. Create your first knowledge website!</p>
          <button className="btn btn-primary" onClick={onCreateProject}>
            Get Started
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div
              key={project.id}
              className="project-card"
              onClick={() => onProjectSelect(project.id)}
            >
              <div className="project-card-header">
                <h3>{project.topic}</h3>
                {getStatusBadge(project.status)}
              </div>
              <div className="project-card-meta">
                <span>Depth: {project.config.depth}</span>
                <span>Tone: {project.config.tone}</span>
              </div>
              <div className="project-card-footer">
                <span className="project-date">{formatDate(project.created_at)}</span>
                <button
                  className="btn-delete"
                  onClick={(e) => handleDelete(project.id, e)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ProjectList
