"""
BundleWWW FastAPI Application
"""
import uuid
import json
import asyncio
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .models import (
    Project, ProjectCreate, Blueprint,
    PipelineEvent, EventType
)
from .models.schema import WebsiteSchema
from .services.persistence import PersistenceService
from .services.openrouter import OpenRouterService
from .services.fal import FALService
from .agents.architect import ArchitectAgent
from .agents.constructor import ConstructorAgent
from .agents.renderer import RendererAgent
from .agents.illustrator import IllustratorAgent

# Load environment variables
load_dotenv()

# Initialize services
persistence = PersistenceService()
openrouter_service = OpenRouterService()
fal_service = FALService()
architect_agent = ArchitectAgent(openrouter_service)
constructor_agent = ConstructorAgent(openrouter_service)
illustrator_agent = IllustratorAgent(openrouter_service, fal_service)
renderer_agent = RendererAgent()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    print("BundleWWW starting up...")
    yield
    # Shutdown
    print("BundleWWW shutting down...")


# Create FastAPI app
app = FastAPI(
    title="BundleWWW API",
    description="Generate complete, AI-powered static websites about any topic",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== PROJECT ENDPOINTS ====================

@app.get("/api/projects")
async def list_projects() -> List[Project]:
    """List all projects"""
    return persistence.list_projects()


@app.post("/api/projects")
async def create_project(project_create: ProjectCreate) -> Project:
    """Create a new project"""
    project = Project(
        id=str(uuid.uuid4()),
        topic=project_create.topic,
        config=project_create.config,
        status="created",
    )
    persistence.save_project(project)
    return project


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str) -> Project:
    """Get project by ID"""
    project = persistence.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.put("/api/projects/{project_id}/status")
async def update_project_status(project_id: str, status_update: dict):
    """Update project status"""
    project = persistence.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.status = status_update.get("status", project.status)
    persistence.save_project(project)
    return {"status": "updated"}


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        if not persistence.delete_project(project_id):
            raise HTTPException(status_code=404, detail="Project not found")
        return {"status": "deleted"}
    except PermissionError:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete project: files are currently in use. Please close any preview windows and try again."
        )


# ==================== BLUEPRINT ENDPOINTS ====================

