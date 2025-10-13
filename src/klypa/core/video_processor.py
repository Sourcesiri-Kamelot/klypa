"""Main video processor orchestrating all components"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from moviepy.editor import VideoFileClip

from ..config import config
from ..models import (
    VideoMetadata,
    ShortVideo,
    Scene,
    BatchExportJob,
    ProcessingStatus,
    VideoFormat,
)
from .scene_detector import SceneDetector
from .transcriber import Transcriber
from .caption_generator import CaptionGenerator

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Main video processing orchestrator"""

    def __init__(
        self,
        transcriber: Optional[Transcriber] = None,
        scene_detector: Optional[SceneDetector] = None,
        caption_generator: Optional[CaptionGenerator] = None,
    ):
        """
        Initialize video processor

        Args:
            transcriber: Transcriber instance
            scene_detector: SceneDetector instance
            caption_generator: CaptionGenerator instance
        """
        self.transcriber = transcriber or Transcriber()
        self.scene_detector = scene_detector or SceneDetector()
        self.caption_generator = caption_generator or CaptionGenerator()

    def extract_metadata(self, video_path: Path) -> VideoMetadata:
        """
        Extract metadata from video file

        Args:
            video_path: Path to video file

        Returns:
            VideoMetadata object
        """
        logger.info(f"Extracting metadata from: {video_path}")

        video = VideoFileClip(str(video_path))
        metadata = VideoMetadata(
            path=video_path,
            duration=video.duration,
            width=video.w,
            height=video.h,
            fps=video.fps,
            format=VideoFormat(video_path.suffix[1:].lower()),
            size_bytes=video_path.stat().st_size,
        )
        video.close()

        logger.info(f"Metadata extracted: {metadata.duration:.2f}s, {metadata.width}x{metadata.height}")
        return metadata

    def create_vertical_short(
        self, video_path: Path, scene: Scene, output_path: Path
    ) -> Path:
        """
        Create a vertical short from a scene

        Args:
            video_path: Path to source video
            scene: Scene to extract
            output_path: Path for output video

        Returns:
            Path to created short video
        """
        logger.info(f"Creating vertical short: {scene.timestamp}")

        video = VideoFileClip(str(video_path))

        # Extract scene
        clip = video.subclip(scene.start_time, scene.end_time)

        # Resize to vertical format (9:16 aspect ratio)
        target_width, target_height = config.video.output_resolution

        # Calculate scaling
        scale = max(target_width / clip.w, target_height / clip.h)
        clip_resized = clip.resize(scale)

        # Crop to exact dimensions (center crop)
        x_center = clip_resized.w / 2
        y_center = clip_resized.h / 2
        x1 = x_center - target_width / 2
        y1 = y_center - target_height / 2

        final_clip = clip_resized.crop(
            x1=x1, y1=y1, width=target_width, height=target_height
        )

        # Write output
        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=config.video.output_fps,
            preset="medium",
        )

        # Cleanup
        video.close()
        clip.close()
        final_clip.close()

        logger.info(f"Vertical short created: {output_path}")
        return output_path

    def process_video(
        self, video_path: Path, max_shorts: int = 10
    ) -> BatchExportJob:
        """
        Process a video and generate shorts

        Args:
            video_path: Path to input video
            max_shorts: Maximum number of shorts to generate

        Returns:
            BatchExportJob with generated shorts
        """
        logger.info(f"Processing video: {video_path}")

        job = BatchExportJob(
            id=str(uuid.uuid4()),
            input_video=video_path,
            status=ProcessingStatus.PROCESSING,
        )

        try:
            # Extract metadata
            metadata = self.extract_metadata(video_path)

            # Detect scenes
            scenes = self.scene_detector.detect_scenes(video_path)
            filtered_scenes = self.scene_detector.filter_scenes(
                scenes,
                min_duration=config.video.min_scene_duration,
                max_duration=config.video.max_scene_duration,
            )

            # Transcribe video
            transcription = self.transcriber.transcribe(video_path)

            # Generate shorts
            for i, scene in enumerate(filtered_scenes[:max_shorts]):
                short_id = f"{job.id}_{i+1}"
                output_path = config.paths.output_dir / f"short_{short_id}.mp4"

                # Create vertical short
                self.create_vertical_short(video_path, scene, output_path)

                # Get transcription for this scene
                scene_transcription = [
                    seg
                    for seg in transcription
                    if scene.start_time <= seg.start < scene.end_time
                ]

                # Create short video object
                short = ShortVideo(
                    id=short_id,
                    source_video=video_path,
                    output_path=output_path,
                    scene=scene,
                    transcription=scene_transcription,
                    status=ProcessingStatus.COMPLETED,
                    metadata={
                        "duration": scene.duration,
                        "resolution": f"{config.video.output_resolution[0]}x{config.video.output_resolution[1]}",
                    },
                )

                job.shorts.append(short)
                logger.info(f"Short {i+1}/{len(filtered_scenes[:max_shorts])} completed")

            job.status = ProcessingStatus.COMPLETED
            job.completed_at = datetime.now()
            job.analytics = {
                "total_scenes": len(scenes),
                "filtered_scenes": len(filtered_scenes),
                "shorts_created": len(job.shorts),
                "source_duration": metadata.duration,
            }

        except Exception as e:
            logger.error(f"Error processing video: {e}", exc_info=True)
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)

        return job
