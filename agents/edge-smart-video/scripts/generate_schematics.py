#!/usr/bin/env python3
"""
EDGE Smart Video — Moonshot Kimi Schematic Generator
Generates professional SVG diagrams and info-graphics using Moonshot Kimi API.
SVGs are embedded directly into the HTML video slideshow — no image hosting needed.

Usage:
  python3 generate_schematics.py --slides ./output/slides.json --output-dir ./output

Requires MOONSHOT_API_KEY env var or --moonshot-key argument.
"""

import json
import os
import sys
import urllib.request
import urllib.error

MOONSHOT_BASE = "https://api.moonshot.ai/v1"


BRAND_COLORS = {
    "bg": "#f0f4f0",
    "surface": "#ffffff",
    "primary": "#1a7a3a",
    "primary_dim": "#145c2d",
    "text": "#1e293b",
    "text_dim": "#64748b",
    "accent": "#d97706",
    "light_green": "#d1e7d6",
    "lighter_green": "#e8f4ec"
}


def moonshot_chat(messages, api_key, model="kimi-k2.6", max_tokens=4096):
    """Call the Moonshot chat completion API (OpenAI-compatible)."""
    url = f"{MOONSHOT_BASE}/chat/completions"
    # kimi-k2 models only accept temperature=1
    temp = 1.0 if model.startswith("kimi-k2") else 0.3
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temp
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
        return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f"Moonshot API error ({e.code}): {error_body[:300]}")


def build_svg_prompt(slide, topic, sector, brand):
    """Build a prompt for generating an SVG schematic for this slide."""
    slide_type = slide.get("type", "content")
    headline = slide.get("headline", "")
    bullets = slide.get("bullets", [])

    if slide_type == "title":
        return f"""You are an EDGE Engineers brand designer. Create a professional SVG hero graphic for a video slide.

Topic: {topic}
Sector: {sector}
Headline: {headline}

Requirements:
- Clean, minimal, professional design — suitable for a LinkedIn corporate video
- Use this exact color palette:
  - Background: {brand['bg']} (light green-gray)
  - Primary: {brand['primary']} (deep green)
  - Text: {brand['text']} (dark slate)
  - Accent: {brand['accent']} (amber)
  - Light green: {brand['light_green']}
- Width: 600px, Height: 400px
- Abstract geometric shapes, a subtle icon or symbol representing {sector} or {topic}
- NO text in the SVG (text will be overlaid by the video player)
- Use viewBox="0 0 600 400"
- Return ONLY the raw SVG markup, no markdown fences, no explanation."""

    elif slide_type == "cta":
        return f"""You are an EDGE Engineers brand designer. Create a professional SVG background graphic for a call-to-action slide.

Topic: {topic}
Sector: {sector}

Requirements:
- Clean, minimal, professional design
- Use this exact color palette:
  - Background: {brand['surface']} (white)
  - Primary: {brand['primary']} (deep green)
  - Light green: {brand['light_green']}
- Width: 600px, Height: 400px
- Abstract upward-trending shapes, arrows or growth motifs
- NO text in the SVG
- Use viewBox="0 0 600 400"
- Return ONLY the raw SVG markup, no markdown fences, no explanation."""

    else:
        # Content slide — generate a diagram illustrating the bullet points
        bullets_text = "\n".join(f"- {b}" for b in bullets)
        return f"""You are an EDGE Engineers technical illustrator. Create a professional SVG diagram illustrating this content.

Topic: {topic}
Sector: {sector}
Headline: {headline}
Key points:
{bullets_text}

Requirements:
- Professional technical diagram, flowchart, comparison chart, or info-graphic
- Make it visually illustrate the CONCEPT behind the headline — not generic decoration
- Use this exact color palette:
  - Background: transparent
  - Primary: {brand['primary']} (deep green #1a7a3a)
  - Primary dim: {brand['primary_dim']} (#145c2d)
  - Text: {brand['text']} (#1e293b, dark slate)
  - Text dim: {brand['text_dim']} (#64748b, medium gray)
  - Accent: {brand['accent']} (#d97706, amber)
  - Light green: {brand['light_green']} (#d1e7d6)
  - Lighter green: {brand['lighter_green']} (#e8f4ec)
- Width: 500px, Height: 340px
- Include brief labels where helpful
- Use viewBox="0 0 500 340"
- Return ONLY the raw SVG markup, no markdown fences, no explanation."""


