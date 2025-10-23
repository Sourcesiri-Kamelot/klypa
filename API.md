# Klypa API Reference

## Core Modules

### VideoProcessor

Main orchestrator for video processing.

```python
from klypa import VideoProcessor

processor = VideoProcessor(
    transcriber=None,        # Optional Transcriber instance
    scene_detector=None,     # Optional SceneDetector instance
    caption_generator=None   # Optional CaptionGenerator instance
)

# Process a video
job = processor.process_video(
    video_path=Path("video.mp4"),
    max_shorts=10
)

# Extract metadata
metadata = processor.extract_metadata(Path("video.mp4"))

# Create vertical short
output_path = processor.create_vertical_short(
    video_path=Path("video.mp4"),
    scene=scene_object,
    output_path=Path("output.mp4")
)
```

### SceneDetector

Detect scenes in videos using PySceneDetect.

```python
from klypa.core import SceneDetector

detector = SceneDetector(
    threshold=27.0,      # Lower = more sensitive
    min_scene_len=15     # Minimum scene length in frames
)

# Detect scenes
scenes = detector.detect_scenes(Path("video.mp4"))

# Filter scenes by duration
filtered = detector.filter_scenes(
    scenes,
    min_duration=3.0,
    max_duration=60.0
)
```

### Transcriber

Transcribe audio using OpenAI Whisper.

```python
from klypa.core import Transcriber

transcriber = Transcriber(model_name="base")
# Models: tiny, base, small, medium, large

# Transcribe full video
segments = transcriber.transcribe(
    audio_path=Path("video.mp4"),
    language="en"  # Optional
)

# Transcribe segment
segments = transcriber.transcribe_segment(
    audio_path=Path("video.mp4"),
    start_time=10.0,
    end_time=20.0
)
```

### CaptionGenerator

Generate and add captions to videos.

```python
from klypa.core import CaptionGenerator

generator = CaptionGenerator(
    font="Arial",
    font_size=48,
    color="white",
    bg_color="black",
    stroke_color="black",
    stroke_width=2
)

# Create captions from transcription
captions = generator.create_captions_from_transcription(
    segments=transcription_segments,
    video_width=1080,
    video_height=1920
)

# Add captions to video
output = generator.add_captions_to_video(
    video_path=Path("input.mp4"),
    captions=captions,
    output_path=Path("output.mp4")
)
```

## AI Integrations

### OllamaClient

Generate viral content ideas using Ollama.

```python
from klypa.integrations import OllamaClient

ollama = OllamaClient(
    host="http://localhost:11434",
    model="llama2"
)

# Generate viral ideas
ideas = ollama.generate_viral_ideas(
    transcription=segments,
    num_ideas=3
)

# Generate title
title = ollama.generate_title(content="video content")

# Generate tags
tags = ollama.generate_tags(content="video content", num_tags=5)
```

### TTSEngine

Text-to-speech using Bark or Coqui.

```python
from klypa.integrations import TTSEngine

tts = TTSEngine(engine="coqui")  # or "bark"

# Generate voiceover
audio_path = tts.generate_voiceover(
    text="This is the voiceover text",
    output_path=Path("voiceover.wav"),
    voice="default"
)

# Batch voiceovers
paths = tts.generate_batch_voiceovers(
    texts=["Text 1", "Text 2", "Text 3"],
    output_dir=Path("output/"),
    prefix="voiceover"
)
```

### SemanticMatcher

Semantic analysis using Sentence Transformers.

```python
from klypa.integrations import SemanticMatcher

matcher = SemanticMatcher(model_name="all-MiniLM-L6-v2")

# Match scenes to topics
matches = matcher.match_scenes_to_topics(
    scenes=scene_list,
    transcriptions=transcription_list,
    topics=["tutorial", "review", "vlog"]
)

# Rank scenes by virality
ranked = matcher.rank_scenes_by_virality(
    scenes=scene_list,
    transcriptions=transcription_list
)

# Find similar segments
results = matcher.find_similar_segments(
    query="funny moment",
    transcriptions=segments,
    top_k=5
)
```

## Utilities

### BatchProcessor

Process multiple videos efficiently.

```python
from klypa.utils import BatchProcessor

processor = BatchProcessor(max_workers=2)

# Process batch
jobs = processor.process_batch(
    video_paths=[Path("v1.mp4"), Path("v2.mp4")],
    max_shorts_per_video=10,
    callback=lambda job: print(f"Done: {job.id}")
)

# Export shorts
paths = processor.export_shorts(
    shorts=short_list,
    output_format="mp4",
    include_captions=True
)

# Queue for processing
job_ids = processor.queue_processing(
    video_paths=[Path("v1.mp4")],
    priority=1
)
```

### AnalyticsTracker

