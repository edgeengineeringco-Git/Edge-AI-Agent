# EDGE Smart Video Agent — LinkedIn Content Creator

This agent produces weekly LinkedIn video content from a topic queue.

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions
- `jobs/weekly-video.md` — Pipeline definition
- `data/topic-queue.md` — Topic queue (populate with upcoming video topics)
- `output/` — Generated weekly video packages

## Pipeline

The weekly pipeline runs every Wednesday at 10:00 AM via CRONS.json. It:
1. Reads the topic queue and selects the next topic to produce
2. Researches the topic for key talking points
3. Writes a 60-90 second video script optimized for LinkedIn
4. Generates post copy, hashtags, thumbnail brief, and engagement prompts
5. Saves the complete video package to `output/YYYY-MM-DD-video-package.md`
6. Marks the topic as completed in the queue

## Topic Queue

Add topics to `data/topic-queue.md` to queue them for production. The agent processes one per week in FIFO order.
