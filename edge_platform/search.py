#!/usr/bin/env python3
"""
EDGE Live Intelligence — Web search, commodity prices, patents.
"""
import os
import json
import httpx
from .config import MOONSHOT_API_KEY, CUSTOM_API_KEY, CUSTOM_OPENAI_BASE_URL

class WebSearchEngine:
    """
    Search the live web for REE intelligence.
    Falls back through available APIs: Serper → Brave → DuckDuckGo scrape.
    """
    
    def __init__(self):
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.brave_key = os.getenv("BRAVE_API_KEY")
    
    async def search(self, query, num=10):
        """Search and return structured results"""
        if self.serper_key:
            return await self._serper_search(query, num)
        elif self.brave_key:
            return await self._brave_search(query, num)
        else:
            return await self._duckduckgo_scrape(query)
    
    async def _serper_search(self, query, num):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": num},
                headers={"X-API-KEY": self.serper_key, "Content-Type": "application/json"},
                timeout=30
            )
            data = r.json()
            return [
                {"title": x.get("title"), "link": x.get("link"), "snippet": x.get("snippet")}
                for x in data.get("organic", [])
            ]
    
    async def _brave_search(self, query, num):
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": num},
                headers={"X-Subscription-Token": self.brave_key, "Accept": "application/json"},
                timeout=30
            )
            data = r.json()
            return [
                {"title": x.get("title"), "link": x.get("url"), "snippet": x.get("description")}
                for x in data.get("web", {}).get("results", [])
            ]
    
    async def _duckduckgo_scrape(self, query):
        # Fallback — lightweight scraping
        from urllib.parse import quote
        q = quote(query)
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://html.duckduckgo.com/html/?q={q}", timeout=30)
            # Very basic extraction
            return [{"title": "DuckDuckGo results", "link": "", "snippet": r.text[:500]}]
    
    async def fetch_ree_intel(self):
        """Fetch a bundle of REE intelligence queries"""
        queries = [
            "rare earth elements price dysprosium terbium 2026",
            "critical minerals exploration funding Africa 2026",
            "new REE deposit discovery 2026",
            "China rare earth export policy 2026"
        ]
        
        results = {}
        for q in queries:
            try:
                results[q] = await self.search(q, num=3)
            except Exception as e:
                results[q] = [{"error": str(e)}]
        
        return results
