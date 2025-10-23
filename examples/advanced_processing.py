"""
Advanced example: Process video with AI-powered features
"""

from pathlib import Path
from klypa.core import VideoProcessor, Transcriber
from klypa.integrations import OllamaClient, TTSEngine, SemanticMatcher

def main():
    # Initialize components
    print("Initializing AI components...")
    
    processor = VideoProcessor()
    transcriber = Transcriber(model_name="base")
    ollama = OllamaClient()
    tts = TTSEngine(engine="coqui")
    matcher = SemanticMatcher()
    
    # Input video
    video_path = Path("example_video.mp4")
    
    if not video_path.exists():
        print(f"Error: Video file not found at {video_path}")
        return
    
    print(f"\n🎬 Processing video: {video_path}")
    
    # Step 1: Process video and detect scenes
    print("\n📹 Step 1: Detecting scenes and processing video...")
    job = processor.process_video(video_path, max_shorts=5)
    
    print(f"   ✓ Generated {len(job.shorts)} shorts")
    
    # Step 2: Generate viral ideas with Ollama
    print("\n🤖 Step 2: Generating viral content ideas...")
    
    # Get transcription from first short
    if job.shorts and job.shorts[0].transcription:
        ideas = ollama.generate_viral_ideas(
            job.shorts[0].transcription,
            num_ideas=3
        )
        
        print(f"   ✓ Generated {len(ideas)} viral ideas:")
        for i, idea in enumerate(ideas, 1):
            print(f"\n   Idea {i}:")
            print(f"     Title: {idea.title}")
            print(f"     Hook: {idea.hook}")
            print(f"     CTA: {idea.call_to_action}")
    
    # Step 3: Rank scenes by virality
    print("\n🎯 Step 3: Ranking scenes by viral potential...")
    
    scenes = [short.scene for short in job.shorts if short.scene]
    transcriptions = [short.transcription for short in job.shorts]
    
    if scenes and transcriptions:
        ranked = matcher.rank_scenes_by_virality(scenes, transcriptions)
        
        print(f"   ✓ Top 3 scenes by virality:")
        for i, (scene, score) in enumerate(ranked[:3], 1):
            print(f"     {i}. Score: {score:.3f} - Duration: {scene.duration:.1f}s")
    
    # Step 4: Generate voiceovers for top shorts
    print("\n🔊 Step 4: Generating voiceovers...")
    
    for i, short in enumerate(job.shorts[:2], 1):
        if short.transcription:
            text = " ".join([seg.text for seg in short.transcription])
            voiceover_path = Path(f"output/voiceover_{short.id}.wav")
            
            try:
                tts.generate_voiceover(text[:200], voiceover_path)
                print(f"   ✓ Voiceover {i} saved to: {voiceover_path}")
                short.voiceover_path = voiceover_path
            except Exception as e:
                print(f"   ✗ Error generating voiceover {i}: {e}")
    
    # Step 5: Generate titles and tags
    print("\n📝 Step 5: Generating titles and tags...")
    
    for i, short in enumerate(job.shorts, 1):
        if short.transcription:
            content = " ".join([seg.text for seg in short.transcription])
            
            title = ollama.generate_title(content)
            tags = ollama.generate_tags(content, num_tags=5)
            
            print(f"\n   Short {i}:")
            print(f"     Title: {title}")
            print(f"     Tags: {', '.join(tags)}")
            
            short.metadata["title"] = title
            short.metadata["tags"] = tags
    
    print("\n\n✅ Advanced processing completed!")
    print(f"\nAll shorts saved to: {job.shorts[0].output_path.parent if job.shorts else 'output/'}")

if __name__ == "__main__":
    main()
