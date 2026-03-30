"""
Auto Pipeline: Generate short video → Upload to TikTok
MoneyPrinterTurbo + social-auto-upload integration
"""
import sys
import os
import shutil
import random
import logging
from uuid import uuid4
from pathlib import Path
from datetime import datetime

# Suppress noisy loggers
for _name in ("httpx", "httpcore", "openai", "urllib3", "PIL", "moviepy"):
    logging.getLogger(_name).setLevel(logging.WARNING)

# Setup paths
TURBO_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(os.environ.get("SOCIAL_UPLOAD_DIR", TURBO_DIR.parent / "social-auto-upload"))

sys.path.insert(0, str(TURBO_DIR))
sys.path.insert(0, str(UPLOAD_DIR))

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

from app.config import config
from app.models.schema import VideoParams, VideoAspect, VideoConcatMode
from app.services import task as tm


# --- Video topics pool ---
TOPICS = [
    "Top 5 iconic Kpop dance moves everyone should learn",
    "Why Korean school uniforms became a global fashion trend",
    "Best Kpop girl group choreography of 2024",
    "Korean girls daily makeup routine for school",
    "Cute Korean dance challenges trending on TikTok",
    "Why Kpop dance covers are taking over the internet",
    "Korean high school girls amazing talent show performances",
    "Best Korean streetwear and school fashion styles",
    "How Kpop idols train to become perfect dancers",
    "Top viral Korean dance trends you need to try",
    "Korean girls incredible singing covers that went viral",
    "Why Korean beauty standards inspire millions worldwide",
    "Amazing Kpop random play dance moments on the street",
    "Korean school festival performances that blew up online",
    "How Korean girls create the perfect aesthetic outfit",
    "Best Kpop dance practice videos that broke records",
    "Korean girls cute and funny TikTok moments compilation",
    "Why learning Kpop choreography is the best workout",
    "Top Korean girl group debut stages of all time",
    "Korean street fashion looks that are going viral",
]


def log(msg: str, level: str = "info"):
    """Clean log output."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"info": " ", "ok": "+", "err": "!", "step": ">"}
    print(f"  [{prefix.get(level, ' ')}] {timestamp}  {msg}")


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
    log(f"Topic: {topic}", "step")
    log("Generating script + downloading clips + rendering...", "info")

    result = tm.start(task_id=task_id, params=params)

    if result and "videos" in result and result["videos"]:
        video_path = result["videos"][0]
        size_mb = Path(video_path).stat().st_size / (1024 * 1024)
        log(f"Video ready ({size_mb:.1f} MB)", "ok")
        return {"path": video_path, "task_id": task_id, "topic": topic}

    log("Video generation FAILED", "err")
    return None


def prepare_upload(video_info: dict) -> Path:
    """Copy video + create metadata txt for social-auto-upload."""
    topic = video_info["topic"]
    video_path = Path(video_info["path"])

    safe_name = topic.lower().replace(" ", "_")[:50]
    dest_video = UPLOAD_DIR / "videos" / f"{safe_name}.mp4"
    dest_txt = UPLOAD_DIR / "videos" / f"{safe_name}.txt"

    os.makedirs(dest_video.parent, exist_ok=True)
    shutil.copy2(video_path, dest_video)

    words = topic.lower().split()
    hashtags = " ".join([f"#{w}" for w in words if len(w) > 2][:5])
    hashtags += " #shorts #viral #fyp"

    dest_txt.write_text(f"{topic}\n{hashtags}", encoding="utf-8")

    log(f"Prepared: {dest_video.name}", "ok")
    return dest_video


def upload_to_tiktok(video_file: Path):
    """Upload video to TikTok via social-auto-upload."""
    import asyncio

    os.chdir(UPLOAD_DIR)
    from uploader.tk_uploader.main_chrome import tiktok_setup, TiktokVideo
    from utils.files_times import get_title_and_hashtags

    account_file = UPLOAD_DIR / "cookies" / "tk_uploader" / "account.json"

    if not account_file.exists():
        log("TikTok cookie not found. Run TikTok login first.", "err")
        return False

    log("Checking TikTok cookie...", "info")
    valid = asyncio.run(tiktok_setup(account_file, handle=False))
    if not valid:
        log("Cookie expired. Re-login required.", "err")
        return False
    log("Cookie valid", "ok")

    title, tags = get_title_and_hashtags(str(video_file))
    log(f"Uploading: {title}", "step")

    app = TiktokVideo(title, video_file, tags, 0, account_file)
    asyncio.run(app.main(), debug=False)
    log("Upload complete", "ok")
    return True


def cleanup_all():
    """Remove all generated files to save disk space."""
    # Clean MoneyPrinterTurbo task storage
    storage_dir = TURBO_DIR / "storage" / "tasks"
    if storage_dir.exists():
        shutil.rmtree(storage_dir, ignore_errors=True)
        storage_dir.mkdir(parents=True, exist_ok=True)

    # Clean uploaded videos from social-auto-upload
    videos_dir = UPLOAD_DIR / "videos"
    if videos_dir.exists():
        for f in videos_dir.iterdir():
            if f.suffix in (".mp4", ".txt", ".png"):
                f.unlink(missing_ok=True)

    log("Cleaned up all temp files", "ok")


def run_pipeline(topic: str = None):
    """Run the full pipeline: generate → prepare → upload → cleanup."""
    os.chdir(TURBO_DIR)

    if not topic:
        topic = random.choice(TOPICS)

    print()
    print("  ========================================")
    print("   Auto Video Pipeline")
    print("  ========================================")
    print()

    # Step 1
    print("  [1/3] VIDEO GENERATION")
    print("  " + "-" * 40)
    video_info = generate_video(topic)
    if not video_info:
        log("Pipeline stopped.", "err")
        return False
    print()

    # Step 2
    print("  [2/3] PREPARE UPLOAD")
    print("  " + "-" * 40)
    video_file = prepare_upload(video_info)
    print()

    # Step 3
    print("  [3/3] TIKTOK UPLOAD")
    print("  " + "-" * 40)
    success = upload_to_tiktok(video_file)
    print()

    # Cleanup all temp files
    cleanup_all()

    print("  ========================================")
    if success:
        log("DONE - Video published to TikTok", "ok")
    else:
        log("PARTIAL - Video generated, upload failed", "err")
        log(f"Saved at: {video_file}", "info")
    print("  ========================================")
    print()
    return success


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    run_pipeline(topic)
