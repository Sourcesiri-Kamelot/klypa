"""Sentence Transformers integration for semantic matching"""

import logging
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer, util

from ..models import Scene, TranscriptionSegment

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """Semantic matching using Sentence Transformers"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize semantic matcher

        Args:
            model_name: Sentence Transformer model name
        """
        logger.info(f"Loading Sentence Transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def match_scenes_to_topics(
        self, scenes: List[Scene], transcriptions: List[List[TranscriptionSegment]], topics: List[str]
    ) -> List[Tuple[Scene, str, float]]:
        """
        Match scenes to topics based on semantic similarity

        Args:
            scenes: List of detected scenes
            transcriptions: List of transcription segments for each scene
            topics: List of topic strings to match against

        Returns:
            List of tuples (scene, best_topic, similarity_score)
        """
        logger.info(f"Matching {len(scenes)} scenes to {len(topics)} topics")

        # Encode topics
        topic_embeddings = self.model.encode(topics, convert_to_tensor=True)

        matches = []
        for scene, trans_segments in zip(scenes, transcriptions):
            if not trans_segments:
                matches.append((scene, topics[0] if topics else "General", 0.0))
                continue

            # Combine transcription text for the scene
            scene_text = " ".join([seg.text for seg in trans_segments])

            if not scene_text.strip():
                matches.append((scene, topics[0] if topics else "General", 0.0))
                continue

            # Encode scene text
            scene_embedding = self.model.encode(scene_text, convert_to_tensor=True)

            # Calculate similarities
            similarities = util.cos_sim(scene_embedding, topic_embeddings)[0]

            # Find best match
            best_idx = similarities.argmax().item()
            best_score = similarities[best_idx].item()

            matches.append((scene, topics[best_idx], best_score))

        logger.info(f"Matched {len(matches)} scenes")
        return matches

    def rank_scenes_by_virality(
        self, scenes: List[Scene], transcriptions: List[List[TranscriptionSegment]]
    ) -> List[Tuple[Scene, float]]:
        """
        Rank scenes by potential virality using semantic analysis

        Args:
            scenes: List of detected scenes
            transcriptions: List of transcription segments for each scene

        Returns:
            List of tuples (scene, virality_score) sorted by score
        """
        logger.info(f"Ranking {len(scenes)} scenes by virality")

        # Viral keywords and phrases
        viral_patterns = [
            "amazing",
            "incredible",
            "shocking",
            "unbelievable",
            "wow",
            "omg",
            "must see",
            "you won't believe",
            "secret",
            "hack",
            "tip",
            "trick",
        ]

        # Encode viral patterns
        viral_embeddings = self.model.encode(viral_patterns, convert_to_tensor=True)

        scored_scenes = []
        for scene, trans_segments in zip(scenes, transcriptions):
            if not trans_segments:
                scored_scenes.append((scene, 0.0))
                continue

            # Combine transcription text
            scene_text = " ".join([seg.text for seg in trans_segments])

            if not scene_text.strip():
                scored_scenes.append((scene, 0.0))
                continue

            # Encode scene text
            scene_embedding = self.model.encode(scene_text, convert_to_tensor=True)

            # Calculate max similarity to viral patterns
            similarities = util.cos_sim(scene_embedding, viral_embeddings)[0]
            virality_score = similarities.max().item()

            scored_scenes.append((scene, virality_score))

        # Sort by score descending
        scored_scenes.sort(key=lambda x: x[1], reverse=True)

        logger.info(f"Ranked scenes, top score: {scored_scenes[0][1]:.3f}")
        return scored_scenes

    def find_similar_segments(
        self, query: str, transcriptions: List[TranscriptionSegment], top_k: int = 5
    ) -> List[Tuple[TranscriptionSegment, float]]:
        """
        Find most similar transcription segments to a query

        Args:
            query: Search query
            transcriptions: List of transcription segments
            top_k: Number of top results to return

        Returns:
            List of tuples (segment, similarity_score)
        """
        logger.info(f"Finding segments similar to: {query}")

        # Encode query
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        # Encode segments
        segment_texts = [seg.text for seg in transcriptions]
        segment_embeddings = self.model.encode(segment_texts, convert_to_tensor=True)

        # Calculate similarities
        similarities = util.cos_sim(query_embedding, segment_embeddings)[0]

        # Get top-k indices
        top_indices = similarities.argsort(descending=True)[:top_k]

        results = [
            (transcriptions[idx], similarities[idx].item())
            for idx in top_indices
        ]

        logger.info(f"Found {len(results)} similar segments")
        return results
