# EDGE Smart Video — Weekly LinkedIn Video Pipeline

Execute the following pipeline sequentially. Each phase builds on the previous.

## Phase 1: Read the Topic Queue

Read `data/topic-queue.md` and identify the next topic marked as `pending` (the first one in the list). If no pending topics exist, report that the queue is empty and stop.

## Phase 2: Research the Topic

Conduct web research on the selected topic to gather:
- Key facts, statistics, and recent developments
- Industry context and relevance to a professional LinkedIn audience
- Different angles or takes that would make compelling content
- Common misconceptions or questions people have about this topic

## Phase 3: Script Writing

Write a 60-90 second video script with this structure:

- **Hook (0-15s):** A strong opening that grabs attention — surprising stat, provocative question, or bold claim
- **Body (15-60s):** The core insight or explanation. Deliver value quickly. Use plain language — no jargon unless explained.
- **CTA (60-90s):** Clear call to action — ask a question, invite comments, or direct to a resource

Format with timing cues throughout. Target 200-350 spoken words total.

## Phase 4: LinkedIn Post Package

Generate a complete post package:

**Video Title** (60 chars max) — The title that appears on the video

**Post Copy** (1200-1500 chars) — LinkedIn post text that accompanies the video:
- Opening line that stops the scroll
- 2-3 paragraphs expanding on the video's topic
- A question to drive comments
- 3-5 line breaks for readability

**Hashtags** — 3-5 targeted, high-reach hashtags relevant to the topic and a professional audience

**On-Screen Text Overlays** — Key phrases to display as text on screen during specific timestamps

**Thumbnail / Cover Image Brief** — Visual description of an engaging thumbnail (composition, text overlay, color scheme, imagery)

**Engagement Prompts** — 2-3 suggested comments or poll questions to pin

## Phase 5: Save & Deliver

1. Save the complete video package to `output/YYYY-MM-DD-video-package.md`
2. Ensure the package is comprehensive and production-ready
3. Mark the topic in `data/topic-queue.md` as `completed` with the date
