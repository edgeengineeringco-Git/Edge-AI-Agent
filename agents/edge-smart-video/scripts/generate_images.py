#!/usr/bin/env python3
"""
EDGE Smart Video - Image Generation
Generates images for video slides using:
  - Pollinations.ai (free, no key needed)
  - Nano Banana / Gemini API (needs GEMINI_API_KEY in env)

Usage:
  python3 generate_images.py --topic "topic" --sector "sector" --output-dir ./output
  python3 generate_images.py --topic "topic" --sector "sector" --backend nano-banana

Backends:
  pollinations  (default) - Free, no API key needed, variable quality
  nano-banana             - Gemini 2.5 Flash Image, needs GEMINI_API_KEY env var
  nano-banana-2           - Gemini 3.1 Flash Image Preview, needs GEMINI_API_KEY env var
  nano-banana-pro         - Gemini 3 Pro Image, needs GEMINI_API_KEY env var
"""

import urllib.request
import urllib.parse
import json
import sys
import os
import time
import base64


POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

MODEL_MAP = {
    "nano-banana": "gemini-2.5-flash-image",
    "nano-banana-2": "gemini-3.1-flash-image-preview",
    "nano-banana-pro": "gemini-3-pro-image-preview",
}


def gemini_request(model_name, payload, gemini_key):
    """Make a request to the Gemini API with key as query param."""
    url = f"{GEMINI_API_BASE}/models/{model_name}:generateContent?key={gemini_key}"
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def generate_pollinations(prompt, seed, output_path, width=1080, height=1080):
    """Generate image via Pollinations.ai (free, no API key needed)."""
    params = urllib.parse.urlencode({
        "width": width, "height": height,
        "seed": seed, "nologo": "true"
    })
    url = f"{POLLINATIONS_BASE}/{urllib.parse.quote(prompt)}?{params}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; EDGE-Smart-Video/1.0)"}
    )
    with urllib.request.urlopen(req) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type", "")

    ext_map = {
        "image/png": ".png", "image/jpeg": ".jpg",
        "image/jpg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"
    }
    detected_ext = ext_map.get(content_type, ".jpg")

    base_path, _ = os.path.splitext(output_path)
    actual_path = base_path + detected_ext

    with open(actual_path, "wb") as f:
        f.write(data)

    if os.path.getsize(actual_path) < 1000:
        with open(actual_path, "r") as f:
            raise Exception(f"API returned error: {f.read()[:200]}")

    # Also save as .png for downstream compatibility
    if detected_ext != ".png":
        png_path = base_path + ".png"
        if not os.path.exists(png_path):
            import shutil
            shutil.copy2(actual_path, png_path)

    return actual_path


def generate_nano_banana(prompt, seed, output_path, gemini_key, backend="nano-banana"):
    """Generate image via Nano Banana (Gemini API)."""
    model = MODEL_MAP.get(backend, "gemini-2.5-flash-image")

    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "16:9",
                "imageSize": "1080p"
            }
        }
    }

    data = gemini_request(model, payload, gemini_key)

    if "candidates" not in data:
        error = data.get("error", data)
        raise Exception(f"Nano Banana API error: {error}")

    for part in data["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            img_data = base64.b64decode(part["inlineData"]["data"])
            with open(output_path, "wb") as f:
                f.write(img_data)
            return output_path

    raise Exception("No image data in Nano Banana response")


def build_image_prompts(topic, sector):
    """Build image prompts tailored to the topic and sector."""
    return {
        "slide1": f"Professional engineering technology background, {sector} industry, {topic}, sleek dark blue tone, cinematic lighting, photorealistic, 16:9",
        "slide2": f"Infographic technical diagram about {topic} in {sector}, data visualization, dark theme with cyan accents, professional, 16:9",
        "slide3": f"Engineering team working on {topic}, {sector} industry, innovation, modern workplace, professional photography, warm tones, 16:9",
        "cta": f"Abstract technology network background, {sector} concept, global connection, dark theme electric blue accents, minimalist, professional, 16:9"
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate images for EDGE video")
    parser.add_argument("--topic", required=True, help="Video topic")
    parser.add_argument("--sector", required=True, help="Industry sector")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--seed-offset", type=int, default=100, help="Seed offset")
    parser.add_argument("--backend",
                        choices=["pollinations", "nano-banana", "nano-banana-2", "nano-banana-pro"],
                        default="pollinations",
                        help="Image generation backend")
    parser.add_argument("--gemini-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    args = parser.parse_args()

    gemini_key = args.gemini_key or os.environ.get("GEMINI_API_KEY", "")
    os.makedirs(args.output_dir, exist_ok=True)

    prompts = build_image_prompts(args.topic, args.sector)
    results = {}

    for slide_key, prompt in prompts.items():
        seed = abs(args.seed_offset + hash(slide_key)) % 10000 + 1
        output_path = os.path.join(args.output_dir, f"{slide_key}.png")

        print(f"  [{slide_key}] Generating image...")
        sys.stdout.flush()

        try:
            if args.backend.startswith("nano-banana"):
                if not gemini_key:
                    raise Exception("Gemini API key required for nano-banana backend. Set GEMINI_API_KEY env var or pass --gemini-key")
                generate_nano_banana(prompt, seed, output_path, gemini_key, args.backend)
            else:
                generate_pollinations(prompt, seed, output_path)

            results[slide_key] = {"path": output_path, "prompt": prompt, "seed": seed}
            print(f"  \u2713 {slide_key}: {output_path}")
        except Exception as e:
            print(f"  \u2717 {slide_key} failed: {e}", file=sys.stderr)
            results[slide_key] = {"error": str(e)}

        # Rate limit for free API
        if args.backend == "pollinations":
            time.sleep(1.5)

    manifest_path = os.path.join(args.output_dir, "image_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump({
            "topic": args.topic,
            "sector": args.sector,
            "backend": args.backend,
            "slides": results
        }, f, indent=2)

    print(f"\nManifest: {manifest_path}")
    success_count = sum(1 for v in results.values() if "error" not in v)
    print(f"Generated {success_count}/{len(results)} images")

    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
