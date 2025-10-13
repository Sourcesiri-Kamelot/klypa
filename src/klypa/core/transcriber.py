"""Transcription module using OpenAI Whisper"""

import logging
from pathlib import Path
from typing import List, Optional

import whisper

from ..models import TranscriptionSegment

logger = logging.getLogger(__name__)


class Transcriber:
    """Handles audio transcription using Whisper"""

    def __init__(self, model_name: str = "base"):
        """
        Initialize transcriber with Whisper model

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        logger.info(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        self.model_name = model_name

    def transcribe(
        self, audio_path: Path, language: Optional[str] = None
    ) -> List[TranscriptionSegment]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio/video file
            language: Optional language code (e.g., 'en', 'es')

        Returns:
            List of transcription segments
        """
        logger.info(f"Transcribing: {audio_path}")

        result = self.model.transcribe(
            str(audio_path), language=language, word_timestamps=True, verbose=False
        )

        segments = []
        for segment in result.get("segments", []):
            segments.append(
                TranscriptionSegment(
                    text=segment["text"].strip(),
                    start=segment["start"],
                    end=segment["end"],
                    confidence=segment.get("confidence", 1.0),
                )
            )

        logger.info(f"Transcription completed: {len(segments)} segments")
        return segments

    def transcribe_segment(
        self, audio_path: Path, start_time: float, end_time: float, language: Optional[str] = None
    ) -> List[TranscriptionSegment]:
        """
        Transcribe a specific segment of audio

        Args:
            audio_path: Path to audio/video file
            start_time: Start time in seconds
            end_time: End time in seconds
            language: Optional language code

        Returns:
            List of transcription segments for the specified time range
        """
        all_segments = self.transcribe(audio_path, language)

        # Filter segments within the time range
        filtered_segments = [
            seg
            for seg in all_segments
            if (seg.start >= start_time and seg.start < end_time)
            or (seg.end > start_time and seg.end <= end_time)
            or (seg.start <= start_time and seg.end >= end_time)
        ]

        return filtered_segments
