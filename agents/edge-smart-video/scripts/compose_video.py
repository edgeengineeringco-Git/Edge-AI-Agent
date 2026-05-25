#!/usr/bin/env python3
"""
EDGE Smart Video - Video Composition
Creates video from images + text overlays.
Primary: Shotstack API (free stage tier)
Fallback: HTML5 slideshow page

Usage:
  python3 compose_video.py --manifest ./output/image_manifest.json --sector "Sector" --topic "Topic" --post-text "Post text"

  --shotstack-key KEY   Shotstack API key (uses stage API for free tier)
  --output-dir DIR      Output directory (default: ./output)
  --force-html          Skip Shotstack, create HTML only
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


def build_shotstack_payload(sector, topic, post_text, image_urls, logo_url=None):
    """
    Build a Shotstack timeline that actually uses the generated images
    as background slides with text overlays.
    """
    images = image_urls  # dict with keys: slide1, slide2, slide3, cta

    # Default URLs if images are missing
    bg_color = "#050d17"

    tracks = []

    # Track 1: Background slides with crossfade
    slide_clips = []
    slide_duration = 3.0
    slide_overlap = 0.5  # crossfade overlap

    slide_keys = ["slide1", "slide2", "slide3", "cta"]
    for i, key in enumerate(slide_keys):
        img_url = images.get(key, {}).get("url", "")
        start = i * (slide_duration - slide_overlap)

        clip = {
            "asset": {
                "type": "image",
                "src": img_url
            } if img_url else {
                "type": "title",
                "text": " ",
            },
            "start": start,
            "length": slide_duration + 0.5,
            "transition": {
                "in": "fade",
                "out": "fade"
            }
        }

        # Only add image-based clip if we have a URL
        if img_url:
            clip["asset"] = {
                "type": "image",
                "src": img_url
            }
            slide_clips.append(clip)

    if slide_clips:
        tracks.append({
            "clips": slide_clips
        })

    # Track 2: Sector name overlay (top, slide in)
    sector_clips = []
    for i, key in enumerate(["slide1"]):
        start = 0.5
        sector_clips.append({
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
            "start": start,
            "length": 8,
            "transition": {"in": "slideRight", "out": "fade"}
        })

    if sector_clips:
        tracks.append({"clips": sector_clips})

    # Track 3: Topic title overlay (center, zoom in)
    topic_clips = []
    for i in range(1):
        start = 1.0
        topic_clips.append({
            "asset": {
                "type": "html",
                "html": f"<p class='topic'>{html_mod.escape(topic)}</p>",
                "css": (
                    "body { margin: 0; padding: 0; background: transparent; "
                    "display: flex; align-items: center; justify-content: center; "
                    "width: 1600px; height: 300px; } "
                    ".topic { font-family: 'Helvetica Neue', Arial, sans-serif; "
                    "color: #ffffff; font-size: 52px; font-weight: bold; "
                    "text-align: center; line-height: 1.3; "
                    "text-shadow: 0 3px 15px rgba(0,0,0,0.9); }"
                ),
                "width": 1600,
                "height": 300
            },
            "position": "center",
            "start": start,
            "length": 7,
            "transition": {"in": "zoom", "out": "fade"}
        })

    if topic_clips:
        tracks.append({"clips": topic_clips})

    # Track 4: Tagline (center, fade)
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
        "length": 5,
        "transition": {"in": "fade", "out": "fade"}
    }]
    tracks.append({"clips": tagline_clips})

    # Track 5: Logo overlay (top-right, subtle)
    if logo_url:
        logo_clips = [{
            "asset": {
                "type": "image",
                "src": logo_url
            },
            "position": {
                "x": 0.9,  # right side
                "y": 0.1   # top
            },
            "start": 0,
            "length": 10,
            "transition": {"in": "fade"}
        }]
        tracks.append({"clips": logo_clips})

    # Track 6: CTA url (bottom, slide up)
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
        "start": 6,
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
    import json as json_mod

    body = json_mod.dumps(payload)
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    conn = http.client.HTTPSConnection(SHOTSTACK_BASE)

    try:
        conn.request("POST", f"/{SHOTSTACK_STAGE}/render", body, headers)
        resp = conn.getresponse()
        data = json_mod.loads(resp.read().decode())
        conn.close()

        if not data.get("success"):
            error_msg = data.get("message", str(data))
            raise Exception(f"Shotstack submission failed: {error_msg}")

        render_id = data["response"]["id"]
        print(f"  Shotstack render ID: {render_id}")
        return render_id
    except http.client.HTTPException as e:
        raise Exception(f"Shotstack HTTP error: {e}")


def poll_shotstack(render_id, api_key, max_attempts=60, poll_interval=5):
    """Poll Shotstack for render completion."""
    import json as json_mod

    headers = {"x-api-key": api_key}

    for attempt in range(max_attempts):
        conn = http.client.HTTPSConnection(SHOTSTACK_BASE)
        try:
            conn.request("GET", f"/{SHOTSTACK_STAGE}/render/{render_id}", headers=headers)
            resp = conn.getresponse()
            data = json_mod.loads(resp.read().decode())
            conn.close()

            status = data["response"]["status"]
            print(f"  [{attempt+1}/{max_attempts}] Status: {status}")

            if status == "done":
                video_url = data["response"]["url"]
                print(f"  ✓ Video ready: {video_url}")
                return video_url
            elif status == "failed":
                error = data["response"].get("error", "Unknown error")
                raise Exception(f"Shotstack render failed: {error}")

            time.sleep(poll_interval)
        except http.client.HTTPException as e:
            # Retry on transient error
            if attempt < max_attempts - 1:
                time.sleep(poll_interval)
                continue
            raise Exception(f"Shotstack poll failed: {e}")

    raise Exception(f"Shotstack render timed out after {max_attempts * poll_interval}s")


def create_html_slideshow(sector, topic, post_text, image_paths, output_dir):
    """
    Create a self-contained HTML slideshow as video fallback.
    This produces a playable HTML page with auto-advancing slides.
    """
    slides = []
    keys = ["slide1", "slide2", "slide3", "cta"]
    labels = [sector, topic, "Precision. Innovation. Impact.", "www.edgeengineers.net"]
    sub_labels = ["", "", "", "ESA Incubatee"]

    for i, key in enumerate(keys):
        img_info = image_paths.get(key, {})
        img_path = img_info.get("path", "")
        img_data = ""

        # Try to embed image as base64 data URI
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

    # Build HTML
    slides_json = json.dumps(slides)

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
.slide .label {{ position: relative; z-index: 2; color: #ffffff; font-size: clamp(24px, 5vw, 52px); font-weight: bold; text-align: center; padding: 20px 40px; text-shadow: 0 3px 15px rgba(0,0,0,0.9); max-width: 90%; }}
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

// Progress bar
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

    print(f"  ✓ HTML slideshow: {output_path}")
    return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compose EDGE video")
    parser.add_argument("--manifest", help="Path to image_manifest.json")
    parser.add_argument("--sector", required=True, help="Industry sector")
    parser.add_argument("--topic", required=True, help="Video topic")
    parser.add_argument("--post-text", default="", help="Generated LinkedIn post text")
    parser.add_argument("--shotstack-key", help="Shotstack API key")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--force-html", action="store_true", help="Skip Shotstack, HTML only")
    parser.add_argument("--logo-url", default="", help="Logo image URL")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Load manifest
    image_paths = {}
    image_urls = {}

    if args.manifest and os.path.exists(args.manifest):
        with open(args.manifest) as f:
            manifest = json.load(f)
            image_paths = manifest.get("slides", {})
            # Build URLs - if we have local paths, we can't use them directly with Shotstack
            # For the manifest, we store URLs from Pollinations
            for key, info in image_paths.items():
                path = info.get("path", "")
                if path and os.path.exists(path):
                    image_paths[key] = info
                    image_urls[key] = info  # May contain URL if available

    # Video URL placeholder
    video_url = None
    html_path = None

    # Try Shotstack first
    if args.shotstack_key and not args.force_html:
        print("Attempting Shotstack video render...")
        sys.stdout.flush()

        try:
            # For Shotstack, images need to be publicly accessible URLs
            # Pollinations images are already served from their CDN
            # If we downloaded them locally, we'll use the original prompt URLs
            shotstack_images = {}
            for key in ["slide1", "slide2", "slide3", "cta"]:
                info = image_paths.get(key, {})
                # We need public URLs - Pollinations URLs are the prompts we sent
                # Rebuild the URL from the prompt if available
                prompt = info.get("prompt", "")
                if prompt:
                    encoded = urllib.parse.quote(prompt)
                    shotstack_images[key] = {
                        "url": f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&nologo=true"
                    }
                elif "path" in info and os.path.exists(info["path"]):
                    print(f"  ⚠ Local image {key} can't be used with Shotstack (no public URL)")

            payload = build_shotstack_payload(
                args.sector, args.topic, args.post_text,
                shotstack_images, args.logo_url
            )

            render_id = submit_shotstack(payload, args.shotstack_key)
            video_url = poll_shotstack(render_id, args.shotstack_key)
            print(f"  ✓ Video: {video_url}")

        except Exception as e:
            print(f"  ✗ Shotstack failed: {e}")
            print("  Falling back to HTML slideshow...")
            video_url = None

    # Fallback: HTML slideshow
    if not video_url:
        print("Creating HTML slideshow...")
        sys.stdout.flush()
        try:
            html_path = create_html_slideshow(
                args.sector, args.topic, args.post_text,
                image_paths, args.output_dir
            )
        except Exception as e:
            print(f"  ✗ HTML slideshow failed: {e}")

    # Write results
    result = {
        "topic": args.topic,
        "sector": args.sector,
        "video_url": video_url or "",
        "html_slideshow": html_path or "",
        "shotstack_used": video_url is not None
    }

    result_path = os.path.join(args.output_dir, "video_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nResult: {result_path}")
    if video_url:
        print(f"Video URL: {video_url}")
    if html_path:
        print(f"HTML slideshow: {html_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
