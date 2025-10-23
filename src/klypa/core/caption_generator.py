"""Caption generation using MoviePy"""

import logging
from pathlib import Path
from typing import List, Optional

from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip

from ..models import Caption, TranscriptionSegment

logger = logging.getLogger(__name__)


class CaptionGenerator:
    """Generates captions for videos"""

    def __init__(
        self,
        font: str = "Arial",
        font_size: int = 48,
        color: str = "white",
        bg_color: Optional[str] = "black",
        stroke_color: Optional[str] = "black",
        stroke_width: int = 2,
    ):
        """
        Initialize caption generator

        Args:
            font: Font name
            font_size: Font size in pixels
            color: Text color
            bg_color: Background color (None for transparent)
            stroke_color: Stroke color for text outline
            stroke_width: Stroke width in pixels
        """
        self.font = font
        self.font_size = font_size
        self.color = color
        self.bg_color = bg_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width

    def create_captions_from_transcription(
        self, segments: List[TranscriptionSegment], video_width: int, video_height: int
    ) -> List[Caption]:
        """
        Create caption objects from transcription segments

        Args:
            segments: List of transcription segments
            video_width: Video width in pixels
            video_height: Video height in pixels

        Returns:
            List of caption objects
        """
        captions = []
        position = (video_width // 2, int(video_height * 0.8))  # Bottom center

        for segment in segments:
            caption = Caption(
                text=segment.text,
                start_time=segment.start,
                end_time=segment.end,
                position=position,
                font_size=self.font_size,
                color=self.color,
                background_color=self.bg_color,
            )
            captions.append(caption)

        logger.info(f"Created {len(captions)} captions")
        return captions

    def add_captions_to_video(
        self, video_path: Path, captions: List[Caption], output_path: Path
    ) -> Path:
        """
        Add captions to a video

        Args:
            video_path: Path to input video
            captions: List of captions to add
            output_path: Path for output video

        Returns:
            Path to output video with captions
        """
        logger.info(f"Adding captions to video: {video_path}")

        # Load video
        video = VideoFileClip(str(video_path))

        # Create text clips for each caption
        text_clips = []
        for caption in captions:
            txt_clip = (
                TextClip(
                    caption.text,
                    fontsize=caption.font_size,
                    color=caption.color,
                    font=self.font,
                    stroke_color=self.stroke_color,
                    stroke_width=self.stroke_width,
                    method="caption",
                    size=(int(video.w * 0.9), None),
                    align="center",
                )
                .set_position(("center", int(video.h * 0.75)))
                .set_start(caption.start_time)
                .set_duration(caption.end_time - caption.start_time)
            )
            text_clips.append(txt_clip)

        # Composite video with captions
        final_video = CompositeVideoClip([video] + text_clips)

        # Write output
        final_video.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=f"{output_path}.temp.m4a",
            remove_temp=True,
            fps=video.fps,
        )

        # Close clips
        video.close()
        final_video.close()

        logger.info(f"Video with captions saved to: {output_path}")
        return output_path
