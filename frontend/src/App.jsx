import { useState, useEffect } from 'react'
import './App.css'
import ProjectList from './components/ProjectList'
import ProjectCreate from './components/ProjectCreate'
import ProjectView from './components/ProjectView'

function App() {
  const [view, setView] = useState('list') // 'list', 'create', 'project'
  const [selectedProjectId, setSelectedProjectId] = useState(null)

  const handleCreateProject = () => {
    setView('create')
  }

  const handleProjectCreated = (projectId) => {
    setSelectedProjectId(projectId)
    setView('project')
  }

  const handleProjectSelected = (projectId) => {
    setSelectedProjectId(projectId)
    setView('project')
  }

  const handleBackToList = () => {
    setView('list')
    setSelectedProjectId(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 onClick={handleBackToList} style={{ cursor: 'pointer' }}>
          BundleWWW
        </h1>
      </header>

      <main className="app-main">
        {view === 'list' && (
          <ProjectList
            onCreateProject={handleCreateProject}
            onProjectSelect={handleProjectSelected}
          />
        )}

        {view === 'create' && (
          <ProjectCreate
            onProjectCreated={handleProjectCreated}
            onCancel={handleBackToList}
          />
        )}

        {view === 'project' && selectedProjectId && (
          <ProjectView
            projectId={selectedProjectId}
            onBack={handleBackToList}
          />
        )}
      </main>
    </div>
  )
}

export default App
