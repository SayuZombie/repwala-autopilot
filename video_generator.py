import argparse, asyncio, json, math, subprocess, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

W, H = 1080, 1920
BG = (17, 24, 32)
LIME = (183, 243, 107)
WHITE = (248, 250, 252)
MUTED = (173, 184, 194)

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, max_width):
    words = str(text).split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            line = test
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def make_frame(scene, title, caption, index, total, outpath):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # Subtle vertical accent and brand framing
    d.rounded_rectangle((54, 64, 1026, 1856), radius=42, outline=(48, 62, 73), width=3)
    d.rounded_rectangle((54, 64, 72, 1856), radius=8, fill=LIME)
    d.text((112, 112), "REPWALA", font=font(42, True), fill=LIME)
    d.text((112, 174), "TRAIN SMART. LOOK STRONG.", font=font(23, True), fill=MUTED)
    d.line((112, 250, 968, 250), fill=(60, 75, 85), width=2)
    d.text((112, 330), f"FITNESS SHORT  /  {index:02d}", font=font(24, True), fill=LIME)
    heading = str(scene.get("visual", scene.get("text", title)))
    lines = wrap(d, heading, font(64, True), 820)
    y = 470
    for line in lines[:5]:
        d.text((112, y), line, font=font(64, True), fill=WHITE)
        y += 88
    # Captions panel
    d.rounded_rectangle((100, 1350, 980, 1695), radius=28, fill=(30, 40, 49))
    cap_lines = wrap(d, caption, font(38, True), 790)
    cy = 1410
    for line in cap_lines[:5]:
        d.text((145, cy), line, font=font(38, True), fill=WHITE)
        cy += 58
    d.text((112, 1765), "FITNESS KA ASLI SCENE.", font=font(25, True), fill=LIME)
    d.text((900, 1765), f"{index}/{total}", font=font(25, True), fill=MUTED)
    im.save(outpath, quality=95)

async def make_voice(text, path, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(path))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--voice", default="hi-IN-SwaraNeural")
    a = p.parse_args()
    src = Path(a.input)
    draft = json.loads(src.read_text(encoding="utf-8"))
    narration = str(draft.get("narration", "")).strip()
    scenes = draft.get("scene_plan") or []
    if not narration or not scenes:
        raise SystemExit("Input JSON must contain narration and a non-empty scene_plan.")
    out = Path("video_output"); out.mkdir(exist_ok=True)
    work = Path("video_work"); work.mkdir(exist_ok=True)
    audio = work / "narration.mp3"
    asyncio.run(make_voice(narration, audio, a.voice))
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio)], text=True)
    duration = float(probe.strip())
    total_frames = max(2, math.ceil(duration * 2))
    scene_durations = [max(1, int(s.get("duration_seconds", 5))) for s in scenes]
    total_scene = sum(scene_durations)
    frames_dir = work / "frames"; frames_dir.mkdir(exist_ok=True)
    sentences = [x.strip() for x in narration.replace("?", ".").replace("!", ".").split(".") if x.strip()]
    if not sentences: sentences = [narration]
    # Map caption chunks to scene cards by relative progress.
    for i in range(total_frames):
        t = i / 2
        progress = min(0.999, t / max(duration, 0.1))
        scene_idx = 0
        edge = 0.0
        for j, sd in enumerate(scene_durations):
            edge += sd / total_scene
            if progress < edge:
                scene_idx = j
                break
        sentence_idx = min(len(sentences)-1, int(progress * len(sentences)))
        scene = scenes[scene_idx]
        cap = sentences[sentence_idx]
        make_frame(scene, draft.get("title", "REPWALA"), cap, scene_idx+1, len(scenes), frames_dir / f"frame_{i:05d}.png")
    frames = str(frames_dir / "frame_%05d.png")
    target = out / (src.stem + "-short.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "2", "-i", frames, "-i", str(audio), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(target)], check=True)
    print(f"Video created: {target} ({duration:.1f}s). Draft only; no publishing performed.")
if __name__ == "__main__":
    main()
