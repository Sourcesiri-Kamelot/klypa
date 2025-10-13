"""Monetization and analytics utilities"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json

from ..models import ShortVideo, BatchExportJob

logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """Track analytics for monetization"""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize analytics tracker

        Args:
            storage_path: Path to store analytics data
        """
        self.storage_path = storage_path or Path("./analytics.json")
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """Load analytics data from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading analytics: {e}")
        return {"jobs": [], "shorts": [], "summary": {}}

    def _save_data(self):
        """Save analytics data to storage"""
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")

    def track_job(self, job: BatchExportJob):
        """
        Track a batch export job

        Args:
            job: BatchExportJob to track
        """
        job_data = {
            "id": job.id,
            "input_video": str(job.input_video),
            "status": job.status.value,
            "shorts_count": len(job.shorts),
            "created_at": str(job.created_at),
            "completed_at": str(job.completed_at) if job.completed_at else None,
            "analytics": job.analytics,
        }

        self.data["jobs"].append(job_data)
        self._update_summary()
        self._save_data()
        logger.info(f"Tracked job: {job.id}")

    def track_short(self, short: ShortVideo):
        """
        Track a generated short video

        Args:
            short: ShortVideo to track
        """
        short_data = {
            "id": short.id,
            "source_video": str(short.source_video),
            "output_path": str(short.output_path) if short.output_path else None,
            "viral_score": short.viral_score,
            "duration": short.scene.duration if short.scene else 0,
            "status": short.status.value,
            "created_at": str(short.created_at),
            "metadata": short.metadata,
        }

        self.data["shorts"].append(short_data)
        self._update_summary()
        self._save_data()
        logger.info(f"Tracked short: {short.id}")

    def _update_summary(self):
        """Update summary statistics"""
        self.data["summary"] = {
            "total_jobs": len(self.data["jobs"]),
            "total_shorts": len(self.data["shorts"]),
            "completed_jobs": sum(
                1 for job in self.data["jobs"] if job["status"] == "completed"
            ),
            "average_viral_score": sum(
                short["viral_score"] for short in self.data["shorts"]
            )
            / max(len(self.data["shorts"]), 1),
            "last_updated": str(datetime.now()),
        }

    def get_summary(self) -> Dict:
        """Get analytics summary"""
        return self.data["summary"]

    def get_top_shorts(self, limit: int = 10) -> List[Dict]:
        """
        Get top performing shorts

        Args:
            limit: Number of shorts to return

        Returns:
            List of top shorts sorted by viral score
        """
        sorted_shorts = sorted(
            self.data["shorts"], key=lambda x: x["viral_score"], reverse=True
        )
        return sorted_shorts[:limit]


class MonetizationHooks:
    """Monetization integration hooks"""

    def __init__(self, analytics_tracker: Optional[AnalyticsTracker] = None):
        """
        Initialize monetization hooks

        Args:
            analytics_tracker: AnalyticsTracker instance
        """
        self.analytics = analytics_tracker or AnalyticsTracker()

    def add_watermark(self, video_path: Path, output_path: Path, watermark_text: str = "Created with Klypa"):
        """
        Add watermark to video (placeholder implementation)

        Args:
            video_path: Input video path
            output_path: Output video path
            watermark_text: Watermark text
        """
        logger.info(f"Adding watermark to: {video_path}")
        # This would use MoviePy to add a watermark
        # For now, it's a placeholder
        from shutil import copy2
        copy2(video_path, output_path)

    def generate_affiliate_link(self, short: ShortVideo) -> str:
        """
        Generate affiliate link for a short

        Args:
            short: ShortVideo object

        Returns:
            Affiliate link URL
        """
        # Placeholder implementation
        return f"https://example.com/shorts/{short.id}?ref=klypa"

    def track_conversion(self, short_id: str, conversion_type: str):
        """
        Track a conversion event

        Args:
            short_id: Short video ID
            conversion_type: Type of conversion (view, click, subscribe, etc.)
        """
        logger.info(f"Conversion tracked: {short_id} - {conversion_type}")
        # This would integrate with analytics platforms
        pass

    def calculate_revenue_estimate(self, shorts: List[ShortVideo]) -> float:
        """
        Calculate estimated revenue from shorts

        Args:
            shorts: List of short videos

        Returns:
            Estimated revenue in USD
        """
        # Simplified calculation based on viral scores
        base_cpm = 2.0  # $2 CPM
        estimated_views = sum(short.viral_score * 10000 for short in shorts)
        revenue = (estimated_views / 1000) * base_cpm
        return round(revenue, 2)
