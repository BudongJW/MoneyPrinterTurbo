"""
Auto Pipeline: Generate short video → Upload to TikTok
MoneyPrinterTurbo + social-auto-upload integration
"""
import sys
import os
import shutil
import random
from uuid import uuid4
from pathlib import Path

# Setup paths
TURBO_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(r"C:\Users\wodnj\Downloads\social-auto-upload")

sys.path.insert(0, str(TURBO_DIR))
sys.path.insert(0, str(UPLOAD_DIR))

from app.config import config
from app.models.schema import VideoParams, VideoAspect, VideoConcatMode
from app.services import task as tm


# --- Video topics pool ---
TOPICS = [
    "Why cats make the best pets",
    "5 morning habits that changed my life",
    "How to stay productive working from home",
    "Simple cooking tips everyone should know",
    "Why reading books is better than scrolling",
    "The science behind good sleep habits",
    "Top 3 budget travel destinations in Asia",
    "How minimalism can improve your life",
    "Easy home workout for beginners",
    "Why journaling helps reduce stress",
    "The power of compound interest explained",
    "How to start a side hustle with zero money",
    "Best free apps to learn new skills",
    "Why walking 10000 steps matters",
    "How music affects your brain and mood",
    "Simple ways to save money every month",
    "The truth about social media and happiness",
    "How to build confidence in 30 days",
    "Why drinking water is so important",
    "Easy meal prep ideas for busy people",
]


def generate_video(topic: str) -> dict:
    """Generate a short video using MoneyPrinterTurbo."""
    params = VideoParams(
        video_subject=topic,
        video_language="en-US",
        video_aspect=VideoAspect.portrait,
        video_concat_mode=VideoConcatMode.random,
        video_clip_duration=3,
        video_count=1,
        voice_name="en-US-AriaNeural",
        voice_rate=1.0,
        voice_volume=1.0,
        bgm_type="random",
        bgm_volume=0.2,
        subtitle_enabled=False,
        font_name="MicrosoftYaHeiBold.ttc",
        text_fore_color="#FFFFFF",
        font_size=60,
        stroke_color="#000000",
        stroke_width=1.5,
        subtitle_position="bottom",
    )

    task_id = str(uuid4())
    print(f"[1/3] Generating video: {topic}")
    print(f"      Task ID: {task_id}")

    result = tm.start(task_id=task_id, params=params)

    if result and "videos" in result and result["videos"]:
        video_path = result["videos"][0]
        print(f"      Video: {video_path}")
        return {"path": video_path, "task_id": task_id, "topic": topic}

    print("      Video generation FAILED")
    return None


def prepare_upload(video_info: dict) -> Path:
    """Copy video + create metadata txt for social-auto-upload."""
    topic = video_info["topic"]
    video_path = Path(video_info["path"])

    # Generate safe filename
    safe_name = topic.lower().replace(" ", "_")[:50]
    dest_video = UPLOAD_DIR / "videos" / f"{safe_name}.mp4"
    dest_txt = UPLOAD_DIR / "videos" / f"{safe_name}.txt"

    # Copy video
    shutil.copy2(video_path, dest_video)

    # Generate hashtags from topic
    words = topic.lower().split()
    hashtags = " ".join([f"#{w}" for w in words if len(w) > 2][:5])
    hashtags += " #shorts #viral #fyp"

    # Write metadata
    title = topic
    dest_txt.write_text(f"{title}\n{hashtags}", encoding="utf-8")

    print(f"[2/3] Prepared: {dest_video.name}")
    return dest_video


def upload_to_tiktok(video_file: Path):
    """Upload video to TikTok via social-auto-upload."""
    import asyncio

    # Import from social-auto-upload
    os.chdir(UPLOAD_DIR)
    from uploader.tk_uploader.main_chrome import tiktok_setup, TiktokVideo
    from utils.files_times import get_title_and_hashtags

    account_file = UPLOAD_DIR / "cookies" / "tk_uploader" / "account.json"

    if not account_file.exists():
        print("      TikTok cookie not found. Run get_tk_cookie.py first.")
        return False

    print("[3/3] Uploading to TikTok...")

    valid = asyncio.run(tiktok_setup(account_file, handle=False))
    if not valid:
        print("      Cookie expired. Re-login required.")
        return False

    title, tags = get_title_and_hashtags(str(video_file))
    print(f"      Title: {title}")
    print(f"      Tags: {tags}")

    app = TiktokVideo(title, video_file, tags, 0, account_file)
    asyncio.run(app.main(), debug=False)
    print("      Upload SUCCESS!")
    return True


def run_pipeline(topic: str = None):
    """Run the full pipeline: generate → prepare → upload."""
    os.chdir(TURBO_DIR)

    if not topic:
        topic = random.choice(TOPICS)

    print("=" * 60)
    print("  Auto Pipeline: Generate → Upload")
    print("=" * 60)

    # Step 1: Generate video
    video_info = generate_video(topic)
    if not video_info:
        print("\nPipeline FAILED at video generation.")
        return False

    # Step 2: Prepare for upload
    video_file = prepare_upload(video_info)

    # Step 3: Upload to TikTok
    success = upload_to_tiktok(video_file)

    print("\n" + "=" * 60)
    if success:
        print("  Pipeline COMPLETE!")
    else:
        print("  Pipeline PARTIAL (video generated, upload failed)")
        print(f"  Video saved at: {video_file}")
    print("=" * 60)
    return success


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    run_pipeline(topic)
