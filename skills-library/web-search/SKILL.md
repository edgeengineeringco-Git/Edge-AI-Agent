---
name: web-search
description: Search the live web for current information — model releases, product specs, news, prices, benchmarks, people, companies, or anything that may have changed after your training cutoff. ALWAYS use this BEFORE claiming something doesn't exist, is fictional, or has no public information. Trigger when the user asks "what is X", "does X exist", "compare X and Y", mentions a specific version number or product name, asks about recent releases/prices/news, or when you are uncertain whether something is real. Also trigger on any factual question where getting it wrong has consequences.
---

# Live Web Search

Retrieve current information from the live web. Use this whenever your training data might be stale — especially before telling a user that something "doesn't exist," "isn't a real model/product," or "hasn't been announced."

**The single most important rule:** if you are about to say "X does not exist" or "I don't recognize X" — STOP. Search first. Your knowledge has a cutoff, and new products/models/announcements ship constantly.

## When to search (non-exhaustive)

- User mentions a specific model/product/version name you're not 100% certain about → search
- User asks "what is X" where X could be recent → search
- User asks to compare named products/models/tools → search for each
- User asks about current prices, market data, benchmarks, or news → search
- User says "search" / "look it up" / "live search" → search
- You feel uncertain about whether something exists → search
- The topic is inherently time-sensitive (AI models, stock prices, current events, firmware versions) → search
- User pushes back on a factual claim you made ("do live search you will find") → you missed it the first time; search now

## When NOT to search

- Pure math, code logic, or reasoning tasks where training knowledge is sufficient
- Questions about this project's own files/config (read the files instead)
- The user's question is about concepts that don't change (e.g., "what is DBSCAN")

## Usage

This skill provides a helper script plus manual curl commands. Use the script for convenience, or curl directly for more control.

### 1. Search the web (titles + snippets)

```bash
skills/web-search/search.sh "your search query"
```

Returns titles and snippets from Bing, converted to clean markdown. This is the fastest way to discover what exists.

### 2. Fetch a specific page (full content as markdown)

```bash
skills/web-search/search.sh --fetch https://example.com/article
```

Returns the full page content as clean markdown via the jina.ai reader proxy. Use this after a search to read the most relevant result(s).

### 3. DuckDuckGo fallback (if Bing is rate-limited)

```bash
skills/web-search/search.sh --ddg "your search query"
```

Returns result titles only. Useful when Bing returns nothing.

### 4. Manual curl (full control)

If the script doesn't fit your needs, run curl directly:

```bash
# Bing search via jina.ai reader (no CAPTCHA, good results)
curl -s "https://r.jina.ai/http://www.bing.com/search?q=URL_ENCODED_QUERY"

# DuckDuckGo HTML (extract titles only)
curl -s -A "Mozilla/5.0" "https://html.duckduckgo.com/html/?q=URL_ENCODED_QUERY" \
    | grep -oP '<a[^>]+class="result__a"[^>]*>.*?</a>' \
    | sed 's/<[^>]*>//g'

# Fetch a specific page as markdown
curl -s "https://r.jina.ai/http://example.com/page"
```

## Workflow

1. **Search broadly** — run a search query to discover what exists.
2. **Scan titles/snippets** — identify the 1–3 most relevant results.
3. **Fetch the best page(s)** — use `--fetch` to get full content for the most promising results.
4. **Synthesize** — combine multiple sources, noting which are vendor-reported vs independently measured.
5. **Cite sources** — include URLs so the user can verify.

## Tips

- **Bing via jina.ai is the most reliable** search method — it rarely shows CAPTCHAs. DuckDuckGo HTML works but is sometimes rate-limited.
- **Google will show CAPTCHAs** — avoid it for automated searches.
- **jina.ai reader** (`https://r.jina.ai/http://URL`) converts any web page to clean markdown. Use it to read articles, blog posts, model cards, docs, or GitHub READMEs.
- **URL-encode queries** — spaces become `+` or `%20`, special characters must be encoded.
- **For AI model comparisons**, good sources: Artificial Analysis (artificialanalysis.ai), HuggingFace leaderboards, vendor blogs (z.ai, anthropic.com, openai.com), and tech analysis sites (theairankings.com, codersera.com, venturebeat.com).
- **If a search returns nothing**, try: different phrasing, a different search engine (`--ddg`), or search for the vendor/company name instead of the product.
- **Never fabricate** — if you cannot find something after searching, say so explicitly and show what you searched for. Do NOT fall back to guessing.

## Example: Verifying a model exists

```bash
# User asks "what is Kimi K3?"
# Don't say it doesn't exist — search first:

skills/web-search/search.sh "Kimi K3 Moonshot AI model"

# Read the top result to confirm specs:
skills/web-search/search.sh --fetch https://z.ai/blog/kimi-k3
```

## Example: Comparing models

```bash
# Search for each model, then a comparison query:
skills/web-search/search.sh "Claude Fable 5 Anthropic"
skills/web-search/search.sh "GLM-5.2 Zhipu AI"
skills/web-search/search.sh "Kimi K3 vs Fable 5 vs GLM-5.2 benchmarks"

# Fetch a comparison article for details:
skills/web-search/search.sh --fetch https://codersera.com/blog/kimi-k3-benchmarks-comparison-2026
```
