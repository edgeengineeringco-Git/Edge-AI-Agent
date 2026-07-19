#!/bin/bash
set -euo pipefail

# web-search/search.sh — live web search + page fetch
#
# Usage:
#   search.sh "query"              Search Bing (via jina.ai reader), get titles + snippets
#   search.sh --ddg "query"        Search DuckDuckGo instead (titles only)
#   search.sh --fetch URL          Fetch a specific URL as clean markdown
#   search.sh --news "query"       Search Bing News
#
# Requirements: curl, python3 (for URL encoding)

usage() {
    cat <<'EOF'
Usage: search.sh "query" | --fetch URL | --ddg "query" | --news "query"

  search.sh "Kimi K3 model specs"        → Bing search results
  search.sh --ddg "GLM-5.2 Zhipu"        → DuckDuckGo titles
  search.sh --fetch https://example.com  → Full page as markdown
  search.sh --news "critical minerals"   → Bing News results
EOF
}

if [ $# -eq 0 ]; then
    usage >&2
    exit 1
fi

MODE="bing"
ARG=""

while [ $# -gt 0 ]; do
    case "$1" in
        --fetch) MODE="fetch"; shift; ARG="$1"; shift ;;
        --ddg)   MODE="ddg"; shift; ARG="$1"; shift ;;
        --news)  MODE="news"; shift; ARG="$1"; shift ;;
        -h|--help) usage; exit 0 ;;
        *)       ARG="$1"; shift ;;
    esac
done

if [ -z "$ARG" ]; then
    echo "Error: no query or URL provided" >&2
    usage >&2
    exit 1
fi

# URL-encode the query
encode() {
    python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$1"
}

case "$MODE" in
    fetch)
        # Strip protocol for jina.ai reader
        URL="${ARG#http://}"
        URL="${URL#https://}"
        curl -s --max-time 30 -A "Mozilla/5.0" "https://r.jina.ai/http://${URL}" 2>/dev/null
        ;;

    ddg)
        ENCODED=$(encode "$ARG")
        curl -s --max-time 20 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
            "https://html.duckduckgo.com/html/?q=${ENCODED}" 2>/dev/null \
            | grep -oP '<a[^>]+class="result__a"[^>]*>.*?</a>' \
            | sed 's/<[^>]*>//g' \
            | head -20
        echo ""
        echo "--- (DuckDuckGo HTML results, titles only) ---"
        ;;

    news)
        ENCODED=$(encode "$ARG")
        curl -s --max-time 30 "https://r.jina.ai/http://www.bing.com/news/search?q=${ENCODED}" 2>/dev/null
        ;;

    bing)
        ENCODED=$(encode "$ARG")
        curl -s --max-time 30 "https://r.jina.ai/http://www.bing.com/search?q=${ENCODED}" 2>/dev/null
        ;;
esac
