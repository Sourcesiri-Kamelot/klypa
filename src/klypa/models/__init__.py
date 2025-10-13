"""Data models for Klypa"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional


class VideoFormat(str, Enum):
    """Supported video formats"""

    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"


class ProcessingStatus(str, Enum):
    """Processing status for videos"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Scene:
    """Represents a detected scene in a video"""

    start_time: float
    end_time: float
    duration: float
    frame_start: int
    frame_end: int
    confidence: float = 1.0
    description: Optional[str] = None

    @property
    def timestamp(self) -> str:
        """Get formatted timestamp"""
        return f"{self.start_time:.2f}s - {self.end_time:.2f}s"


@dataclass
class TranscriptionSegment:
    """Represents a transcribed segment"""

    text: str
    start: float
    end: float
    confidence: float = 1.0


@dataclass
class Caption:
    """Represents a caption for video"""

    text: str
    start_time: float
    end_time: float
    position: tuple[int, int] = (0, 0)
    font_size: int = 48
    color: str = "white"
    background_color: Optional[str] = None


@dataclass
class VideoMetadata:
    """Metadata for input video"""

    path: Path
    duration: float
    width: int
    height: int
    fps: float
    format: VideoFormat
    size_bytes: int
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ShortVideo:
    """Represents a generated short video"""

    id: str
    source_video: Path
    output_path: Optional[Path] = None
    scene: Optional[Scene] = None
    transcription: List[TranscriptionSegment] = field(default_factory=list)
    captions: List[Caption] = field(default_factory=list)
    viral_score: float = 0.0
    viral_idea: Optional[str] = None
    voiceover_path: Optional[Path] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class BatchExportJob:
    """Represents a batch export job"""

    id: str
    input_video: Path
    shorts: List[ShortVideo] = field(default_factory=list)
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    analytics: dict = field(default_factory=dict)


@dataclass
class ViralIdea:
    """Represents a viral content idea from Ollama"""

    title: str
    description: str
    hook: str
    call_to_action: str
    estimated_score: float = 0.0
    tags: List[str] = field(default_factory=list)
