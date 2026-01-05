from typing import List
from pydantic import BaseModel, Field


class Section(BaseModel):
    id: str = Field(description="Unique section identifier")
    title: str = Field(description="Section title")
    purpose: str = Field(description="Section purpose and intent")
    expected_content_types: List[str] = Field(
        default_factory=list,
        description="Expected content block types (prose, timeline, table, etc.)"
    )


class Chapter(BaseModel):
    id: str = Field(description="Unique chapter identifier")
    title: str = Field(description="Chapter title")
    purpose: str = Field(description="Chapter purpose and intent")
    sections: List[Section] = Field(default_factory=list, description="Sections within chapter")


class Blueprint(BaseModel):
    id: str = Field(description="Unique blueprint identifier")
    project_id: str = Field(description="Associated project ID")
    chapters: List[Chapter] = Field(default_factory=list, description="Chapter hierarchy")
    approved: bool = Field(default=False, description="User approval status")