@app.get("/api/projects/{project_id}/blueprint")
async def get_blueprint(project_id: str) -> Blueprint:
    """Get project blueprint"""
    project = persistence.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.blueprint_id:
        raise HTTPException(status_code=404, detail="Blueprint not generated yet")

    blueprint = persistence.get_blueprint(project_id, project.blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    return blueprint


@app.post("/api/projects/{project_id}/blueprint/approve")
async def approve_blueprint(project_id: str):
    """Approve the project blueprint"""
    project = persistence.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.blueprint_id:
        raise HTTPException(status_code=404, detail="Blueprint not generated yet")

    blueprint = persistence.get_blueprint(project_id, project.blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    blueprint.approved = True
    persistence.save_blueprint(blueprint)

    project.status = "blueprint_approved"
    persistence.save_project(project)

    return {"status": "approved"}


# ==================== GENERATION ENDPOINTS (SSE) ====================

@app.get("/api/projects/{project_id}/generate/blueprint")
async def generate_blueprint_stream(project_id: str):
    """Generate blueprint with SSE streaming"""
    project = persistence.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    async def event_generator():
        try:
            blueprint = None
            async for item in architect_agent.generate_blueprint(project):
                if isinstance(item, PipelineEvent):
                    # Send SSE event
                    event_data = item.model_dump_json()
                    yield f"data: {event_data}\n\n"
                elif isinstance(item, Blueprint):
                    blueprint = item

            # Save blueprint
            if blueprint:
                persistence.save_blueprint(blueprint)
                project.blueprint_id = blueprint.id
                project.status = "blueprint_generated"
                persistence.save_project(project)

                # Send final event with blueprint ID
                final_event = PipelineEvent(
                    event_type=EventType.BLUEPRINT_COMPLETE,
                    message="Blueprint saved",
                    data={"blueprint_id": blueprint.id},
                )
                yield f"data: {final_event.model_dump_json()}\n\n"

        except Exception as e:
            # Reset project status on failure
            project.status = "created"
            persistence.save_project(project)

            error_event = PipelineEvent(
                event_type=EventType.ERROR,
                message=f"Generation failed: {str(e)}",
                data={"error": str(e)},
            )
            yield f"data: {error_event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/projects/{project_id}/generate/content")
async def generate_content_stream(project_id: str):
    """Generate website content with SSE streaming"""
    project = persistence.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.blueprint_id:
        raise HTTPException(status_code=400, detail="Blueprint not generated")

    blueprint = persistence.get_blueprint(project_id, project.blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    if not blueprint.approved:
        raise HTTPException(status_code=400, detail="Blueprint not approved")

    async def event_generator():
        try:
            # Prepare output directory for images if generation is enabled
            # Use a pre-generated schema ID to keep images and schema together
            schema_id = str(uuid.uuid4())
            output_dir = None
            if project.config.generate_images:
                output_dir = persistence.ensure_website_dir(project_id, schema_id)

            schema = None
            async for item in constructor_agent.generate_website_schema(
                project, blueprint, illustrator_agent, output_dir
            ):
                if isinstance(item, PipelineEvent):
                    # Send SSE event
                    event_data = item.model_dump_json()
                    yield f"data: {event_data}\n\n"
                elif isinstance(item, WebsiteSchema):
                    schema = item
                    # Set the schema ID to match the directory where images were saved
                    schema.id = schema_id

            # Save schema
            if schema:
                persistence.save_schema(schema)
                project.schema_version = schema.id
                project.status = "schema_generated"
                persistence.save_project(project)

                # Send completion event
                final_event = PipelineEvent(
                    event_type=EventType.CHAPTER_SCHEMA_COMPLETE,
                    message="Schema generation complete",
                    data={"schema_id": schema.id},
                    progress=100.0,
                )
                yield f"data: {final_event.model_dump_json()}\n\n"

        except Exception as e:
            # Reset project status on failure
            project.status = "blueprint_approved"
            persistence.save_project(project)

            error_event = PipelineEvent(
                event_type=EventType.ERROR,
                message=f"Content generation failed: {str(e)}",
                data={"error": str(e)},
            )
            yield f"data: {error_event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/projects/{project_id}/generate/website")
async def generate_website_stream(project_id: str):
    """Render static website with SSE streaming"""
    project = persistence.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.schema_version:
        raise HTTPException(status_code=400, detail="Schema not generated")

    schema = persistence.get_schema(project_id, project.schema_version)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")

    blueprint = persistence.get_blueprint(project_id, project.blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    async def event_generator():
        try:
            # Determine output directory
            output_dir = persistence.ensure_website_dir(project_id, schema.id)

            async for event in renderer_agent.render_website(
                project, blueprint, schema, output_dir
            ):
                # Send SSE event
                event_data = event.model_dump_json()
                yield f"data: {event_data}\n\n"

            # Update project
            project.website_path = str(output_dir)
            project.status = "completed"
            persistence.save_project(project)

        except Exception as e:
            # Reset project status on failure
            project.status = "schema_generated"
            persistence.save_project(project)

            error_event = PipelineEvent(
                event_type=EventType.ERROR,
                message=f"Website rendering failed: {str(e)}",
                data={"error": str(e)},
            )
            yield f"data: {error_event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# ==================== PREVIEW & DOWNLOAD ENDPOINTS ====================

@app.get("/api/projects/{project_id}/preview/{filename:path}")
async def preview_file(project_id: str, filename: str):
    """Serve a file from the generated website for preview"""
    project = persistence.get_project(project_id)
    if not project or not project.website_path:
        raise HTTPException(status_code=404, detail="Website not generated")

    file_path = Path(project.website_path) / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)


@app.get("/api/projects/{project_id}/download")
async def download_website(project_id: str):
    """Download the generated website as a zip archive"""
    import shutil
    import tempfile

    project = persistence.get_project(project_id)
    if not project or not project.website_path:
        raise HTTPException(status_code=404, detail="Website not generated")

    website_dir = Path(project.website_path)
    if not website_dir.exists():
        raise HTTPException(status_code=404, detail="Website files not found")

    # Create temporary zip file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
        zip_path = tmp_file.name

    # Create zip archive
    shutil.make_archive(zip_path.replace(".zip", ""), "zip", website_dir)

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{project.topic.replace(' ', '_')}_website.zip",
    )


# ==================== MODEL INFO ====================

@app.get("/api/models")
async def get_available_models():
    """Get list of available LLM models"""
    from .services.openrouter import ModelConfig
    return {"models": ModelConfig.get_available_models()}


# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "bundlewww"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
