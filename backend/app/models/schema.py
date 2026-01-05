from typing import List, Dict, Any, Union, Optional
from enum import Enum
from pydantic import BaseModel, Field


class BlockType(str, Enum):
    PROSE = "prose"
    TIMELINE = "timeline"
    TABLE = "table"
    CALLOUT = "callout"
    KEY_STAT = "key_stat"
    CODE = "code"


class ProseSection(BaseModel):
    type: BlockType = Field(default=BlockType.PROSE)
    heading: str = Field(description="Section heading")
    paragraphs: List[str] = Field(description="Ordered array of paragraph text")


class TimelineEvent(BaseModel):
    date: str = Field(description="Event date or time period")
    title: str = Field(description="Event title")
    description: str = Field(description="Event description")


class Timeline(BaseModel):
    type: BlockType = Field(default=BlockType.TIMELINE)
    heading: str = Field(description="Timeline heading")
    events: List[TimelineEvent] = Field(description="Chronological events")


class Table(BaseModel):
    type: BlockType = Field(default=BlockType.TABLE)
    heading: str = Field(description="Table heading")
    columns: List[str] = Field(description="Column headers")
    rows: List[List[str]] = Field(description="Table data rows")


class Callout(BaseModel):
    type: BlockType = Field(default=BlockType.CALLOUT)
    title: str = Field(description="Callout title")
    content: str = Field(description="Callout content")
    style: str = Field(default="info", description="Callout style (info, warning, tip, etc.)")


class KeyStat(BaseModel):
    type: BlockType = Field(default=BlockType.KEY_STAT)
    value: str = Field(description="Statistical value")
    label: str = Field(description="Stat label")
    context: str = Field(default="", description="Additional context")


class CodeBlock(BaseModel):
    type: BlockType = Field(default=BlockType.CODE)
    heading: str = Field(description="Code block heading")
    language: str = Field(description="Programming language")
    code: str = Field(description="Code content")


ContentBlock = Union[ProseSection, Timeline, Table, Callout, KeyStat, CodeBlock]


class SectionSchema(BaseModel):
    section_id: str = Field(description="Reference to blueprint section ID")
    blocks: List[ContentBlock] = Field(description="Ordered content blocks")


class ChapterSchema(BaseModel):
    chapter_id: str = Field(description="Reference to blueprint chapter ID")
    introduction: List[str] = Field(description="Chapter introduction paragraphs")
    sections: List[SectionSchema] = Field(description="Section schemas")
    image_path: Optional[str] = Field(default=None, description="Relative path to chapter hero image")


class WebsiteSchema(BaseModel):
    id: str = Field(description="Unique schema version identifier")
    project_id: str = Field(description="Associated project ID")
    blueprint_id: str = Field(description="Associated blueprint ID")
    chapters: List[ChapterSchema] = Field(description="Complete chapter schemas")
    landing_page_image_path: Optional[str] = Field(default=None, description="Relative path to landing page hero image")
