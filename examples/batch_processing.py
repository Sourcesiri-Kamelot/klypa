"""
Batch processing example: Process multiple videos
"""

from pathlib import Path
from klypa.utils import BatchProcessor, ExportManager, AnalyticsTracker

def progress_callback(job):
    """Callback function for progress updates"""
    print(f"✓ Completed: {job.input_video.name}")
    print(f"  Generated {len(job.shorts)} shorts")

def main():
    print("🎬 Batch Processing Example\n")
    
    # Initialize components
    batch_processor = BatchProcessor(max_workers=2)
    export_manager = ExportManager(Path("output/batch"))
    analytics = AnalyticsTracker(Path("output/batch_analytics.json"))
    
    # List of videos to process
    video_paths = [
        Path("video1.mp4"),
        Path("video2.mp4"),
        Path("video3.mp4"),
    ]
    
    # Filter existing files
    existing_videos = [p for p in video_paths if p.exists()]
    
    if not existing_videos:
        print("Error: No video files found!")
        print(f"Please add video files: {', '.join([p.name for p in video_paths])}")
        return
    
    print(f"Found {len(existing_videos)} videos to process:")
    for video in existing_videos:
        print(f"  - {video.name}")
    
    # Process batch
    print(f"\n📹 Starting batch processing with {batch_processor.max_workers} workers...")
    
    jobs = batch_processor.process_batch(
        video_paths=existing_videos,
        max_shorts_per_video=5,
        callback=progress_callback
    )
    
    # Track analytics for each job
    print("\n📊 Tracking analytics...")
    for job in jobs:
        analytics.track_job(job)
        for short in job.shorts:
            analytics.track_short(short)
    
    # Organize exports
    print("\n📦 Organizing exports...")
    for job in jobs:
        job_dir = export_manager.organize_exports(job)
        manifest_path = job_dir / "manifest.json"
        export_manager.generate_manifest(job, manifest_path)
        print(f"  ✓ Job organized: {job_dir}")
    
    # Display summary
    print("\n" + "="*50)
    print("BATCH PROCESSING SUMMARY")
    print("="*50)
    
    summary = analytics.get_summary()
    print(f"Total Jobs: {summary['total_jobs']}")
    print(f"Total Shorts: {summary['total_shorts']}")
    print(f"Completed Jobs: {summary['completed_jobs']}")
    print(f"Average Viral Score: {summary['average_viral_score']:.3f}")
    
    print("\n📈 Top 5 Shorts:")
    top_shorts = analytics.get_top_shorts(5)
    for i, short in enumerate(top_shorts, 1):
        print(f"  {i}. {short['id']}")
        print(f"     Score: {short['viral_score']:.3f}")
        print(f"     Duration: {short.get('duration', 0):.1f}s")
    
    print(f"\n✅ Batch processing completed!")
    print(f"Results saved to: output/batch/")

if __name__ == "__main__":
    main()
