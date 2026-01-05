"""
Agent B: Constructor
Generates structured content including prose sections
"""
import uuid
import json
import asyncio
from typing import AsyncGenerator, List, Optional
from pathlib import Path

from ..models import Blueprint, Chapter, Section, Project
from ..models.schema import (
    WebsiteSchema, ChapterSchema, SectionSchema, ContentBlock,
    ProseSection, Timeline, TimelineEvent, Table, Callout, KeyStat, CodeBlock
)
from ..models.events import PipelineEvent, EventType
from ..services.openrouter import OpenRouterService, ModelConfig


class ConstructorAgent:
    """Agent responsible for generating structured content and prose"""

    def __init__(self, openrouter: OpenRouterService):
        self.openrouter = openrouter

    def _build_chapter_prompt(
        self,
        project: Project,
        blueprint: Blueprint,
        chapter: Chapter,
    ) -> str:
        """Build prompt for generating a chapter's content schema"""
        return f"""You are the Constructor agent for the Knowledge Architect system.

Your responsibility is to generate ALL content for a chapter in structured JSON format.

PROJECT CONTEXT:
Topic: {project.topic}
Depth: {project.config.depth.value}
Tone: {project.config.tone.value}
Audience: {project.config.audience_level}

CHAPTER TO GENERATE:
Title: {chapter.title}
Purpose: {chapter.purpose}

SECTIONS TO COVER:
{self._format_sections(chapter.sections)}

CONTENT REQUIREMENTS:
1. You MUST generate encyclopedic prose - explanatory paragraphs that educate the reader
2. Prose should be neutral, informative, and reference-style (like Wikipedia or an encyclopedia)
3. Mix prose with other structured content types (timelines, tables, callouts)
4. Each section should have 2-5 content blocks
5. Prose blocks should have 2-5 paragraphs each
6. Historical context and explanatory narrative are expected and required

AVAILABLE CONTENT BLOCK TYPES:
- prose: {{"type": "prose", "heading": "...", "paragraphs": ["...", "..."]}}
- timeline: {{"type": "timeline", "heading": "...", "events": [{{"date": "...", "title": "...", "description": "..."}}]}}
- table: {{"type": "table", "heading": "...", "columns": ["..."], "rows": [["..."]]}}
- callout: {{"type": "callout", "title": "...", "content": "...", "style": "info"}}
- key_stat: {{"type": "key_stat", "value": "...", "label": "...", "context": "..."}}

OUTPUT FORMAT:
{{
  "introduction": ["paragraph 1", "paragraph 2", "paragraph 3"],
  "sections": [
    {{
      "section_id": "{chapter.sections[0].id if chapter.sections else 'section_0'}",
      "blocks": [
        {{"type": "prose", "heading": "Section Heading", "paragraphs": ["...", "..."]}},
        {{"type": "timeline", "heading": "Key Events", "events": [...]}}
      ]
    }}
  ]
}}

CRITICAL RULES:
- Introduction must be 2-4 paragraphs of encyclopedic prose
- Each section MUST include at least one prose block
- Prose should explain, contextualize, and educate
- Use other block types to break up text and present structured info
- Maintain factual accuracy and neutral tone
- Never fabricate specific data - use approximations or ranges if uncertain

Generate the complete chapter content now. Return ONLY the JSON."""

    def _format_sections(self, sections: List[Section]) -> str:
        """Format sections for prompt"""
        lines = []
        for section in sections:
            lines.append(f"- {section.title}: {section.purpose}")
            lines.append(f"  Expected content: {', '.join(section.expected_content_types)}")
        return "\n".join(lines)

    def _is_valid_block(self, block: ContentBlock) -> bool:
        """Validate that a content block has actual content"""
        if isinstance(block, ProseSection):
            # Prose must have at least one non-empty paragraph
            return len(block.paragraphs) > 0 and any(p.strip() for p in block.paragraphs)
        elif isinstance(block, Timeline):
            # Timeline must have at least one event
            return len(block.events) > 0
        elif isinstance(block, Table):
            # Table must have rows
            return len(block.rows) > 0
        elif isinstance(block, Callout):
            # Callout must have content
            return bool(block.content.strip())
        elif isinstance(block, KeyStat):
            # KeyStat must have value and label
            return bool(block.value.strip()) and bool(block.label.strip())
        elif isinstance(block, CodeBlock):
            # CodeBlock must have code
            return bool(block.code.strip())
        return True

    def _parse_content_block(self, block_data: dict) -> ContentBlock:
        """Parse a content block from JSON data"""
        block_type = block_data.get("type")

        if block_type == "prose":
            return ProseSection(**block_data)
        elif block_type == "timeline":
            return Timeline(**block_data)
        elif block_type == "table":
            return Table(**block_data)
        elif block_type == "callout":
            return Callout(**block_data)
        elif block_type == "key_stat":
            return KeyStat(**block_data)
        elif block_type == "code":
            return CodeBlock(**block_data)
        else:
            # Default to prose if type unknown
            return ProseSection(
                heading=block_data.get("heading", ""),
                paragraphs=block_data.get("paragraphs", []),
            )

    async def generate_chapter_schema(
        self,
        project: Project,
        blueprint: Blueprint,
        chapter: Chapter,
        chapter_index: int,
        total_chapters: int,
    ) -> AsyncGenerator[PipelineEvent | ChapterSchema, None]:
        """Generate content schema for a single chapter"""

        # Emit start event (only message, no progress percentage yet)
        yield PipelineEvent(
            event_type=EventType.CHAPTER_SCHEMA_START,
            message=f"Generating chapter {chapter_index + 1}/{total_chapters}: {chapter.title}",
            data={"chapter_id": chapter.id, "chapter_title": chapter.title},
        )

        # Build prompt
        prompt = self._build_chapter_prompt(project, blueprint, chapter)

        # Get the selected model
        model = ModelConfig.get_model_for_project(project.config.model)

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Generate the complete content for chapter: {chapter.title}"},
        ]

        try:
            # Get completion
            response = await self.openrouter.chat_completion(
                messages=messages,
                model=model,
                temperature=0.7,
                max_tokens=8000,
            )

            # Parse JSON response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No valid JSON found in response")

            json_str = response[json_start:json_end]
            chapter_data = json.loads(json_str)

            # Build ChapterSchema object
            sections = []
            for section_data in chapter_data.get("sections", []):
                blocks = []
                for block_data in section_data.get("blocks", []):
                    block = self._parse_content_block(block_data)
                    # Only include blocks that have actual content
                    if self._is_valid_block(block):
                        blocks.append(block)

                # Only include sections that have at least one valid block
                if blocks:
                    section_schema = SectionSchema(
                        section_id=section_data.get("section_id", ""),
                        blocks=blocks,
                    )
                    sections.append(section_schema)

            chapter_schema = ChapterSchema(
                chapter_id=chapter.id,
                introduction=chapter_data.get("introduction", []),
                sections=sections,
                image_path=None,  # Will be set later if images are generated
            )

            # Emit completion event with accurate progress
            progress = ((chapter_index + 1) / total_chapters) * 100
            yield PipelineEvent(
                event_type=EventType.CHAPTER_SCHEMA_COMPLETE,
                message=f"Completed chapter {chapter_index + 1}/{total_chapters}: {chapter.title}",
                progress=round(progress, 1),
                data={"chapter_id": chapter.id, "chapter_number": chapter_index + 1, "total_chapters": total_chapters},
            )

            # Yield the chapter schema
            yield chapter_schema

        except Exception as e:
            yield PipelineEvent(
                event_type=EventType.ERROR,
                message=f"Chapter generation failed: {str(e)}",
                data={"error": str(e), "chapter_id": chapter.id},
            )
            raise

    async def generate_website_schema(
        self,
        project: Project,
        blueprint: Blueprint,
        illustrator_agent=None,
        output_dir: Optional[Path] = None,
    ) -> AsyncGenerator[PipelineEvent | WebsiteSchema, None]:
        """
        Generate complete website schema

        Args:
            project: Project configuration
            blueprint: Approved blueprint
            illustrator_agent: Optional illustrator for image generation
            output_dir: Optional output directory for images
        """

        chapter_schemas = []
        total_chapters = len(blueprint.chapters)

        # Generate each chapter sequentially
        for idx, chapter in enumerate(blueprint.chapters):
            # Generate chapter content
            chapter_schema = None
            async for item in self.generate_chapter_schema(
                project, blueprint, chapter, idx, total_chapters
            ):
                if isinstance(item, ChapterSchema):
                    chapter_schema = item
                else:
                    # Forward events
                    yield item

            if chapter_schema:
                # Generate image in parallel if enabled
                if (
                    project.config.generate_images
                    and illustrator_agent
                    and output_dir
                ):
                    try:
                        yield PipelineEvent(
                            event_type=EventType.PROGRESS,
                            message=f"Generating image for chapter {idx + 1}",
                        )
                        image_path = await illustrator_agent.generate_chapter_image(
                            project, chapter, output_dir, idx + 1
                        )
                        if image_path:
                            chapter_schema.image_path = image_path
                            yield PipelineEvent(
                                event_type=EventType.PROGRESS,
                                message=f"Image generated for chapter {idx + 1}",
                            )
                    except Exception as e:
                        print(f"Image generation failed for chapter {idx + 1}: {str(e)}")
                        # Continue without image

                chapter_schemas.append(chapter_schema)

        # Generate landing page image if enabled
        landing_page_image_path = None
        if (
            project.config.generate_images
            and illustrator_agent
            and output_dir
        ):
            try:
                yield PipelineEvent(
                    event_type=EventType.PROGRESS,
                    message="Generating landing page hero image",
                )
                landing_page_image_path = await illustrator_agent.generate_landing_page_image(
                    project, output_dir
                )
                if landing_page_image_path:
                    yield PipelineEvent(
                        event_type=EventType.PROGRESS,
                        message="Landing page image generated",
                    )
            except Exception as e:
                print(f"Landing page image generation failed: {str(e)}")
                # Continue without image

        # Create final schema
        schema = WebsiteSchema(
            id=str(uuid.uuid4()),
            project_id=project.id,
            blueprint_id=blueprint.id,
            chapters=chapter_schemas,
            landing_page_image_path=landing_page_image_path,
        )

        yield schema
