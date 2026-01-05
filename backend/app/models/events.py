from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    BLUEPRINT_START = "blueprint_start"
    BLUEPRINT_COMPLETE = "blueprint_complete"
    CHAPTER_SCHEMA_START = "chapter_schema_start"
    CHAPTER_SCHEMA_COMPLETE = "chapter_schema_complete"
    RENDER_START = "render_start"
    RENDER_COMPLETE = "render_complete"
    EXPORT_READY = "export_ready"
    ERROR = "error"
    PROGRESS = "progress"


class PipelineEvent(BaseModel):
    event_type: EventType = Field(description="Type of pipeline event")
    message: str = Field(description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional event data")
    progress: Optional[float] = Field(default=None, description="Progress percentage (0-100)")
