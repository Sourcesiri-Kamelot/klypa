"""Configuration management for Klypa"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class AzureConfig(BaseModel):
    """Azure storage configuration"""

    connection_string: str = Field(
        default_factory=lambda: os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    )
    container_name: str = Field(
        default_factory=lambda: os.getenv("AZURE_STORAGE_CONTAINER_NAME", "klypa-videos")
    )


class OllamaConfig(BaseModel):
    """Ollama AI configuration"""

    host: str = Field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama2"))


class VideoConfig(BaseModel):
    """Video processing configuration"""

    max_duration: int = Field(default_factory=lambda: int(os.getenv("MAX_VIDEO_DURATION", "3600")))
    min_scene_duration: int = Field(
        default_factory=lambda: int(os.getenv("MIN_SCENE_DURATION", "3"))
    )
    max_scene_duration: int = Field(
        default_factory=lambda: int(os.getenv("MAX_SCENE_DURATION", "60"))
    )
    output_resolution: tuple[int, int] = (1080, 1920)  # Vertical format for Shorts
    output_fps: int = Field(default_factory=lambda: int(os.getenv("OUTPUT_FPS", "30")))


class TTSConfig(BaseModel):
    """Text-to-Speech configuration"""

    engine: str = Field(default_factory=lambda: os.getenv("TTS_ENGINE", "coqui"))
    voice: str = Field(default_factory=lambda: os.getenv("TTS_VOICE", "default"))


class PathConfig(BaseModel):
    """Path configuration"""

    upload_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("UPLOAD_DIR", "./uploads"))
    )
    output_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "./output"))
    )
    temp_dir: Path = Field(default_factory=lambda: Path(os.getenv("TEMP_DIR", "./temp")))

    def create_directories(self):
        """Create all required directories"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)


class MonetizationConfig(BaseModel):
    """Monetization and analytics configuration"""

    enable_analytics: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    )
    watermark_enabled: bool = Field(
        default_factory=lambda: os.getenv("WATERMARK_ENABLED", "false").lower() == "true"
    )


class Config(BaseModel):
    """Main application configuration"""

    azure: AzureConfig = Field(default_factory=AzureConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    video: VideoConfig = Field(default_factory=VideoConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    paths: PathConfig = Field(default_factory=PathConfig)
    monetization: MonetizationConfig = Field(default_factory=MonetizationConfig)

    def __init__(self, **data):
        super().__init__(**data)
        self.paths.create_directories()


# Global configuration instance
config = Config()
