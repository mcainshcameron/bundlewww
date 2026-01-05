from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DepthLevel(str, Enum):
    OVERVIEW = "overview"
    DEEP_DIVE = "deep_dive"
    COMPREHENSIVE = "comprehensive"


class ToneStyle(str, Enum):
    INTRODUCTORY = "introductory"
    PROFESSIONAL = "professional"
    ACADEMIC = "academic"
    CASUAL = "casual"


class ProjectConfig(BaseModel):
    depth: DepthLevel = Field(description="Content depth level")
    tone: ToneStyle = Field(description="Writing tone style")
    audience_level: str = Field(default="general", description="Target audience expertise level")
    model: str = Field(default="xAI: Grok Code Fast", description="LLM model to use for generation")
    generate_images: bool = Field(default=False, description="Generate AI images for chapters")


class ProjectCreate(BaseModel):
    topic: str = Field(description="The topic for the website")
    config: ProjectConfig


class Project(BaseModel):
    id: str = Field(description="Unique project identifier")
    topic: str = Field(description="The topic for the website")
    config: ProjectConfig
    created_at: datetime = Field(default_factory=datetime.now)
    blueprint_id: Optional[str] = Field(default=None, description="Approved blueprint ID")
    schema_version: Optional[str] = Field(default=None, description="Current schema version ID")
    website_path: Optional[str] = Field(default=None, description="Path to generated website")
    status: str = Field(default="created", description="Project status")