Track analytics for monetization.

```python
from klypa.utils import AnalyticsTracker

tracker = AnalyticsTracker(storage_path=Path("analytics.json"))

# Track job
tracker.track_job(batch_job)

# Track short
tracker.track_short(short_video)

# Get summary
summary = tracker.get_summary()
# Returns: {'total_jobs': 10, 'total_shorts': 50, ...}

# Get top shorts
top = tracker.get_top_shorts(limit=10)
```

### MonetizationHooks

Monetization features.

```python
from klypa.utils import MonetizationHooks

monetization = MonetizationHooks()

# Add watermark
monetization.add_watermark(
    video_path=Path("input.mp4"),
    output_path=Path("output.mp4"),
    watermark_text="Created with Klypa"
)

# Generate affiliate link
link = monetization.generate_affiliate_link(short)

# Track conversion
monetization.track_conversion(
    short_id="short_001",
    conversion_type="view"
)

# Calculate revenue estimate
revenue = monetization.calculate_revenue_estimate(shorts_list)
```

### AzureStorageClient

Azure Blob Storage integration.

```python
from klypa.utils import AzureStorageClient

azure = AzureStorageClient(
    connection_string="your_connection_string",
    container_name="klypa-videos"
)

# Upload video
url = azure.upload_video(
    local_path=Path("video.mp4"),
    blob_name="uploads/video.mp4"
)

# Download video
path = azure.download_video(
    blob_name="uploads/video.mp4",
    local_path=Path("downloaded.mp4")
)

# List videos
videos = azure.list_videos(prefix="shorts/")

# Delete video
azure.delete_video("uploads/video.mp4")

# Generate SAS URL
sas_url = azure.generate_sas_url(
    blob_name="shorts/video.mp4",
    expiry_hours=24
)
```

## Data Models

### Scene

```python
from klypa.models import Scene

scene = Scene(
    start_time=0.0,
    end_time=10.0,
    duration=10.0,
    frame_start=0,
    frame_end=300,
    confidence=1.0,
    description="Optional description"
)

# Get formatted timestamp
print(scene.timestamp)  # "0.00s - 10.00s"
```

### TranscriptionSegment

```python
from klypa.models import TranscriptionSegment

segment = TranscriptionSegment(
    text="Hello world",
    start=0.0,
    end=2.0,
    confidence=0.95
)
```

### Caption

```python
from klypa.models import Caption

caption = Caption(
    text="Caption text",
    start_time=0.0,
    end_time=2.0,
    position=(540, 1600),
    font_size=48,
    color="white",
    background_color="black"
)
```

### ShortVideo

```python
from klypa.models import ShortVideo, ProcessingStatus

short = ShortVideo(
    id="short_001",
    source_video=Path("source.mp4"),
    output_path=Path("output.mp4"),
    scene=scene_object,
    transcription=[segment1, segment2],
    captions=[caption1, caption2],
    viral_score=0.85,
    viral_idea="Viral idea text",
    voiceover_path=Path("voiceover.wav"),
    status=ProcessingStatus.COMPLETED,
    metadata={"custom": "data"}
)
```

### BatchExportJob

```python
from klypa.models import BatchExportJob, ProcessingStatus

job = BatchExportJob(
    id="job_001",
    input_video=Path("input.mp4"),
    shorts=[short1, short2],
    status=ProcessingStatus.COMPLETED,
    analytics={"total_scenes": 10}
)
```

## Configuration

### Config Object

```python
from klypa.config import config

# Video settings
config.video.max_duration  # Maximum video duration
config.video.min_scene_duration  # Minimum scene duration
config.video.max_scene_duration  # Maximum scene duration
config.video.output_resolution  # (width, height)
config.video.output_fps  # Frames per second

# Paths
config.paths.upload_dir
config.paths.output_dir
config.paths.temp_dir

# Azure
config.azure.connection_string
config.azure.container_name

# Ollama
config.ollama.host
config.ollama.model

# TTS
config.tts.engine  # "coqui" or "bark"
config.tts.voice

# Monetization
config.monetization.enable_analytics
config.monetization.watermark_enabled
```

## Error Handling

All modules raise standard Python exceptions:

```python
from pathlib import Path

try:
    job = processor.process_video(Path("video.mp4"))
except FileNotFoundError:
    print("Video file not found")
except Exception as e:
    print(f"Processing error: {e}")
```

## Logging

Configure logging level:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("klypa")
```

## Events and Callbacks

Use callbacks for progress tracking:

```python
def on_progress(job):
    print(f"Processed: {job.id}, Shorts: {len(job.shorts)}")

batch_processor.process_batch(
    video_paths=videos,
    callback=on_progress
)
```

---

For more examples, see the [examples/](examples/) directory.
