"""
Basic example: Process a single video and generate shorts
"""

from pathlib import Path
from klypa import VideoProcessor

def main():
    # Initialize processor
    processor = VideoProcessor()
    
    # Path to your input video
    video_path = Path("example_video.mp4")
    
    # Check if file exists
    if not video_path.exists():
        print(f"Error: Video file not found at {video_path}")
        print("Please provide a valid video file.")
        return
    
    print(f"Processing video: {video_path}")
    
    # Process the video
    job = processor.process_video(
        video_path=video_path,
        max_shorts=10  # Generate up to 10 shorts
    )
    
    # Print results
    print(f"\n✅ Processing completed!")
    print(f"Status: {job.status.value}")
    print(f"Generated {len(job.shorts)} shorts")
    print(f"\nAnalytics:")
    print(f"  - Total scenes detected: {job.analytics.get('total_scenes', 0)}")
    print(f"  - Filtered scenes: {job.analytics.get('filtered_scenes', 0)}")
    print(f"  - Source duration: {job.analytics.get('source_duration', 0):.2f}s")
    
    # Print details for each short
    print(f"\nGenerated Shorts:")
    for i, short in enumerate(job.shorts, 1):
        print(f"\n{i}. Short ID: {short.id}")
        print(f"   Duration: {short.scene.duration:.2f}s")
        print(f"   Output: {short.output_path}")
        print(f"   Viral Score: {short.viral_score:.2f}")
        
        if short.transcription:
            print(f"   Transcription preview: {short.transcription[0].text[:50]}...")

if __name__ == "__main__":
    main()
