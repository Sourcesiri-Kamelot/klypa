# Klypa Quick Start Guide

## Installation

### Option 1: Docker (Recommended)

```bash
# Clone and start
git clone https://github.com/Sourcesiri-Kamelot/klypa.git
cd klypa
cp .env.example .env
docker-compose up --build

# Access at http://localhost:8501
```

### Option 2: Local Setup

```bash
# Clone repository
git clone https://github.com/Sourcesiri-Kamelot/klypa.git
cd klypa

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run Streamlit app
streamlit run src/app.py
```

## Basic Usage

### 1. Web Interface

```bash
streamlit run src/app.py
# Open http://localhost:8501
# Upload video → Configure options → Process → Download shorts
```

### 2. Python API

```python
from klypa import VideoProcessor
from pathlib import Path

processor = VideoProcessor()
job = processor.process_video(Path("video.mp4"), max_shorts=10)

for short in job.shorts:
    print(f"Generated: {short.output_path}")
```

### 3. CLI Examples

```bash
# Basic processing
python examples/basic_processing.py

# Advanced with AI features
python examples/advanced_processing.py

# Batch processing
python examples/batch_processing.py

# Azure integration
python examples/azure_integration.py
```

## Configuration

Edit `.env` file or set environment variables:

```bash
# Essential settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
OUTPUT_RESOLUTION=1080x1920
OUTPUT_FPS=30

# Azure (optional)
AZURE_STORAGE_CONNECTION_STRING=your_string
AZURE_STORAGE_CONTAINER_NAME=klypa-videos

# TTS
TTS_ENGINE=coqui  # or bark
```

## Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| Scene Detection | PySceneDetect for smart scene cuts | ✅ |
| Transcription | Whisper AI for accurate speech-to-text | ✅ |
| Captions | Auto-generated stylish captions | ✅ |
| Vertical Export | 9:16 format for Shorts/Reels/TikTok | ✅ |
| AI Ideas | Ollama-powered viral content ideas | ✅ |
| Voiceovers | Bark/Coqui TTS integration | ✅ |
| Semantic Match | Smart content analysis | ✅ |
| Analytics | Built-in tracking and monetization | ✅ |
| Batch Export | Process multiple videos | ✅ |
| Dashboard | Streamlit web interface | ✅ |
| Azure Cloud | Cloud storage and deployment | ✅ |
| Docker | Containerized deployment | ✅ |

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows: Download from ffmpeg.org
   ```

2. **Out of memory**
   - Increase Docker memory limit
   - Process fewer shorts at a time
   - Use smaller video files for testing

3. **Ollama connection failed**
   ```bash
   # Install Ollama
   curl https://ollama.ai/install.sh | sh
   
   # Start Ollama
   ollama serve
   
   # Pull model
   ollama pull llama2
   ```

4. **GPU not detected**
   - Install CUDA toolkit
   - Install PyTorch with CUDA support
   - Docker: Use nvidia-docker runtime

## Next Steps

1. Check out [examples/](examples/) for more usage patterns
2. Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
3. Customize processing in `src/klypa/config.py`
4. Extend functionality in `src/klypa/core/`

## Support

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/Sourcesiri-Kamelot/klypa/issues)
- 💬 [Discussions](https://github.com/Sourcesiri-Kamelot/klypa/discussions)

---

Happy creating! 🎬✨
