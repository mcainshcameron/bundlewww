import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..models import Project, Blueprint
from ..models.schema import WebsiteSchema


class PersistenceService:
    """JSON flat-file persistence service"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.projects_dir = self.data_dir / "projects"
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure required directories exist"""
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def _project_dir(self, project_id: str) -> Path:
        """Get project directory path"""
        return self.projects_dir / project_id

    def _ensure_project_dir(self, project_id: str) -> Path:
        """Ensure project directory exists"""
        project_dir = self._project_dir(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    # Project methods
    def save_project(self, project: Project) -> None:
        """Save project metadata"""
        project_dir = self._ensure_project_dir(project.id)
        project_file = project_dir / "project.json"

        # Convert datetime to ISO format
        project_dict = project.model_dump()
        project_dict['created_at'] = project.created_at.isoformat()

        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_dict, f, indent=2, ensure_ascii=False)

    def get_project(self, project_id: str) -> Optional[Project]:
        """Load project by ID"""
        project_file = self._project_dir(project_id) / "project.json"
        if not project_file.exists():
            return None

        with open(project_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert ISO format back to datetime
            if 'created_at' in data and isinstance(data['created_at'], str):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            return Project(**data)

    def list_projects(self) -> List[Project]:
        """List all projects"""
        projects = []
        if not self.projects_dir.exists():
            return projects

        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                project = self.get_project(project_dir.name)
                if project:
                    projects.append(project)

        # Sort by creation date, newest first
        projects.sort(key=lambda p: p.created_at, reverse=True)
        return projects

    def delete_project(self, project_id: str) -> bool:
        """Delete project and all associated data"""
        import shutil
        import time
        import stat

        project_dir = self._project_dir(project_id)
        if not project_dir.exists():
            return False

        def handle_remove_readonly(func, path, exc):
            """Error handler for Windows readonly files"""
            try:
                if not os.access(path, os.W_OK):
                    # Try to make the file writable
                    os.chmod(path, stat.S_IWUSR | stat.S_IREAD)
                    time.sleep(0.1)  # Brief pause for Windows
                    func(path)
                else:
                    # If we can access it, try again
                    time.sleep(0.1)
                    func(path)
            except Exception:
                # Ignore errors in the error handler
                pass

        # Try to delete with retries for Windows file locking
        max_retries = 5
        for attempt in range(max_retries):
            try:
                shutil.rmtree(project_dir, onerror=handle_remove_readonly)
                # Double-check if deletion succeeded
                if not project_dir.exists():
                    return True
                # If directory still exists, wait and retry
                if attempt < max_retries - 1:
                    time.sleep(0.5)
            except Exception as e:
                if attempt < max_retries - 1:
                    # Wait and retry
                    time.sleep(0.5)
                else:
                    # Check one more time if deletion actually succeeded
                    if not project_dir.exists():
                        return True
                    # Still exists, raise the error
                    raise PermissionError(f"Could not delete project directory: {str(e)}")

        # Final check after all retries
        return not project_dir.exists()

    # Blueprint methods
    def save_blueprint(self, blueprint: Blueprint) -> None:
        """Save blueprint"""
        project_dir = self._ensure_project_dir(blueprint.project_id)
        blueprint_file = project_dir / f"blueprint_{blueprint.id}.json"

        with open(blueprint_file, 'w', encoding='utf-8') as f:
            json.dump(blueprint.model_dump(), f, indent=2, ensure_ascii=False)

    def get_blueprint(self, project_id: str, blueprint_id: str) -> Optional[Blueprint]:
        """Load blueprint by ID"""
        blueprint_file = self._project_dir(project_id) / f"blueprint_{blueprint_id}.json"
        if not blueprint_file.exists():
            return None

        with open(blueprint_file, 'r', encoding='utf-8') as f:
            return Blueprint(**json.load(f))

    # Schema methods
    def save_schema(self, schema: WebsiteSchema) -> None:
        """Save website schema"""
        project_dir = self._ensure_project_dir(schema.project_id)
        schema_file = project_dir / f"schema_{schema.id}.json"

        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema.model_dump(), f, indent=2, ensure_ascii=False)

    def get_schema(self, project_id: str, schema_id: str) -> Optional[WebsiteSchema]:
        """Load schema by ID"""
        schema_file = self._project_dir(project_id) / f"schema_{schema_id}.json"
        if not schema_file.exists():
            return None

        with open(schema_file, 'r', encoding='utf-8') as f:
            return WebsiteSchema(**json.load(f))

    # Website artifact methods
    def get_website_path(self, project_id: str, schema_id: str) -> Path:
        """Get path to website artifact directory"""
        return self._project_dir(project_id) / f"website_{schema_id}"

    def ensure_website_dir(self, project_id: str, schema_id: str) -> Path:
        """Ensure website directory exists"""
        website_dir = self.get_website_path(project_id, schema_id)
        website_dir.mkdir(parents=True, exist_ok=True)
        return website_dir
