"""Klypa - Automated Video Shorts Generation System"""

__version__ = "0.1.0"
__author__ = "Helo-im.Ai"
__license__ = "MIT"

from .core.video_processor import VideoProcessor
from .core.scene_detector import SceneDetector
from .core.transcriber import Transcriber
from .core.caption_generator import CaptionGenerator
from .integrations.ollama_client import OllamaClient
from .integrations.tts_engine import TTSEngine

__all__ = [
    "VideoProcessor",
    "SceneDetector",
    "Transcriber",
    "CaptionGenerator",
    "OllamaClient",
    "TTSEngine",
]
