---
name: web-search-intel
description: Live web search, patent monitoring, commodity price fetching, and regulatory/policy tracking for critical minerals exploration. Uses Serper.dev, Brave Search API, or RSS feeds.
---

# Live Intelligence and Web Search

## When to use

- You need current REE commodity prices for economic assessments.
- You want to monitor new patents, papers, or policy changes affecting critical minerals.
- You need to research a new tenement area (geology, previous explorers, infrastructure).
- You want alerts on competitor activity, funding rounds, or JV announcements.

## APIs and Data Sources

### Search APIs
| Service | Free Tier | Paid | Best For |
|---|---|---|---|
| **Serper.dev** | 2,500 queries/mo | $50/50k queries | Google search results, structured JSON |
| **Brave Search API** | 2,000 queries/mo | $3/1000 queries | Privacy-focused, fast |
| **Google Custom Search** | 100 queries/day | $5/1000 queries | Programmatic Google |
| **SearXNG** | Self-hosted | Free | Meta-search, no API limits |

### Commodity Price APIs
| Source | Data | Access |
|---|---|---|
| **Fastmarkets** | REE oxide prices | Subscription |
| **Asian Metal** | Chinese REE prices | Subscription |
| **USGS Mineral Commodity Summaries** | Annual, free | PDF/CSV download |
| **Trading Economics** | Historical prices | API + free tier |
| **UN Comtrade** | Trade flows | Free API |
| **World Bank Commodity Price Data** | Monthly indices | Free CSV |

### Patent / Literature
| Source | API | Notes |
|---|---|---|
| **USPTO Patent Public Search** | REST API | US patents |
| **EPO Open Patent Services** | REST API | European patents |
| **Google Patents Public Datasets** | BigQuery | Free, massive dataset |
| **CrossRef / OpenAlex** | REST API | Academic papers |
| **arXiv API** | REST API | Preprints |
| **GeoScienceWorld** | Web scrape | Geology journals |

## Python Implementation

### Serper.dev Search
```python
import requests
import json
import os

SERPER_API_KEY = os.getenv('SERPER_API_KEY')

def search_web(query, num=10, tbs=None):
    """
    Search web via Serper.dev
    tbs: time filter e.g. 'qdr:w' (past week), 'qdr:m' (past month)
    """
    url = "https://google.serper.dev/search"
    payload = {
        "q": query,
        "num": num,
    }
    if tbs:
        payload["tbs"] = tbs
    
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Example queries for REE intel
queries = [
    "rare earth elements price 2026 dysprosium terbium",
    "critical minerals exploration funding Africa 2026",
    "new REE deposit discovery 2026",
    "China rare earth export policy 2026",
    "USGS critical minerals list update",
]

for q in queries:
    results = search_web(q, num=5, tbs='qdr:w')
    for r in results.get('organic', []):
        print(f"[{r['title']}] {r['link']}\n{r['snippet'][:200]}...")
```

### Commodity Price Fetcher
```python
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_ree_prices_trading_economics():
    """
    Fetch REE-related commodity data from Trading Economics
    """
    symbols = {
        'Neodymium': 'neodymium',
        'Dysprosium': 'dysprosium',
        'Lanthanum': 'lanthanum',
        'Cerium': 'cerium'
    }
    
    prices = {}
    for name, symbol in symbols.items():
        url = f"https://tradingeconomics.com/commodity/{symbol}"
        # Note: TE has anti-scraping. Use their API or selenium.
        pass
    
    return prices

def fetch_usgs_commodity_summary(year=2026):
    """
    Download USGS Mineral Commodity Summaries
    """
    url = f"https://pubs.usgs.gov/periodicals/mcs{year}/mcs{year}.pdf"
    r = requests.get(url)
    with open(f'usgs_mcs_{year}.pdf', 'wb') as f:
        f.write(r.content)
    return f'usgs_mcs_{year}.pdf'
```

### Patent Monitoring
```python
def search_uspto_patents(query, date_from, date_to):
    """
    Search USPTO patents via their REST API
    """
    base_url = "https://developer.uspto.gov/api/v1/patent/applications/search"
    
    payload = {
        "q": query,
        "f": ["patentTitle", "patentApplicationNumber", "inventorName", "filingDate"],
        "s": [{"filingDate": "desc"}],
        "fq": [f"filingDate:[{date_from} TO {date_to}]"]
    }
    
    response = requests.post(base_url, json=payload)
    return response.json()

# Search for REE processing patents
patents = search_uspto_patents(
    query="rare earth extraction OR rare earth separation OR rare earth recovery",
    date_from="2026-01-01",
    date_to="2026-07-01"
)
```

### RSS Monitoring for News
```python
import feedparser

def monitor_rss_feeds(feeds):
    """
    Monitor multiple RSS feeds for critical minerals news
    """
    all_entries = []
    
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            all_entries.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published', ''),
                'source': feed.feed.title
            })
    
    return pd.DataFrame(all_entries)

# Key feeds
feeds = [
    "https://www.mining.com/feed/",
    "https://www.ree-magazine.com/feed/",
    "https://feeds.reuters.com/reuters/basicmaterialsNews",
    "https://www.spglobal.com/commodityinsights/en/market-insights/rss.xml"
]
```

## Intelligence Report Generator

```python
def generate_intel_report():
    """
    Daily/weekly intelligence briefing generator
    """
    report = {
        'date': datetime.now().isoformat(),
        'sections': []
    }
    
    # 1. Price movements
    prices = fetch_latest_prices()
    report['sections'].append({
        'title': 'Commodity Price Movements',
        'data': prices
    })
    
    # 2. News highlights
    news = search_web("rare earth critical minerals", num=10, tbs='qdr:w')
    report['sections'].append({
        'title': 'Key News',
        'data': news['organic'][:5]
    })
    
    # 3. New patents
    patents = search_uspto_patents("rare earth", "2026-06-01", "2026-07-01")
    report['sections'].append({
        'title': 'Recent Patents',
        'data': patents['response']['docs'][:5]
    })
    
    # 4. Policy updates
    policy = search_web("critical minerals policy regulation 2026", num=5)
    report['sections'].append({
        'title': 'Policy & Regulation',
        'data': policy['organic']
    })
    
    return report
```

## Best Practices

1. **Rate limiting:** Respect API limits. Use exponential backoff.
2. **Caching:** Cache search results for 1–6 hours to avoid redundant API calls.
3. **Deduplication:** Hash article URLs to avoid reporting the same story multiple times.
4. **Source weighting:** USGS, peer-reviewed journals > industry blogs > social media.
5. **Alert thresholds:** Only alert on price moves > 10% week-over-week or major policy shifts.
6. **Geographic filtering:** Tag results by country/region for relevance.
