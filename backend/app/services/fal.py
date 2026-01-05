"""
FAL API Service
Handles image generation via FAL.ai Nano Banana Pro
"""
import os
import aiohttp
from typing import Optional, Dict, Any


class FALService:
    """Service for interacting with FAL.ai API"""

    def __init__(self):
        self.api_key = os.getenv("FAL_KEY")
        self.base_url = "https://fal.run/fal-ai/nano-banana-pro"
        self.enabled = bool(self.api_key)

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        resolution: str = "1K",
        output_format: str = "png",
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an image using FAL API

        Args:
            prompt: Text prompt for image generation
            aspect_ratio: Image aspect ratio (default: 16:9)
            resolution: Image resolution (default: 1K)
            output_format: Output format (default: png)

        Returns:
            Dict with 'images' list and 'description', or None if API key not configured
        """
        if not self.enabled:
            return None

        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": prompt,
            "num_images": 1,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
            "resolution": resolution,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        print(f"FAL API error {response.status}: {error_text}")
                        return None

        except Exception as e:
            print(f"FAL API request failed: {str(e)}")
            return None
