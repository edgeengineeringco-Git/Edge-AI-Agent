#!/usr/bin/env python3
"""
EDGE Smart Video - Video Composition
Creates video from images + text overlays + optional Veo AI video clip.

Modes:
  1. Shotstack API (free stage tier) - professional compositing with images + text
  2. HTML5 slideshow - always works, no deps needed
  3. Output manifest includes any Veo-generated video clip

Usage:
  python3 compose_video.py --manifest ./output/image_manifest.json --sector "Sector" --topic "Topic"
  python3 compose_video.py --veo-video ./output/veo_video.mp4 --sector "Sector" --topic "Topic"
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import http.client
import html as html_mod


SHOTSTACK_BASE = "api.shotstack.io"
SHOTSTACK_STAGE = "stage"


def build_shotstack_payload(sector, topic, post_text, image_urls, video_url=None):
    """
    Build a Shotstack timeline that uses generated images as background slides
    with text overlays. Optionally includes a Veo video clip as the opening background.
    """
    tracks = []
    bg_color = "#050d17"

    # Determine total duration
    num_slides = sum(1 for v in image_urls.values() if v.get("url"))
    base_duration = max(num_slides, 1) * 3.0  # 3s per slide
    total_duration = max(base_duration, 10.0)

    # Track: Video background (if Veo video URL provided)
    if video_url:
        video_clip = {
            "asset": {
                "type": "video",
                "src": video_url,
                "volume": 0.3
            },
            "start": 0,
            "length": total_duration,
            "transition": {"in": "fade", "out": "fade"}
        }
        tracks.append({
            "clips": [video_clip]
        })

    # Track: Image slides (crossfade between them)
    slide_keys = ["slide1", "slide2", "slide3", "cta"]
    slide_clips = []
    slide_duration = 3.0
    overlap = 0.5

    for i, key in enumerate(slide_keys):
        img_info = image_urls.get(key, {})
        img_url = img_info.get("url", "")
        if not img_url:
            continue

        start = i * (slide_duration - overlap)
        slide_clips.append({
            "asset": {
                "type": "image",
                "src": img_url
            },
            "start": start,
            "length": slide_duration + 0.5,
            "transition": {"in": "fade", "out": "fade"}
        })

    if slide_clips:
        tracks.append({"clips": slide_clips})

    # Track: Sector name (top, slide in)
    sector_clips = [{
        "asset": {
            "type": "html",
            "html": f"<p class='sector'>{html_mod.escape(sector)}</p>",
            "css": (
                "body { margin: 0; padding: 0; background: transparent; "
                "display: flex; align-items: center; justify-content: center; "
                "width: 1920px; height: 100px; } "
                ".sector { font-family: 'Helvetica Neue', Arial, sans-serif; "
                "color: #4fc3c8; font-size: 28px; letter-spacing: 6px; "
                "text-transform: uppercase; text-align: center; "
                "text-shadow: 0 2px 10px rgba(0,0,0,0.8); }"
            ),
            "width": 1920,
            "height": 100
        },
        "position": "top",
        "start": 0.5,
        "length": total_duration - 1,
        "transition": {"in": "slideRight", "out": "fade"}
    }]
    tracks.append({"clips": sector_clips})

    # Track: Topic title (center, zoom in)
    topic_clips = [{
        "asset": {
            "type": "html",
            "html": f"<p class='topic'>{html_mod.escape(topic)}</p>",
            "css": (
                "body { margin: 0; padding: 0; background: transparent; "
                "display: flex; align-items: center; justify-content: center; "
                "width: 1600px; height: 300px; } "
                ".topic { font-family: 'Helvetica Neue', Arial, sans-serif; "
                "color: #ffffff; font-size: 48px; font-weight: bold; "
                "text-align: center; line-height: 1.3; "
                "text-shadow: 0 3px 15px rgba(0,0,0,0.9); }"
            ),
            "width": 1600,
            "height": 300
        },
        "position": "center",
        "start": 1.5,
        "length": total_duration - 2.5,
        "transition": {"in": "zoom", "out": "fade"}
    }]
    tracks.append({"clips": topic_clips})

    # Track: Tagline (center, fade)
    tagline_clips = [{
        "asset": {
            "type": "html",
            "html": "<p class='tagline'>Precision. Innovation. Impact.</p>",
            "css": (
                "body { margin: 0; padding: 0; background: transparent; "
                "display: flex; align-items: center; justify-content: center; "
                "width: 1920px; height: 80px; } "
                ".tagline { font-family: 'Helvetica Neue', Arial, sans-serif; "
                "color: #4fc3c8; font-size: 26px; letter-spacing: 3px; "
                "text-align: center; text-shadow: 0 2px 8px rgba(0,0,0,0.8); }"
            ),
            "width": 1920,
            "height": 80
        },
        "position": "center",
        "offset": {"x": 0, "y": -0.2},
        "start": 3,
        "length": total_duration - 4,
        "transition": {"in": "fade", "out": "fade"}
    }]
    tracks.append({"clips": tagline_clips})

    # Track: CTA url (bottom, slide up)
    cta_clips = [{
        "asset": {
            "type": "html",
            "html": "<p class='cta'>www.edgeengineers.net | ESA Incubatee</p>",
            "css": (
                "body { margin: 0; padding: 0; background: transparent; "
                "display: flex; align-items: center; justify-content: center; "
                "width: 1920px; height: 60px; } "
                ".cta { font-family: 'Helvetica Neue', Arial, sans-serif; "
                "color: #aaaaaa; font-size: 22px; text-align: center; "
                "letter-spacing: 2px; text-shadow: 0 2px 6px rgba(0,0,0,0.7); }"
            ),
            "width": 1920,
            "height": 60
        },
        "position": "bottom",
        "start": max(total_duration - 4, 6),
        "length": 4,
        "transition": {"in": "slideUp"}
    }]
    tracks.append({"clips": cta_clips})

    return {
        "timeline": {
            "background": bg_color,
            "fonts": [
                {"src": "https://templates.shotstack.io/basic/asset/font/quicksand-bold.ttf"}
            ],
            "tracks": tracks
        },
        "output": {
            "format": "mp4",
            "resolution": "hd",
            "fps": 25,
            "size": {"width": 1920, "height": 1080}
        }
    }


def submit_shotstack(payload, api_key):
    """Submit render job to Shotstack stage API."""
    body = json.dumps(payload)
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    conn = http.client.HTTPSConnection(SHOTSTACK_BASE)
    conn.request("POST", f"/{SHOTSTACK_STAGE}/render", body, headers)
    resp = conn.getresponse()
    data = json.loads(resp.read().decode())
    conn.close()

    if not data.get("success"):
        raise Exception(f"Shotstack submission failed: {data.get('message', str(data))}")

    render_id = data["response"]["id"]
    print(f"  Shotstack render ID: {render_id}")
    return render_id


def poll_shotstack(render_id, api_key, max_attempts=60, poll_interval=5):
    """Poll Shotstack for render completion."""
    headers = {"x-api-key": api_key}

    for attempt in range(max_attempts):
        conn = http.client.HTTPSConnection(SHOTSTACK_BASE)
        conn.request("GET", f"/{SHOTSTACK_STAGE}/render/{render_id}", headers=headers)
        resp = conn.getresponse()
        data = json.loads(resp.read().decode())
        conn.close()

        status = data["response"]["status"]
        print(f"  [{attempt+1}/{max_attempts}] Status: {status}")

        if status == "done":
            video_url = data["response"]["url"]
            print(f"  \u2713 Video ready: {video_url}")
            return video_url
        elif status == "failed":
            error = data["response"].get("error", "Unknown error")
            raise Exception(f"Shotstack render failed: {error}")

        time.sleep(poll_interval)

    raise Exception(f"Shotstack render timed out after {max_attempts * poll_interval}s")


def create_html_slideshow(sector, topic, post_text, image_paths, output_dir, veo_video_path=None):
    """Create a self-contained HTML slideshow as video fallback."""
    slides = []
    keys = ["slide1", "slide2", "slide3", "cta"]
    labels = [sector, topic, "Precision. Innovation. Impact.", "www.edgeengineers.net"]
    sub_labels = ["", "", "", "ESA Incubatee"]

    for i, key in enumerate(keys):
        img_info = image_paths.get(key, {})
        img_path = img_info.get("path", "")
        img_data = ""

        if img_path and os.path.exists(img_path):
            try:
                import base64
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                ext = os.path.splitext(img_path)[1][1:] or "png"
                img_data = f"data:image/{ext};base64,{base64.b64encode(img_bytes).decode()}"
            except Exception:
                img_data = ""

        slides.append({
            "image": img_data or "",
            "label": labels[i] if i < len(labels) else "",
            "sub": sub_labels[i] if i < len(sub_labels) else ""
        })

    slides_json = json.dumps(slides)

    veo_html = ""
    if veo_video_path and os.path.exists(veo_video_path):
        try:
            import base64
            with open(veo_video_path, "rb") as f:
                vid_bytes = f.read()
            vid_b64 = base64.b64encode(vid_bytes).decode()
            veo_html = f'''
<div style="margin-bottom:20px;">
  <video controls width="100%" style="border-radius:8px;">
    <source src="data:video/mp4;base64,{vid_b64}" type="video/mp4">
  </video>
</div>'''
        except Exception:
            veo_html = ""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EDGE Video - {html_mod.escape(topic)}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #050d17; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: 'Helvetica Neue', Arial, sans-serif; }}
.player {{ width: 100%; max-width: 854px; aspect-ratio: 16/9; background: #050d17; position: relative; overflow: hidden; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }}
.slide {{ position: absolute; inset: 0; opacity: 0; transition: opacity 0.8s ease-in-out; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.slide.active {{ opacity: 1; }}
.slide .bg {{ position: absolute; inset: 0; background-size: cover; background-position: center; }}
.slide .bg::after {{ content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(5,13,23,0.7) 0%, rgba(5,13,23,0.3) 100%); }}
.slide .label {{ position: relative; z-index: 2; color: #ffffff; font-size: clamp(24px, 5vw, 48px); font-weight: bold; text-align: center; padding: 20px 40px; text-shadow: 0 3px 15px rgba(0,0,0,0.9); max-width: 90%; }}
.slide .sector-label {{ color: #4fc3c8; font-size: clamp(14px, 2.5vw, 28px); letter-spacing: 6px; text-transform: uppercase; margin-bottom: 10px; text-shadow: 0 2px 10px rgba(0,0,0,0.8); }}
.slide .sub {{ color: #aaaaaa; font-size: clamp(12px, 2vw, 22px); letter-spacing: 2px; position: relative; z-index: 2; text-shadow: 0 2px 6px rgba(0,0,0,0.7); }}
.controls {{ position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 10; display: flex; gap: 10px; }}
.dot {{ width: 10px; height: 10px; border-radius: 50%; background: rgba(255,255,255,0.3); cursor: pointer; transition: background 0.3s; }}
.dot.active {{ background: #4fc3c8; }}
.progress {{ position: absolute; bottom: 0; left: 0; height: 3px; background: #4fc3c8; z-index: 10; transition: width 0.3s; }}
.overlay-text {{ position: absolute; bottom: 60px; left: 50%; transform: translateX(-50%); z-index: 5; color: #666; font-size: 12px; letter-spacing: 1px; }}
</style>
</head>
<body>
<div class="player" id="player">
  <div class="progress" id="progress"></div>
  <div id="slides-container"></div>
  <div class="controls" id="controls"></div>
  <div class="overlay-text">www.edgeengineers.net | ESA Incubatee</div>
</div>
<script>
const slides = {slides_json};
let current = 0;
let timer = null;
const DURATION = 4000;

function render() {{
  const container = document.getElementById('slides-container');
  const controls = document.getElementById('controls');
  container.innerHTML = '';
  controls.innerHTML = '';

  slides.forEach((slide, i) => {{
    const div = document.createElement('div');
    div.className = 'slide' + (i === current ? ' active' : '');

    if (slide.image) {{
      const bg = document.createElement('div');
      bg.className = 'bg';
      bg.style.backgroundImage = `url(${{slide.image}})`;
      div.appendChild(bg);
    }}

    if (i === 0 && slide.label) {{
      const sector = document.createElement('div');
      sector.className = 'sector-label';
      sector.textContent = slide.label;
      div.appendChild(sector);
    }} else if (slide.label) {{
      const label = document.createElement('div');
      label.className = 'label';
      label.textContent = slide.label;
      div.appendChild(label);
    }}

    if (slide.sub) {{
      const sub = document.createElement('div');
      sub.className = 'sub';
      sub.textContent = slide.sub;
      div.appendChild(sub);
    }}

    container.appendChild(div);

    const dot = document.createElement('div');
    dot.className = 'dot' + (i === current ? ' active' : '');
    dot.onclick = () => goTo(i);
    controls.appendChild(dot);
  }}
}}

function goTo(i) {{
  current = i;
  render();
  resetTimer();
}}

function next() {{
  current = (current + 1) % slides.length;
  render();
  resetTimer();
}}

function resetTimer() {{
  if (timer) clearInterval(timer);
  timer = setInterval(next, DURATION);
}}

document.getElementById('player').onclick = next;
render();
resetTimer();

let startTime = Date.now();
setInterval(() => {{
  const elapsed = Date.now() - startTime;
  const pct = Math.min((elapsed % (DURATION * slides.length)) / (DURATION * slides.length) * 100, 100);
  document.getElementById('progress').style.width = pct + '%';
}}, 50);
</script>
</body>
</html>"""

    output_path = os.path.join(output_dir, "slideshow.html")
    with open(output_path, "w") as f:
        f.write(html_content)

    print(f"  \u2713 HTML slideshow: {output_path}")

    # Also create a combined view page if Veo video exists
    if veo_video_path and os.path.exists(veo_video_path) and veo_html:
        combined_path = os.path.join(output_dir, "view.html")
        combined_html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>EDGE - {html_mod.escape(topic)}</title>
