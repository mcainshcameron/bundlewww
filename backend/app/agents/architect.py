"""
Agent A: Architect
Generates site structure and blueprint (no content)
"""
import uuid
import json
from typing import AsyncGenerator

from ..models import Blueprint, Chapter, Section, Project, ProjectConfig
from ..models.events import PipelineEvent, EventType
from ..services.openrouter import OpenRouterService, ModelConfig


class ArchitectAgent:
    """Agent responsible for generating site structure and blueprint"""

    def __init__(self, openrouter: OpenRouterService):
        self.openrouter = openrouter

    def _build_architect_prompt(self, topic: str, config: ProjectConfig) -> str:
        """Build the system prompt for blueprint generation"""
        return f"""You are the Architect agent for the Knowledge Architect system.

Your ONLY responsibility is to create a structural blueprint for a website about the given topic.

Topic: {topic}
Depth Level: {config.depth.value}
Tone: {config.tone.value}
Audience: {config.audience_level}

CONSTRAINTS:
- You must ONLY produce structure: chapters, sections, and metadata
- NO prose, NO facts, NO actual content
- Each chapter must have 3-6 sections
- Each section must have a clear purpose statement
- The structure should support an encyclopedia-style reference site

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
  "chapters": [
    {{
      "title": "Chapter Title",
      "purpose": "What this chapter covers and why",
      "sections": [
        {{
          "title": "Section Title",
          "purpose": "What this section covers",
          "expected_content_types": ["prose", "timeline", "table"]
        }}
      ]
    }}
  ]
}}

GUIDELINES:
- For "overview" depth: 3-5 chapters
- For "deep_dive" depth: 5-8 chapters
- For "comprehensive" depth: 8-12 chapters
- Ensure logical flow and progression
- Balance theoretical and practical sections
- Include historical/background sections where relevant

Generate the blueprint now. Return ONLY the JSON, no other text."""

    async def generate_blueprint(
        self,
        project: Project,
    ) -> AsyncGenerator[PipelineEvent | Blueprint, None]:
        """Generate blueprint for the project"""

        # Emit start event
        yield PipelineEvent(
            event_type=EventType.BLUEPRINT_START,
            message=f"Starting blueprint generation for: {project.topic}",
            progress=0.0,
        )

        # Build prompt
        prompt = self._build_architect_prompt(project.topic, project.config)

        # Get the selected model
        model = ModelConfig.get_model_for_project(project.config.model)

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Generate the structural blueprint for: {project.topic}"},
        ]

        try:
            # Get completion from OpenRouter
            response = await self.openrouter.chat_completion(
                messages=messages,
                model=model,
                temperature=0.7,
                max_tokens=4000,
            )

            # Parse JSON response
            # Extract JSON from response (handle cases where model adds extra text)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No valid JSON found in response")

            json_str = response[json_start:json_end]
            blueprint_data = json.loads(json_str)

            # Build Blueprint object
            chapters = []
            for idx, chapter_data in enumerate(blueprint_data["chapters"]):
                sections = []
                for sec_idx, section_data in enumerate(chapter_data["sections"]):
                    section = Section(
                        id=f"section_{idx}_{sec_idx}",
                        title=section_data["title"],
                        purpose=section_data["purpose"],
                        expected_content_types=section_data.get("expected_content_types", ["prose"]),
                    )
                    sections.append(section)

                chapter = Chapter(
                    id=f"chapter_{idx}",
                    title=chapter_data["title"],
                    purpose=chapter_data["purpose"],
                    sections=sections,
                )
                chapters.append(chapter)

            blueprint = Blueprint(
                id=str(uuid.uuid4()),
                project_id=project.id,
                chapters=chapters,
                approved=False,
            )

            # Emit completion event
            yield PipelineEvent(
                event_type=EventType.BLUEPRINT_COMPLETE,
                message=f"Blueprint generated with {len(chapters)} chapters",
                progress=100.0,
                data={"chapter_count": len(chapters)},
            )

            # Yield the blueprint
            yield blueprint

        except Exception as e:
            yield PipelineEvent(
                event_type=EventType.ERROR,
                message=f"Blueprint generation failed: {str(e)}",
                data={"error": str(e)},
            )
            raise
