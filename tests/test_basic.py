"""
Basic tests for Klypa core functionality
"""

import pytest
from pathlib import Path
from klypa.models import Scene, TranscriptionSegment, VideoMetadata, ShortVideo, ProcessingStatus


class TestModels:
    """Test data models"""

    def test_scene_creation(self):
        scene = Scene(
            start_time=0.0,
            end_time=10.0,
            duration=10.0,
            frame_start=0,
            frame_end=300,
        )
        assert scene.duration == 10.0
        assert scene.timestamp == "0.00s - 10.00s"

    def test_transcription_segment(self):
        segment = TranscriptionSegment(
            text="Hello world",
            start=0.0,
            end=2.0,
            confidence=0.95,
        )
        assert segment.text == "Hello world"
        assert segment.confidence == 0.95

    def test_short_video(self):
        short = ShortVideo(
            id="test_001",
            source_video=Path("test.mp4"),
            status=ProcessingStatus.PENDING,
        )
        assert short.id == "test_001"
        assert short.status == ProcessingStatus.PENDING
        assert short.viral_score == 0.0


class TestConfiguration:
    """Test configuration management"""

    def test_config_import(self):
        from klypa.config import config

        assert config.video.output_resolution == (1080, 1920)
        assert config.video.output_fps > 0

    def test_path_config(self):
        from klypa.config import config

        assert config.paths.upload_dir is not None
        assert config.paths.output_dir is not None


class TestIntegrations:
    """Test integration modules"""

    def test_ollama_client_import(self):
        from klypa.integrations import OllamaClient

        client = OllamaClient()
        assert client.host is not None
        assert client.model is not None

    def test_tts_engine_import(self):
        from klypa.integrations import TTSEngine

        engine = TTSEngine()
        assert engine.engine in ["coqui", "bark"]

    def test_semantic_matcher_import(self):
        from klypa.integrations import SemanticMatcher

        # Don't initialize to avoid downloading models in tests
        assert SemanticMatcher is not None


class TestUtils:
    """Test utility modules"""

    def test_analytics_tracker(self):
        from klypa.utils import AnalyticsTracker

        tracker = AnalyticsTracker(Path("/tmp/test_analytics.json"))
        summary = tracker.get_summary()
        assert isinstance(summary, dict)

    def test_batch_processor_import(self):
        from klypa.utils import BatchProcessor

        processor = BatchProcessor()
        assert processor.max_workers > 0

    def test_monetization_hooks(self):
        from klypa.utils import MonetizationHooks

        hooks = MonetizationHooks()
        assert hooks is not None


class TestCoreModules:
    """Test core modules can be imported"""

    def test_video_processor_import(self):
        from klypa.core import VideoProcessor

        # Don't initialize to avoid loading models
        assert VideoProcessor is not None

    def test_scene_detector_import(self):
        from klypa.core import SceneDetector

        detector = SceneDetector()
        assert detector.threshold > 0

    def test_transcriber_import(self):
        from klypa.core import Transcriber

        # Don't initialize to avoid loading Whisper model
        assert Transcriber is not None

    def test_caption_generator_import(self):
        from klypa.core import CaptionGenerator

        generator = CaptionGenerator()
        assert generator.font is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
