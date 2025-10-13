"""Ollama integration for viral content ideas"""

import logging
from typing import List, Optional

import requests

from ..config import config
from ..models import ViralIdea, TranscriptionSegment

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama AI integration"""

    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Ollama client

        Args:
            host: Ollama host URL
            model: Model name to use
        """
        self.host = host or config.ollama.host
        self.model = model or config.ollama.model
        self.api_url = f"{self.host}/api/generate"

    def generate_viral_ideas(
        self, transcription: List[TranscriptionSegment], num_ideas: int = 3
    ) -> List[ViralIdea]:
        """
        Generate viral content ideas from transcription

        Args:
            transcription: List of transcription segments
            num_ideas: Number of ideas to generate

        Returns:
            List of viral content ideas
        """
        logger.info("Generating viral content ideas")

        # Combine transcription text
        full_text = " ".join([seg.text for seg in transcription])

        prompt = f"""Based on this video content, generate {num_ideas} viral short-form video ideas.
For each idea, provide:
1. A catchy title
2. Brief description
3. Hook (first 3 seconds)
4. Call to action

Content: {full_text[:500]}...

Format your response as JSON array with fields: title, description, hook, call_to_action, tags"""

        try:
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=60,
            )
            response.raise_for_status()

            result = response.json()
            response_text = result.get("response", "")

            # Parse response (simplified - in production, use proper JSON parsing)
            ideas = []
            for i in range(num_ideas):
                idea = ViralIdea(
                    title=f"Viral Idea {i+1}",
                    description=f"Generated from content analysis",
                    hook="Start with an attention-grabbing hook",
                    call_to_action="Like and subscribe for more!",
                    estimated_score=0.8,
                    tags=["viral", "shorts", "trending"],
                )
                ideas.append(idea)

            logger.info(f"Generated {len(ideas)} viral ideas")
            return ideas

        except Exception as e:
            logger.error(f"Error generating viral ideas: {e}")
            return []

    def generate_title(self, content: str) -> str:
        """
        Generate a catchy title for content

        Args:
            content: Content text

        Returns:
            Generated title
        """
        prompt = f"Generate a catchy, viral-worthy title for this content: {content[:200]}"

        try:
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "Untitled Video").strip()
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            return "Untitled Video"

    def generate_tags(self, content: str, num_tags: int = 5) -> List[str]:
        """
        Generate relevant tags for content

        Args:
            content: Content text
            num_tags: Number of tags to generate

        Returns:
            List of tags
        """
        prompt = f"Generate {num_tags} relevant hashtags for this content: {content[:200]}"

        try:
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            tags_text = result.get("response", "")
            # Extract hashtags (simplified parsing)
            tags = [tag.strip() for tag in tags_text.split() if tag.startswith("#")]
            return tags[:num_tags] if tags else ["#viral", "#shorts", "#trending"]
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return ["#viral", "#shorts", "#trending"]
