#!/usr/bin/env python3
"""
EDGE Smart Video - Image Generation
Generates images for video slides using Pollinations.ai (free) or Nano Banana (Gemini API).
Saves locally and returns URLs for video compositing.

Usage:
  python3 generate_images.py --topic "topic" --sector "sector" --output-dir ./output

Optional:
  --seed-offset N    Offset for random seeds (default: 100)
  --backend          Image backend: pollinations (default) or nano-banana
  --gemini-key KEY   Gemini API key for Nano Banana backend
"""

import urllib.request
import urllib.parse
import json
import sys
import os
import time

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"

def generate_pollinations(prompt, seed, output_path, width=1080, height=1080):
    """Generate image via Pollinations.ai (free, no API key needed)."""
    # Ensure output path has correct extension based on response content type
    params = urllib.parse.urlencode({
        "width": width,
        "height": height,
        "seed": seed,
        "nologo": "true"
    })
    url = f"{POLLINATIONS_BASE}/{urllib.parse.quote(prompt)}?{params}"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; EDGE-Smart-Video/1.0)"}
        )
        with urllib.request.urlopen(req) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "")

            # Detect actual format from Content-Type
            ext_map = {
                "image/png": ".png",
                "image/jpeg": ".jpg",
                "image/jpg": ".jpg",
                "image/webp": ".webp",
                "image/gif": ".gif"
            }
            detected_ext = ext_map.get(content_type, ".jpg")

            # Fix output path extension if needed
            base, _ = os.path.splitext(output_path)
            actual_path = base + detected_ext

            with open(actual_path, 'wb') as f:
                f.write(data)

        file_size = os.path.getsize(actual_path)
        if file_size < 1000:  # Too small = likely an error
            with open(actual_path, 'r') as f:
                content = f.read()
            raise Exception(f"Pollinations returned error: {content[:200]}")

        # If extension changed, also save as .png for downstream compatibility
        if detected_ext != ".png":
            png_path = base + ".png"
            if not os.path.exists(png_path):
                import shutil
                shutil.copy2(actual_path, png_path)

        return actual_path
    except Exception as e:
        raise Exception(f"Failed to generate image (seed={seed}): {e}")


def generate_nano_banana(prompt, seed, output_path, gemini_key):
    """Generate image via Nano Banana (Gemini API - better quality, needs API key)."""
    import http.client
    import base64

    model = "gemini-2.5-flash-image"
    url_path = f"/v1beta/models/{model}:generateContent"

    payload = json.dumps({
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "16:9",
                "imageSize": "2K"
            }
        }
    })

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {gemini_key}"
    }

    conn = http.client.HTTPSConnection("generativelanguage.googleapis.com")

    try:
        conn.request("POST", url_path, payload, headers)
        resp = conn.getresponse()
        data = json.loads(resp.read().decode())
        conn.close()

        if "candidates" not in data:
            raise Exception(f"Nano Banana API error: {json.dumps(data.get('error', data))}")

        for part in data["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                img_data = base64.b64decode(part["inlineData"]["data"])
                with open(output_path, "wb") as f:
                    f.write(img_data)
                return output_path

        raise Exception("No image data in Nano Banana response")
    except Exception as e:
        raise Exception(f"Nano Banana generation failed: {e}")


def build_image_prompts(topic, sector):
    """Build image prompts tailored to the topic and sector."""
    return {
        "slide1": f"Professional engineering technology background, {sector} industry, {topic}, sleek dark blue tone, cinematic lighting, photorealistic, 4k",
        "slide2": f"Infographic style illustration about {topic} in {sector}, data visualization, technical diagram, professional presentation style, dark theme with cyan accents",
        "slide3": f"Engineering team working on {topic} technology, {sector} industry, innovation, modern workplace, professional photography style, warm lighting",
        "cta": f"Abstract technology network background, {sector} industry concept, global connection, dark theme with electric blue accents, minimalist, professional"
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate images for EDGE video")
    parser.add_argument("--topic", required=True, help="Video topic")
    parser.add_argument("--sector", required=True, help="Industry sector")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--seed-offset", type=int, default=100, help="Seed offset")
    parser.add_argument("--backend", choices=["pollinations", "nano-banana"], default="pollinations",
                        help="Image generation backend")
    parser.add_argument("--gemini-key", help="Gemini API key (required for nano-banana)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    prompts = build_image_prompts(args.topic, args.sector)
    results = {}

    for slide_key, prompt in prompts.items():
        seed = args.seed_offset + hash(slide_key) % 10000
        output_path = os.path.join(args.output_dir, f"{slide_key}.png")

        print(f"  [{slide_key}] Generating image...")
        sys.stdout.flush()

        try:
            if args.backend == "nano-banana":
                if not args.gemini_key:
                    raise Exception("Gemini API key required for nano-banana backend")
                generate_nano_banana(prompt, seed, output_path, args.gemini_key)
            else:
                generate_pollinations(prompt, seed, output_path)

            results[slide_key] = {
                "path": output_path,
                "prompt": prompt,
                "seed": seed
            }
            print(f"  ✓ {slide_key}: {output_path}")
        except Exception as e:
            print(f"  ✗ {slide_key} failed: {e}", file=sys.stderr)
            results[slide_key] = {"error": str(e)}

        # Rate limit for free API
        if args.backend == "pollinations":
            time.sleep(1.5)

    # Write manifest
    manifest_path = os.path.join(args.output_dir, "image_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump({
            "topic": args.topic,
            "sector": args.sector,
            "backend": args.backend,
            "slides": results
        }, f, indent=2)

    print(f"\nManifest: {manifest_path}")

    # Count successes
    success_count = sum(1 for v in results.values() if "error" not in v)
    print(f"Generated {success_count}/{len(results)} images")

    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
