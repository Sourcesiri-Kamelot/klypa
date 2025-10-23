"""Batch processing utilities"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Callable, Optional
import time

from ..models import BatchExportJob, ShortVideo, ProcessingStatus
from ..core.video_processor import VideoProcessor

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Handle batch processing of videos"""

    def __init__(
        self,
        video_processor: Optional[VideoProcessor] = None,
        max_workers: int = 2,
    ):
        """
        Initialize batch processor

        Args:
            video_processor: VideoProcessor instance
            max_workers: Maximum number of parallel workers
        """
        self.video_processor = video_processor or VideoProcessor()
        self.max_workers = max_workers

    def process_batch(
        self,
        video_paths: List[Path],
        max_shorts_per_video: int = 10,
        callback: Optional[Callable[[BatchExportJob], None]] = None,
    ) -> List[BatchExportJob]:
        """
        Process multiple videos in batch

        Args:
            video_paths: List of video file paths
            max_shorts_per_video: Maximum shorts per video
            callback: Optional callback function for each completed job

        Returns:
            List of completed batch export jobs
        """
        logger.info(f"Starting batch processing of {len(video_paths)} videos")

        jobs = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(
                    self.video_processor.process_video, path, max_shorts_per_video
                ): path
                for path in video_paths
            }

            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    job = future.result()
                    jobs.append(job)
                    logger.info(f"Completed processing: {path}")

                    if callback:
                        callback(job)

                except Exception as e:
                    logger.error(f"Error processing {path}: {e}", exc_info=True)

        logger.info(f"Batch processing completed: {len(jobs)} jobs")
        return jobs

    def export_shorts(
        self,
        shorts: List[ShortVideo],
        output_format: str = "mp4",
        include_captions: bool = True,
    ) -> List[Path]:
        """
        Export multiple shorts with optional enhancements

        Args:
            shorts: List of short videos to export
            output_format: Output video format
            include_captions: Whether to include captions

        Returns:
            List of exported video paths
        """
        logger.info(f"Exporting {len(shorts)} shorts")

        exported_paths = []
        for short in shorts:
            if short.output_path and short.output_path.exists():
                exported_paths.append(short.output_path)
            else:
                logger.warning(f"Short {short.id} has no output path")

        logger.info(f"Exported {len(exported_paths)} shorts")
        return exported_paths

    def queue_processing(
        self, video_paths: List[Path], priority: int = 0
    ) -> List[str]:
        """
        Queue videos for processing

        Args:
            video_paths: List of video file paths
            priority: Processing priority (higher = more urgent)

        Returns:
            List of job IDs
        """
        # This would integrate with a task queue like Celery or RQ
        # For now, it's a simplified implementation
        logger.info(f"Queuing {len(video_paths)} videos for processing")

        job_ids = []
        for path in video_paths:
            job_id = f"queue_{int(time.time())}_{path.stem}"
            job_ids.append(job_id)
            logger.info(f"Queued: {job_id}")

        return job_ids


class ExportManager:
    """Manage exports and output organization"""

    def __init__(self, output_dir: Path):
        """
        Initialize export manager

        Args:
            output_dir: Base output directory
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def organize_exports(self, job: BatchExportJob) -> Path:
        """
        Organize exported shorts into directories

        Args:
            job: Batch export job

        Returns:
            Path to organized export directory
        """
        # Create job-specific directory
        job_dir = self.output_dir / f"job_{job.id}"
        job_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (job_dir / "shorts").mkdir(exist_ok=True)
        (job_dir / "metadata").mkdir(exist_ok=True)

        logger.info(f"Organized exports in: {job_dir}")
        return job_dir

    def generate_manifest(self, job: BatchExportJob, output_path: Path):
        """
        Generate manifest file for a batch export job

        Args:
            job: Batch export job
            output_path: Path to save manifest
        """
        import json

        manifest = {
            "job_id": job.id,
            "input_video": str(job.input_video),
            "status": job.status.value,
            "created_at": str(job.created_at),
            "completed_at": str(job.completed_at) if job.completed_at else None,
            "shorts": [
                {
                    "id": short.id,
                    "output_path": str(short.output_path) if short.output_path else None,
                    "duration": short.scene.duration if short.scene else 0,
                    "viral_score": short.viral_score,
                }
                for short in job.shorts
            ],
            "analytics": job.analytics,
        }

        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Manifest saved to: {output_path}")
