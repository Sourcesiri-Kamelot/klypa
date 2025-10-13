"""Text-to-Speech engine integration"""

import logging
from pathlib import Path
from typing import Optional

from ..config import config

logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-Speech engine wrapper"""

    def __init__(self, engine: Optional[str] = None):
        """
        Initialize TTS engine

        Args:
            engine: Engine name ('coqui' or 'bark')
        """
        self.engine = engine or config.tts.engine
        self._model = None

    def _load_coqui(self):
        """Load Coqui TTS model"""
        try:
            from TTS.api import TTS

            self._model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            logger.info("Coqui TTS model loaded")
        except Exception as e:
            logger.error(f"Error loading Coqui TTS: {e}")
            raise

    def _load_bark(self):
        """Load Bark TTS model"""
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models

            preload_models()
            self._model = generate_audio
            logger.info("Bark TTS model loaded")
        except Exception as e:
            logger.error(f"Error loading Bark TTS: {e}")
            raise

    def generate_voiceover(
        self, text: str, output_path: Path, voice: Optional[str] = None
    ) -> Path:
        """
        Generate voiceover from text

        Args:
            text: Text to convert to speech
            output_path: Path for output audio file
            voice: Optional voice identifier

        Returns:
            Path to generated audio file
        """
        logger.info(f"Generating voiceover with {self.engine} engine")

        if self.engine == "coqui":
            return self._generate_coqui(text, output_path)
        elif self.engine == "bark":
            return self._generate_bark(text, output_path)
        else:
            raise ValueError(f"Unsupported TTS engine: {self.engine}")

    def _generate_coqui(self, text: str, output_path: Path) -> Path:
        """Generate voiceover using Coqui TTS"""
        if self._model is None:
            self._load_coqui()

        self._model.tts_to_file(text=text, file_path=str(output_path))
        logger.info(f"Coqui voiceover saved to: {output_path}")
        return output_path

    def _generate_bark(self, text: str, output_path: Path) -> Path:
        """Generate voiceover using Bark"""
        if self._model is None:
            self._load_bark()

        from scipy.io.wavfile import write as write_wav
        from bark import SAMPLE_RATE

        audio_array = self._model(text)
        write_wav(str(output_path), SAMPLE_RATE, audio_array)
        logger.info(f"Bark voiceover saved to: {output_path}")
        return output_path

    def generate_batch_voiceovers(
        self, texts: list[str], output_dir: Path, prefix: str = "voiceover"
    ) -> list[Path]:
        """
        Generate multiple voiceovers in batch

        Args:
            texts: List of texts to convert
            output_dir: Output directory for audio files
            prefix: Prefix for output filenames

        Returns:
            List of paths to generated audio files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []

        for i, text in enumerate(texts):
            output_path = output_dir / f"{prefix}_{i+1}.wav"
            try:
                path = self.generate_voiceover(text, output_path)
                paths.append(path)
            except Exception as e:
                logger.error(f"Error generating voiceover {i+1}: {e}")

        logger.info(f"Generated {len(paths)}/{len(texts)} voiceovers")
        return paths