def generate_schematic(slide, topic, sector, api_key, model="kimi-k2.6"):
    """Generate an SVG schematic for a single slide."""
    prompt = build_svg_prompt(slide, topic, sector, BRAND_COLORS)
    messages = [
        {
            "role": "system",
            "content": "You are a professional technical illustrator. You generate clean, modern SVG diagrams. You always return ONLY valid SVG markup with no markdown formatting, no code fences, no explanation."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    svg = moonshot_chat(messages, api_key, model).strip()

    # Strip markdown code fences if present
    if svg.startswith("```"):
        lines = svg.split("\n")
        svg = "\n".join(lines[1:] if "svg" in lines[0].lower() else lines[1:])
        if svg.endswith("```"):
            svg = svg[:-3].strip()
    if svg.startswith("```"):
        svg = svg.replace("```svg", "").replace("```", "").strip()

    return svg


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate SVG schematics via Moonshot Kimi")
    parser.add_argument("--slides", required=True, help="Path to slides.json")
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--topic", required=True, help="Video topic")
    parser.add_argument("--sector", required=True, help="Industry sector")
    parser.add_argument("--moonshot-key", help="Moonshot API key (or MOONSHOT_API_KEY env)")
    parser.add_argument("--model", default="kimi-k2.6",
                        choices=["kimi-k2.6", "kimi-k2.5", "moonshot-v1-auto",
                                 "moonshot-v1-128k", "moonshot-v1-128k-vision-preview"],
                        help="Moonshot model")
    args = parser.parse_args()

    api_key = args.moonshot_key or os.environ.get("MOONSHOT_API_KEY", "")
    if not api_key:
        print("ERROR: MOONSHOT_API_KEY required. Set env var or pass --moonshot-key", file=sys.stderr)
        return 1

    if not os.path.exists(args.slides):
        print(f"ERROR: Slides file not found: {args.slides}", file=sys.stderr)
        return 1

    with open(args.slides) as f:
        slides = json.load(f)

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Generating {len(slides)} SVG schematics via Moonshot {args.model}...")
    sys.stdout.flush()

    schematics = []
    for i, slide in enumerate(slides):
        slide_type = slide.get("type", "content")
        headline = slide.get("headline", f"Slide {i+1}")
        print(f"  [{i+1}/{len(slides)}] {slide_type}: {headline[:50]}...")
        sys.stdout.flush()

        svg = None
        last_error = None
        for attempt in range(1, 3):  # up to 2 attempts
            try:
                svg = generate_schematic(slide, args.topic, args.sector, api_key, args.model)
                if svg and len(svg.strip()) > 100:
                    print(f"    Generated SVG ({len(svg)} chars)")
                    break
                else:
                    print(f"    Attempt {attempt}: empty/short SVG, retrying...")
                    svg = None
            except Exception as e:
                last_error = str(e)
                print(f"    Attempt {attempt} failed: {e}", file=sys.stderr)
                svg = None

        schematics.append({
            "slide_index": i,
            "slide_type": slide_type,
            "headline": headline,
            "svg": svg,
            **({"error": last_error} if svg is None and last_error else {})
        })
        sys.stdout.flush()

    # Save schematics manifest
    manifest_path = os.path.join(args.output_dir, "schematics.json")
    with open(manifest_path, "w") as f:
        json.dump(schematics, f, indent=2)
    print(f"\n  Saved schematics: {manifest_path}")

    success_count = sum(1 for s in schematics if s.get("svg"))
    print(f"  Generated: {success_count}/{len(slides)} schematics")

    return 0


if __name__ == "__main__":
    sys.exit(main())
