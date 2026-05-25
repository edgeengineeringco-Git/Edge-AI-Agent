#!/usr/bin/env python3
"""
EDGE Smart Video - Veo 3.1 Video Generation
Generates short AI video clips via Google Veo 3.1 API.

Usage:
  python3 generate_video.py --prompt "Cinematic drone shot..." --output-dir ./output

Requires GEMINI_API_KEY env var or --gemini-key argument.

Veo models:
  veo-3.1-generate-preview      - Standard (default)
  veo-3.1-fast-generate-preview - Faster, lower quality
  veo-3.1-lite-generate-preview - Cost-effective Lite
"""

import urllib.request
import json
import sys
import os
import time
import base64

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


def gemini_post(url, payload, api_key):
    """POST to Gemini API with key as query param."""
    full_url = f"{url}?key={api_key}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        full_url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def gemini_get(url, api_key):
    """GET from Gemini API."""
    full_url = f"{url}?key={api_key}"
    req = urllib.request.Request(full_url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def generate_video(prompt, api_key, model="veo-3.1-generate-preview",
                   duration=5, aspect_ratio="16:9", max_poll_secs=300):
    """
    Generate a video using Veo 3.1.
    Returns dict with video bytes, mime type, and metadata.
    """
    submit_url = f"{GEMINI_API_BASE}/models/{model}:generateVideos"

    body = {
        "prompt": prompt,
        "numberOfVideos": 1,
        "durationSeconds": duration,
        "aspectRatio": aspect_ratio,
        "enhancePrompt": True
    }

    print(f"  Submitting Veo job (model={model}, duration={duration}s)...")
    sys.stdout.flush()

    try:
        result = gemini_post(submit_url, body, api_key)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f"Veo API error ({e.code}): {error_body[:300]}")

    # Handle response - should return an operation
    operation_name = result.get("name", "")
    if not operation_name:
        # Maybe the result is directly an operation
        if "error" in result:
            raise Exception(f"Veo API error: {result['error']}")

        # Check if video is already in the response
        if "generatedVideos" in result:
            return _extract_video(result)

        operation_name = result.get("operation", result.get("name", ""))
        if not operation_name:
            # Try to find any operation-like field
            for key in result:
                if "operation" in key.lower() or key == "name":
                    operation_name = result[key]
                    break

    if not operation_name:
        # Print the response for debugging
        print(f"  Response keys: {list(result.keys())}", file=sys.stderr)
        raise Exception(f"Could not get operation name from response. Keys: {list(result.keys())}")

    print(f"  Operation: {operation_name}")
    sys.stdout.flush()

    # Poll for completion
    poll_url = f"{GEMINI_API_BASE}/{operation_name}"
    deadline = time.time() + max_poll_secs

    while time.time() < deadline:
        time.sleep(15)
        status = gemini_get(poll_url, api_key)
        done = status.get("done", False)

        if done:
            response = status.get("response", status)
            if "generatedVideos" in response:
                return _extract_video(response)
            elif "error" in status:
                raise Exception(f"Veo generation failed: {status['error']}")
            else:
                print(f"  Done but unexpected format: {list(response.keys())}", file=sys.stderr)
                # Try direct result
                return _extract_video(status)

        print(f"  Still rendering... ({int(time.time() - (deadline - max_poll_secs))}s elapsed)")
        sys.stdout.flush()

    raise Exception(f"Veo timed out after {max_poll_secs}s")