<style>
body {{ background: #050d17; color: #fff; font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; text-align: center; }}
h1 {{ color: #4fc3c8; font-size: 24px; }}
.section {{ margin: 30px 0; padding: 20px; background: #0a1628; border-radius: 12px; }}
</style>
</head>
<body>
<h1>{html_mod.escape(topic)}</h1>
<p style="color:#888;">{html_mod.escape(sector)}</p>
<div class="section">
<h2>Veo AI Video</h2>
{veo_html}
</div>
<div class="section">
<h2>Branded Slideshow</h2>
<p><a href="slideshow.html" style="color:#4fc3c8;">Open slideshow &rarr;</a></p>
</div>
<div class="section">
<h2>LinkedIn Post</h2>
<pre style="text-align:left; color:#ccc; white-space:pre-wrap; font-size:14px;">{html_mod.escape(post_text)}</pre>
</div>
</body>
</html>"""
        with open(combined_path, "w") as f:
            f.write(combined_html)
        print(f"  \u2713 Combined view: {combined_path}")

    return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compose EDGE video")
    parser.add_argument("--manifest", help="Path to image_manifest.json")
    parser.add_argument("--sector", required=True, help="Industry sector")
    parser.add_argument("--topic", required=True, help="Video topic")
    parser.add_argument("--post-text", default="", help="Generated LinkedIn post text")
    parser.add_argument("--shotstack-key", help="Shotstack API key (or SHOTSTACK_API_KEY env)")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--force-html", action="store_true", help="Skip Shotstack, HTML only")
    parser.add_argument("--veo-video", help="Path to Veo-generated video file")
    parser.add_argument("--veo-prompt", help="Veo video prompt (for reference)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    shotstack_key = args.shotstack_key or os.environ.get("SHOTSTACK_API_KEY", "")

    # Load manifest
    image_paths = {}
    image_urls = {}

    if args.manifest and os.path.exists(args.manifest):
        with open(args.manifest) as f:
            manifest = json.load(f)
            image_paths = manifest.get("slides", {})
            for key, info in image_paths.items():
                path = info.get("path", "")
                if path and os.path.exists(path):
                    image_paths[key] = info

    video_url = None
    html_path = None

    # Build Shotstack payload with images + optional Veo video
    if shotstack_key and not args.force_html:
        print("Attempting Shotstack render...")
        sys.stdout.flush()

        try:
            shotstack_images = {}
            for key in ["slide1", "slide2", "slide3", "cta"]:
                info = image_paths.get(key, {})
                prompt = info.get("prompt", "")
                if prompt:
                    encoded = urllib.parse.quote(prompt)
                    shotstack_images[key] = {
                        "url": f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&nologo=true"
                    }

            payload = build_shotstack_payload(
                args.sector, args.topic, args.post_text,
                shotstack_images, None  # Can't use local Veo video with Shotstack (needs public URL)
            )

            render_id = submit_shotstack(payload, shotstack_key)
            video_url = poll_shotstack(render_id, shotstack_key)
            print(f"  \u2713 Shotstack video: {video_url}")

        except Exception as e:
            print(f"  \u2717 Shotstack failed: {e}")
            print("  Falling back to HTML slideshow...")

    # HTML slideshow (always created as fallback)
    print("Creating HTML slideshow...")
    sys.stdout.flush()

    try:
        html_path = create_html_slideshow(
            args.sector, args.topic, args.post_text,
            image_paths, args.output_dir,
            args.veo_video
        )
    except Exception as e:
        print(f"  \u2717 HTML slideshow failed: {e}")

    # Write results
    result = {
        "topic": args.topic,
        "sector": args.sector,
        "shotstack_video_url": video_url or "",
        "html_slideshow": html_path or "",
        "shotstack_used": video_url is not None,
        "veo_video_path": args.veo_video or "",
        "veo_prompt": args.veo_prompt or ""
    }

    result_path = os.path.join(args.output_dir, "video_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nResult: {result_path}")
    if video_url:
        print(f"  Shotstack video: {video_url}")
    if html_path:
        print(f"  HTML slideshow: {html_path}")
    if args.veo_video:
        print(f"  Veo AI video: {args.veo_video}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
