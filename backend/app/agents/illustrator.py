"""
Agent D: Illustrator
Generates images for chapters using AI image generation
"""
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any
from ..models import Chapter, Project
from ..services.fal import FALService
from ..services.openrouter import OpenRouterService, ModelConfig


class IllustratorAgent:
    """Agent responsible for generating chapter images"""

    def __init__(self, openrouter: OpenRouterService, fal_service: FALService):
        self.openrouter = openrouter
        self.fal_service = fal_service

    async def generate_image_prompt(
        self,
        project: Project,
        chapter: Chapter,
    ) -> str:
        """
        Generate an image generation prompt based on chapter content

        Args:
            project: The project context
            chapter: The chapter to generate an image for

        Returns:
            A detailed image generation prompt
        """
        system_prompt = """You are an expert at creating visual image prompts for educational content.

Your task is to create a single, detailed image generation prompt that visually represents the core concept of a chapter.

Guidelines:
- Focus on the main theme and concept of the chapter
- Create a visually compelling scene that captures the essence
- Be specific about composition, style, and elements
- Avoid text or typography in the image description
- Keep it appropriate for educational content
- Aim for clarity and visual impact
- The image should be suitable for a chapter header/hero image

Style Requirements:
- Contemporary flat illustration style with a focus on bold, organic shapes
- Use a vivid, saturated color palette (e.g., electric blue, coral, sunny yellow)
- Composition utilizes the rule of thirds with a clean, uncluttered layout
- Apply a very subtle grain texture to the flat colors to add warmth, avoiding gradients
- Visuals should rely on shape language rather than line work

Return ONLY the image prompt, no additional text."""

        user_prompt = f"""Create an image generation prompt for this chapter:

Title: {chapter.title}
Purpose: {chapter.purpose}
Topic: {project.topic}

Generate a detailed visual prompt (2-3 sentences) that captures the essence of this chapter."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Use fast model for prompt generation
        model = ModelConfig.get_model_for_project("xAI: Grok Code Fast")

        response = await self.openrouter.chat_completion(
            messages=messages,
            model=model,
            temperature=0.7,
            max_tokens=300,
        )

        return response.strip()

    async def generate_landing_page_image_prompt(
        self,
        project: Project,
    ) -> str:
        """
        Generate an image generation prompt for the landing page

        Args:
            project: The project context

        Returns:
            A detailed image generation prompt for the landing page
        """
        system_prompt = """You are an expert at creating visual image prompts for educational content.

Your task is to create a single, detailed image generation prompt that visually represents the overall theme and essence of an entire topic.

Guidelines:
- Focus on the overarching theme and concept of the entire topic
- Create a visually compelling hero scene that captures the essence
- Be specific about composition, style, and elements
- Avoid text or typography in the image description
- Keep it appropriate for educational content
- Aim for clarity and visual impact
- The image should be suitable as a main landing page hero image

Style Requirements:
- Contemporary flat illustration style with a focus on bold, organic shapes
- Use a vivid, saturated color palette (e.g., electric blue, coral, sunny yellow)
- Composition utilizes the rule of thirds with a clean, uncluttered layout
- Apply a very subtle grain texture to the flat colors to add warmth, avoiding gradients
- Visuals should rely on shape language rather than line work

Return ONLY the image prompt, no additional text."""

        user_prompt = f"""Create an image generation prompt for the landing page of a website about:

Topic: {project.topic}
Depth: {project.config.depth}
Tone: {project.config.tone}

Generate a detailed visual prompt (2-3 sentences) that captures the overall essence of this topic as a hero image."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Use fast model for prompt generation
        model = ModelConfig.get_model_for_project("xAI: Grok Code Fast")

        response = await self.openrouter.chat_completion(
            messages=messages,
            model=model,
            temperature=0.7,
            max_tokens=300,
        )

        return response.strip()

    async def generate_chapter_image(
        self,
        project: Project,
        chapter: Chapter,
        output_dir: Path,
        chapter_number: int,
    ) -> Optional[str]:
        """
        Generate an image for a chapter

        Args:
            project: The project context
            chapter: The chapter to generate an image for
            output_dir: Directory to save the image
            chapter_number: Chapter number for filename

        Returns:
            Relative path to the saved image, or None if generation failed/disabled
        """
        if not self.fal_service.enabled:
            return None

        try:
            # Generate the image prompt
            image_prompt = await self.generate_image_prompt(project, chapter)
            print(f"Generated image prompt for chapter {chapter_number}: {image_prompt}")

            # Generate the image
            print(f"Requesting image from FAL API for chapter {chapter_number}...")
            result = await self.fal_service.generate_image(
                prompt=image_prompt,
                aspect_ratio="16:9",
                resolution="1K",
            )

            if not result or not result.get("images"):
                print(f"No image result from FAL API for chapter {chapter_number}")
                return None

            # Download and save the image
            image_data = result["images"][0]
            image_url = image_data["url"]
            print(f"Downloading image for chapter {chapter_number} from {image_url[:50]}...")

            file_extension = image_data.get("content_type", "image/png").split("/")[1]
            filename = f"chapter_{chapter_number}_hero.{file_extension}"
            image_path = output_dir / filename

            # Download the image with timeout
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    image_url,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(image_path, "wb") as f:
                            f.write(content)
                        print(f"Successfully saved image for chapter {chapter_number}")
                        return filename
                    else:
                        print(f"Failed to download image: HTTP {response.status}")
                        return None

        except asyncio.TimeoutError:
            print(f"Timeout while generating/downloading image for chapter {chapter_number}")
            return None
        except Exception as e:
            print(f"Image generation failed for chapter {chapter_number}: {str(e)}")
            return None

    async def generate_landing_page_image(
        self,
        project: Project,
        output_dir: Path,
    ) -> Optional[str]:
        """
        Generate a hero image for the landing page

        Args:
            project: The project context
            output_dir: Directory to save the image

        Returns:
            Relative path to the saved image, or None if generation failed/disabled
        """
        if not self.fal_service.enabled:
            return None

        try:
            # Generate the image prompt
            image_prompt = await self.generate_landing_page_image_prompt(project)
            print(f"Generated image prompt for landing page: {image_prompt}")

            # Generate the image
            print(f"Requesting landing page image from FAL API...")
            result = await self.fal_service.generate_image(
                prompt=image_prompt,
                aspect_ratio="16:9",
                resolution="1K",
            )

            if not result or not result.get("images"):
                print(f"No image result from FAL API for landing page")
                return None

            # Download and save the image
            image_data = result["images"][0]
            image_url = image_data["url"]
            print(f"Downloading landing page image from {image_url[:50]}...")

            file_extension = image_data.get("content_type", "image/png").split("/")[1]
            filename = f"landing_hero.{file_extension}"
            image_path = output_dir / filename

            # Download the image with timeout
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    image_url,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(image_path, "wb") as f:
                            f.write(content)
                        print(f"Successfully saved landing page image")
                        return filename
                    else:
                        print(f"Failed to download landing page image: HTTP {response.status}")
                        return None

        except asyncio.TimeoutError:
            print(f"Timeout while generating/downloading landing page image")
            return None
        except Exception as e:
            print(f"Landing page image generation failed: {str(e)}")
            return None