def _extract_video(response):
    """Extract video data from Veo response."""
    videos = response.get("generatedVideos", [])
    if not videos:
        raise Exception(f"No videos in response. Keys: {list(response.keys())}")

    video = videos[0]
    video_data = video.get("video", video)

    # Video can be inline (base64) or a URI
    if "data" in video_data:
        raw = base64.b64decode(video_data["data"])
        mime = video_data.get("mimeType", "video/mp4")
        return {"bytes": raw, "mime": mime}
    elif "uri" in video_data or "url" in video_data:
        url = video_data.get("uri", video_data.get("url", ""))
        print(f"  Downloading from: {url[:80]}...")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
        return {"bytes": raw, "mime": video_data.get("mimeType", "video/mp4")}
    elif "inlineData" in video_data:
        raw = base64.b64decode(video_data["inlineData"]["data"])
        mime = video_data["inlineData"].get("mimeType", "video/mp4")
        return {"bytes": raw, "mime": mime}
    else:
        # Maybe the video data is flat in the response
        for part_key in ["video", "data", "content", "videoData"]:
            if part_key in video_data:
                raw = base64.b64decode(video_data[part_key]) if isinstance(video_data[part_key], str) else video_data[part_key]
                return {"bytes": raw if isinstance(raw, bytes) else raw.encode(), "mime": "video/mp4"}

        raise Exception(f"Unknown video format. Keys: {list(video.keys())}")


def build_video_prompt(topic, sector, post_text=""):
    """Build a video prompt tailored to the topic."""
    return (
        f"Cinematic aerial drone shot of a {sector} engineering site, "
        f"showcasing {topic}. Professional industrial setting, "
        f"golden hour lighting, slow camera pan, high-end production quality. "
        f"Modern technology equipment visible, professional team in background. "
        f"Clean, polished, suitable for LinkedIn corporate content."
    )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate video via Veo 3.1")
    parser.add_argument("--prompt", help="Video description prompt (default: auto-built)")
    parser.add_argument("--topic", help="Topic (used with --sector to auto-build prompt)")
    parser.add_argument("--sector", help="Industry sector")
    parser.add_argument("--model", default="veo-3.1-generate-preview",
                        choices=["veo-3.1-generate-preview",
                                 "veo-3.1-fast-generate-preview",
                                 "veo-3.1-lite-generate-preview"],
                        help="Veo model")
    parser.add_argument("--duration", type=int, default=5, choices=[4, 5, 6, 8],
                        help="Video duration in seconds")
    parser.add_argument("--aspect-ratio", default="16:9", choices=["16:9", "9:16", "1:1"])
    parser.add_argument("--output-dir", default="./output")
    parser.add_argument("--gemini-key", help="Gemini API key (or GEMINI_API_KEY env var)")
    parser.add_argument("--post-text", default="", help="Generated post text for context")
    args = parser.parse_args()

    gemini_key = args.gemini_key or os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY required. Set env var or pass --gemini-key", file=sys.stderr)
        return 1

    # Build prompt if not provided
    prompt = args.prompt
    if not prompt:
        if args.topic and args.sector:
            prompt = build_video_prompt(args.topic, args.sector, args.post_text)
        else:
            print("ERROR: Provide --prompt or both --topic and --sector", file=sys.stderr)
            return 1

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Generating Veo video...")
    print(f"  Model: {args.model}")
    print(f"  Duration: {args.duration}s")
    print(f"  Prompt: {prompt[:120]}...")
    sys.stdout.flush()

    try:
        result = generate_video(
            prompt=prompt,
            api_key=gemini_key,
            model=args.model,
            duration=args.duration,
            aspect_ratio=args.aspect_ratio
        )

        ext = "mp4"
        if "webm" in result["mime"]:
            ext = "webm"

        output_path = os.path.join(args.output_dir, f"veo_video.{ext}")
        with open(output_path, "wb") as f:
            f.write(result["bytes"])

        print(f"  \u2713 Video saved: {output_path} ({len(result['bytes'])} bytes, {result['mime']})")

        # Write result manifest
        manifest = {
            "prompt": prompt,
            "model": args.model,
            "duration": args.duration,
            "video_path": output_path,
            "video_size": len(result["bytes"]),
            "mime_type": result["mime"],
            "status": "completed"
        }
        manifest_path = os.path.join(args.output_dir, "veo_result.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"  \u2713 Manifest: {manifest_path}")

        return 0

    except Exception as e:
        print(f"  \u2717 Video generation failed: {e}", file=sys.stderr)
        manifest = {"prompt": prompt, "model": args.model, "status": "failed", "error": str(e)}
        with open(os.path.join(args.output_dir, "veo_result.json"), "w") as f:
            json.dump(manifest, f, indent=2)
        return 1


if __name__ == "__main__":
    sys.exit(main())
