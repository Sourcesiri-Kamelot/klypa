"""
Azure cloud integration example
"""

from pathlib import Path
from klypa import VideoProcessor
from klypa.utils import AzureStorageClient, AnalyticsTracker
import os

def main():
    print("☁️  Azure Cloud Integration Example\n")
    
    # Check for Azure credentials
    if not os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
        print("Warning: AZURE_STORAGE_CONNECTION_STRING not set")
        print("Please set it in your .env file or environment")
        print("\nRunning in local mode...")
        use_azure = False
    else:
        use_azure = True
        print("✓ Azure credentials found")
    
    # Initialize components
    processor = VideoProcessor()
    analytics = AnalyticsTracker()
    
    if use_azure:
        azure_client = AzureStorageClient()
    
    # Local video to process
    local_video = Path("example_video.mp4")
    
    if not local_video.exists():
        print(f"\nError: Video file not found at {local_video}")
        return
    
    # Upload to Azure (if configured)
    if use_azure:
        print(f"\n📤 Uploading video to Azure Storage...")
        try:
            blob_url = azure_client.upload_video(
                local_video,
                blob_name=f"uploads/{local_video.name}"
            )
            print(f"   ✓ Uploaded to: {blob_url}")
            
            # Generate temporary access URL
            sas_url = azure_client.generate_sas_url(
                f"uploads/{local_video.name}",
                expiry_hours=24
            )
            print(f"   ✓ Temporary URL (24h): {sas_url[:50]}...")
            
        except Exception as e:
            print(f"   ✗ Upload failed: {e}")
            print("   Continuing with local processing...")
    
    # Process video
    print(f"\n📹 Processing video...")
    job = processor.process_video(local_video, max_shorts=5)
    
    print(f"   ✓ Generated {len(job.shorts)} shorts")
    
    # Upload shorts to Azure (if configured)
    if use_azure and job.shorts:
        print(f"\n📤 Uploading shorts to Azure...")
        
        uploaded_urls = []
        for i, short in enumerate(job.shorts, 1):
            if short.output_path and short.output_path.exists():
                try:
                    blob_name = f"shorts/{short.id}.mp4"
                    url = azure_client.upload_video(
                        short.output_path,
                        blob_name=blob_name
                    )
                    uploaded_urls.append(url)
                    print(f"   ✓ Uploaded short {i}: {blob_name}")
                    
                    # Update metadata with cloud URL
                    short.metadata["azure_url"] = url
                    
                except Exception as e:
                    print(f"   ✗ Failed to upload short {i}: {e}")
        
        print(f"\n   Total uploaded: {len(uploaded_urls)}/{len(job.shorts)}")
    
    # Track analytics
    analytics.track_job(job)
    
    # List all shorts in Azure (if configured)
    if use_azure:
        print(f"\n📋 Listing all shorts in Azure Storage...")
        try:
            shorts_list = azure_client.list_videos(prefix="shorts/")
            print(f"   Found {len(shorts_list)} shorts in cloud:")
            for blob_name in shorts_list[:5]:
                print(f"     - {blob_name}")
            if len(shorts_list) > 5:
                print(f"     ... and {len(shorts_list) - 5} more")
        except Exception as e:
            print(f"   ✗ Failed to list: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"Input Video: {local_video.name}")
    print(f"Shorts Generated: {len(job.shorts)}")
    print(f"Status: {job.status.value}")
    
    if use_azure:
        print(f"Cloud Storage: Enabled ✓")
        print(f"Container: {azure_client.container_name}")
    else:
        print(f"Cloud Storage: Disabled (local only)")
    
    print(f"\n✅ Processing completed!")

if __name__ == "__main__":
    main()
