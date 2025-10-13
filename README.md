# 🎬 Klypa - AI-Powered Video Shorts Generator

Automatically generate multiple viral Shorts from long-form video uploads using open-source tools and AI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)

## ✨ Features

- 🎥 **Automatic Scene Detection** - Uses PySceneDetect to intelligently identify scene changes
- 📝 **AI Transcription** - Leverages OpenAI Whisper for accurate speech-to-text
- 🎨 **Caption Generation** - Automatically adds stylish captions with MoviePy
- 📱 **Vertical Format Export** - Optimized 9:16 aspect ratio for Shorts/Reels/TikTok
- 🤖 **AI-Powered Ideas** - Generates viral content ideas using Ollama
- 🔊 **Text-to-Speech** - Supports Bark and Coqui TTS for voiceovers
- 🧠 **Semantic Matching** - Uses Sentence Transformers for smart content analysis
- 💰 **Monetization Hooks** - Built-in analytics and revenue tracking
- 📦 **Batch Processing** - Process multiple videos efficiently
- 🎛️ **Streamlit Dashboard** - User-friendly web interface with preview/edit tools
- ☁️ **Azure Integration** - Cloud storage and deployment ready
- 🐳 **Docker Support** - Easy deployment with Docker/Docker Compose

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Sourcesiri-Kamelot/klypa.git
cd klypa

# Copy environment file
cp .env.example .env

# Build and run
docker-compose up --build

# Access the dashboard at http://localhost:8501
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/Sourcesiri-Kamelot/klypa.git
cd klypa

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .

# Run the dashboard
streamlit run src/app.py
```

## 📖 Usage

### Web Dashboard

1. Start the Streamlit dashboard:
```bash
streamlit run src/app.py
```

2. Upload a video through the web interface
3. Configure processing options (max shorts, duration, etc.)
4. Click "Start Processing"
5. Download your generated shorts!

### Python API

```python
from klypa import VideoProcessor
from pathlib import Path

# Initialize processor
processor = VideoProcessor()

# Process a video
job = processor.process_video(
    video_path=Path("input.mp4"),
    max_shorts=10
)

# Access generated shorts
for short in job.shorts:
    print(f"Short: {short.id}")
    print(f"Duration: {short.scene.duration}s")
    print(f"Output: {short.output_path}")
```

### Advanced Features

#### Generate Viral Ideas with Ollama

```python
from klypa.integrations import OllamaClient
from klypa.core import Transcriber

# Transcribe video
transcriber = Transcriber()
segments = transcriber.transcribe(Path("video.mp4"))

# Generate viral ideas
ollama = OllamaClient()
ideas = ollama.generate_viral_ideas(segments, num_ideas=5)

for idea in ideas:
    print(f"Title: {idea.title}")
    print(f"Hook: {idea.hook}")
```

#### Add Text-to-Speech Voiceovers

```python
from klypa.integrations import TTSEngine
from pathlib import Path

# Initialize TTS
tts = TTSEngine(engine="coqui")

# Generate voiceover
audio_path = tts.generate_voiceover(
    text="This is an amazing video!",
    output_path=Path("voiceover.wav")
)
```

#### Smart Scene Ranking

```python
from klypa.integrations import SemanticMatcher

matcher = SemanticMatcher()

# Rank scenes by virality potential
ranked_scenes = matcher.rank_scenes_by_virality(
    scenes=detected_scenes,
    transcriptions=scene_transcriptions
)

# Get top scenes
top_scenes = ranked_scenes[:5]
```

#### Batch Processing

```python
from klypa.utils import BatchProcessor
from pathlib import Path

processor = BatchProcessor(max_workers=3)

video_paths = [
    Path("video1.mp4"),
    Path("video2.mp4"),
    Path("video3.mp4")
]

jobs = processor.process_batch(
    video_paths=video_paths,
    max_shorts_per_video=10
)
```

## 🏗️ Architecture

```
klypa/
├── src/klypa/
│   ├── core/              # Core processing modules
│   │   ├── video_processor.py
│   │   ├── scene_detector.py
│   │   ├── transcriber.py
│   │   └── caption_generator.py
│   ├── integrations/      # Third-party integrations
│   │   ├── ollama_client.py
│   │   ├── tts_engine.py
│   │   └── semantic_matcher.py
│   ├── utils/             # Utility modules
│   │   ├── monetization.py
│   │   ├── batch_processor.py
│   │   └── azure_client.py
│   ├── models/            # Data models
│   └── config.py          # Configuration management
├── tests/                 # Test suite
├── examples/              # Example scripts
├── config/                # Configuration files
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## ⚙️ Configuration

Configuration is managed through environment variables or a `.env` file:

```bash
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_CONTAINER_NAME=klypa-videos

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Video Settings
MAX_VIDEO_DURATION=3600
MIN_SCENE_DURATION=3
MAX_SCENE_DURATION=60
OUTPUT_RESOLUTION=1080x1920
OUTPUT_FPS=30

# TTS
TTS_ENGINE=coqui  # Options: coqui, bark

# Paths
UPLOAD_DIR=./uploads
OUTPUT_DIR=./output
TEMP_DIR=./temp

# Monetization
ENABLE_ANALYTICS=true
WATERMARK_ENABLED=false
```

## 🐳 Deployment

### Azure Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions:

- Azure Container Instances (ACI)
- Azure App Service
- Azure Kubernetes Service (AKS)

### Docker Compose Production

```bash
docker-compose -f docker-compose.yml up -d
```

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=klypa --cov-report=html
```

## 📊 Analytics & Monetization

Klypa includes built-in analytics tracking:

```python
from klypa.utils import AnalyticsTracker, MonetizationHooks

# Track analytics
tracker = AnalyticsTracker()
tracker.track_job(job)

# Get insights
summary = tracker.get_summary()
top_shorts = tracker.get_top_shorts(limit=10)

# Monetization
monetization = MonetizationHooks()
revenue_estimate = monetization.calculate_revenue_estimate(job.shorts)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for transcription
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) for scene detection
- [MoviePy](https://github.com/Zulko/moviepy) for video editing
- [Ollama](https://ollama.ai/) for AI content generation
- [Coqui TTS](https://github.com/coqui-ai/TTS) and [Bark](https://github.com/suno-ai/bark) for text-to-speech
- [Sentence Transformers](https://www.sbert.net/) for semantic analysis

## 📧 Contact

For questions and support, please open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Real-time processing
- [ ] Advanced video effects
- [ ] Custom branding templates
- [ ] Social media auto-posting
- [ ] A/B testing for viral optimization
- [ ] Mobile app
- [ ] Plugin system for extensibility

---

Made with ❤️ by [Helo-im.Ai](https://github.com/Sourcesiri-Kamelot)
