"""Scene detection module using PySceneDetect"""

import logging
from pathlib import Path
from typing import List

from scenedetect import SceneManager, open_video
from scenedetect.detectors import ContentDetector

from ..models import Scene

logger = logging.getLogger(__name__)


class SceneDetector:
    """Handles scene detection in videos"""

    def __init__(self, threshold: float = 27.0, min_scene_len: int = 15):
        """
        Initialize scene detector

        Args:
            threshold: Content detection threshold (lower = more sensitive)
            min_scene_len: Minimum scene length in frames
        """
        self.threshold = threshold
        self.min_scene_len = min_scene_len

    def detect_scenes(self, video_path: Path) -> List[Scene]:
        """
        Detect scenes in a video

        Args:
            video_path: Path to video file

        Returns:
            List of detected scenes
        """
        logger.info(f"Detecting scenes in: {video_path}")

        # Open video and create scene manager
        video = open_video(str(video_path))
        scene_manager = SceneManager()
        scene_manager.add_detector(
            ContentDetector(threshold=self.threshold, min_scene_len=self.min_scene_len)
        )

        # Detect scenes
        scene_manager.detect_scenes(video)
        scene_list = scene_manager.get_scene_list()

        # Convert to Scene objects
        scenes = []
        fps = video.frame_rate

        for i, (start_time, end_time) in enumerate(scene_list):
            scene = Scene(
                start_time=start_time.get_seconds(),
                end_time=end_time.get_seconds(),
                duration=(end_time - start_time).get_seconds(),
                frame_start=start_time.get_frames(),
                frame_end=end_time.get_frames(),
            )
            scenes.append(scene)

        logger.info(f"Detected {len(scenes)} scenes")
        return scenes

    def filter_scenes(
        self, scenes: List[Scene], min_duration: float = 3.0, max_duration: float = 60.0
    ) -> List[Scene]:
        """
        Filter scenes by duration

        Args:
            scenes: List of scenes to filter
            min_duration: Minimum scene duration in seconds
            max_duration: Maximum scene duration in seconds

        Returns:
            Filtered list of scenes
        """
        filtered = [
            scene
            for scene in scenes
            if min_duration <= scene.duration <= max_duration
        ]

        logger.info(f"Filtered {len(scenes)} scenes to {len(filtered)} scenes")
        return filtered
