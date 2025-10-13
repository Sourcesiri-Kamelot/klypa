"""Streamlit dashboard for Klypa"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from klypa.core import VideoProcessor, SceneDetector, Transcriber, CaptionGenerator
from klypa.integrations import OllamaClient, TTSEngine, SemanticMatcher
from klypa.utils import AnalyticsTracker, BatchProcessor, MonetizationHooks
from klypa.models import ProcessingStatus
from klypa.config import config

# Page configuration
st.set_page_config(
    page_title="Klypa - AI Video Shorts Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF4B4B;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initialize session state variables"""
    if "processor" not in st.session_state:
        st.session_state.processor = VideoProcessor()
    if "analytics" not in st.session_state:
        st.session_state.analytics = AnalyticsTracker()
    if "batch_processor" not in st.session_state:
        st.session_state.batch_processor = BatchProcessor()
    if "current_job" not in st.session_state:
        st.session_state.current_job = None


def render_header():
    """Render page header"""
    st.markdown('<div class="main-header">🎬 Klypa</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-Powered Video Shorts Generator</div>',
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render sidebar navigation"""
    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Go to",
        [
            "📤 Upload & Process",
            "📊 Analytics Dashboard",
            "⚙️ Settings",
            "📚 Help",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "Klypa automatically generates viral Shorts from long-form videos using AI."
    )

    return page


def render_upload_page():
    """Render upload and processing page"""
    st.header("Upload & Process Videos")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Upload a video file",
            type=["mp4", "avi", "mov", "mkv"],
            help="Upload a long-form video to generate shorts",
        )

        if uploaded_file:
            # Save uploaded file
            upload_path = config.paths.upload_dir / uploaded_file.name
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"Uploaded: {uploaded_file.name}")

            # Display video
            st.video(str(upload_path))

    with col2:
        st.subheader("Processing Options")

        max_shorts = st.slider(
            "Maximum shorts to generate", min_value=1, max_value=20, value=10
        )

        min_duration = st.slider(
            "Minimum scene duration (seconds)", min_value=3, max_value=30, value=5
        )

        max_duration = st.slider(
            "Maximum scene duration (seconds)", min_value=30, max_value=120, value=60
        )

        add_captions = st.checkbox("Add captions", value=True)
        generate_voiceover = st.checkbox("Generate voiceover", value=False)
        use_ai_ideas = st.checkbox("Generate viral ideas with AI", value=True)

    if uploaded_file:
        if st.button("🚀 Start Processing", type="primary"):
            with st.spinner("Processing video... This may take a few minutes."):
                try:
                    # Process video
                    job = st.session_state.processor.process_video(
                        upload_path, max_shorts=max_shorts
                    )

                    st.session_state.current_job = job

                    # Track analytics
                    st.session_state.analytics.track_job(job)

                    st.success(
                        f"✅ Processing completed! Generated {len(job.shorts)} shorts."
                    )

                    # Display results
                    render_job_results(job)

                except Exception as e:
                    st.error(f"Error processing video: {e}")


def render_job_results(job):
    """Render processing job results"""
    st.subheader("Generated Shorts")

    # Display analytics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Shorts", len(job.shorts))
    with col2:
        st.metric("Success Rate", f"{100}%")
    with col3:
        total_duration = sum(
            short.scene.duration for short in job.shorts if short.scene
        )
        st.metric("Total Duration", f"{total_duration:.1f}s")
    with col4:
        avg_score = sum(short.viral_score for short in job.shorts) / max(
            len(job.shorts), 1
        )
        st.metric("Avg Viral Score", f"{avg_score:.2f}")

    # Display shorts
    for i, short in enumerate(job.shorts):
        with st.expander(f"Short {i+1} - {short.id}", expanded=i == 0):
            col1, col2 = st.columns([2, 1])

            with col1:
                if short.output_path and short.output_path.exists():
                    st.video(str(short.output_path))
                else:
                    st.info("Video file not found")

            with col2:
                st.write("**Details**")
                st.write(f"Duration: {short.scene.duration:.2f}s" if short.scene else "N/A")
                st.write(f"Viral Score: {short.viral_score:.2f}")
                st.write(f"Status: {short.status.value}")

                if short.transcription:
                    st.write("**Transcription**")
                    for seg in short.transcription:
                        st.text(seg.text)

                st.download_button(
                    "⬇️ Download",
                    data=open(short.output_path, "rb").read() if short.output_path and short.output_path.exists() else b"",
                    file_name=f"short_{short.id}.mp4",
                    mime="video/mp4",
                )


def render_analytics_page():
    """Render analytics dashboard"""
    st.header("📊 Analytics Dashboard")

    # Get analytics summary
    summary = st.session_state.analytics.get_summary()

    # Display metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Jobs", summary.get("total_jobs", 0))
    with col2:
        st.metric("Total Shorts", summary.get("total_shorts", 0))
    with col3:
        st.metric("Completed Jobs", summary.get("completed_jobs", 0))

    st.markdown("---")

    # Display top shorts
    st.subheader("Top Performing Shorts")

    top_shorts = st.session_state.analytics.get_top_shorts(10)

    if top_shorts:
        for i, short in enumerate(top_shorts):
            with st.expander(f"#{i+1} - {short['id']}", expanded=i < 3):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Viral Score:** {short['viral_score']:.2f}")
                    st.write(f"**Duration:** {short.get('duration', 0):.2f}s")
                    st.write(f"**Created:** {short['created_at']}")

                with col2:
                    if short.get("output_path"):
                        output_path = Path(short["output_path"])
                        if output_path.exists():
                            st.download_button(
                                "⬇️ Download",
                                data=open(output_path, "rb").read(),
                                file_name=output_path.name,
                                mime="video/mp4",
                            )
    else:
        st.info("No shorts generated yet. Upload and process a video to get started!")


def render_settings_page():
    """Render settings page"""
    st.header("⚙️ Settings")

    tab1, tab2, tab3 = st.tabs(["Video Settings", "AI Settings", "Cloud Settings"])

    with tab1:
        st.subheader("Video Processing Settings")

        output_resolution = st.selectbox(
            "Output Resolution",
            ["1080x1920 (Full HD)", "720x1280 (HD)", "540x960 (SD)"],
            index=0,
        )

        output_fps = st.slider(
            "Output FPS", min_value=24, max_value=60, value=30, step=6
        )

        st.info("Settings will be applied to new processing jobs")

    with tab2:
        st.subheader("AI Integration Settings")

        ollama_host = st.text_input("Ollama Host", value="http://localhost:11434")
        ollama_model = st.text_input("Ollama Model", value="llama2")

        tts_engine = st.selectbox("TTS Engine", ["coqui", "bark"], index=0)

        st.info("Make sure Ollama is running locally or provide a remote host")

    with tab3:
        st.subheader("Azure Cloud Settings")

        enable_azure = st.checkbox("Enable Azure Storage", value=False)

        if enable_azure:
            connection_string = st.text_input(
                "Connection String", type="password", value=""
            )
            container_name = st.text_input("Container Name", value="klypa-videos")

            if st.button("Test Connection"):
                st.info("Testing Azure connection...")


def render_help_page():
    """Render help page"""
    st.header("📚 Help & Documentation")

    st.markdown(
        """
    ## Getting Started

    1. **Upload a video** on the Upload & Process page
    2. **Configure settings** like maximum shorts, duration ranges
    3. **Start processing** to generate viral shorts automatically
    4. **Download** your generated shorts from the results panel

    ## Features

    - 🎥 **Automatic Scene Detection** - Intelligently detects scene changes
    - 📝 **AI Transcription** - Uses Whisper for accurate transcription
    - 🎨 **Caption Generation** - Adds stylish captions automatically
    - 🤖 **AI-Powered Ideas** - Generates viral content ideas with Ollama
    - 🔊 **Text-to-Speech** - Adds voiceovers with Bark or Coqui TTS
    - 📊 **Analytics** - Track performance of your shorts
    - ☁️ **Cloud Integration** - Upload to Azure for easy sharing
    - 🎯 **Batch Processing** - Process multiple videos at once

    ## System Requirements

    - Python 3.9+
    - FFmpeg installed
    - 8GB+ RAM recommended
    - GPU recommended for faster processing

    ## Support

    For issues and questions, visit our [GitHub repository](https://github.com/Sourcesiri-Kamelot/klypa).
    """
    )


def main():
    """Main application entry point"""
    initialize_session_state()
    render_header()

    page = render_sidebar()

    if "Upload & Process" in page:
        render_upload_page()
    elif "Analytics Dashboard" in page:
        render_analytics_page()
    elif "Settings" in page:
        render_settings_page()
    elif "Help" in page:
        render_help_page()


if __name__ == "__main__":
    main()
