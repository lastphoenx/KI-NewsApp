"""
URL-Fetcher mit BeautifulSoup für HTML-Extraktion
"""
import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict
import time

async def fetch_url(url: str, timeout: int = 10) -> Dict[str, any]:
    """
    Fetcht URL und extrahiert Text-Content
    
    Returns:
        {
            "url": str,
            "status": int,
            "content_type": str,
            "text": str,           # Extrahierter Plain-Text
            "title": str,          # <title> Tag
            "error": Optional[str]
        }
    """
    result = {
        "url": url,
        "status": 0,
        "content_type": None,
        "text": "",
        "title": "",
        "error": None
    }
    
    # URL normalisieren
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        result["url"] = url
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            result["status"] = response.status_code
            result["content_type"] = response.headers.get("content-type", "")
            
            if response.status_code != 200:
                result["error"] = f"HTTP {response.status_code}"
                return result
            
            # Nur HTML verarbeiten
            if "text/html" not in result["content_type"].lower():
                result["error"] = f"Nicht-HTML Content-Type: {result['content_type']}"
                return result
            
            # HTML parsen
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Title extrahieren
            title_tag = soup.find("title")
            result["title"] = title_tag.get_text(strip=True) if title_tag else ""
            
            # Text extrahieren (ohne Scripts, Styles, Navigation)
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            
            # Hauptcontent bevorzugen
            main_content = (
                soup.find("main") or 
                soup.find("article") or 
                soup.find("div", {"id": "content"}) or
                soup.find("div", {"class": "content"}) or
                soup.body or
                soup
            )
            
            # Text extrahieren und säubern
            text = main_content.get_text(separator="\n", strip=True)
            
            # Mehrfache Leerzeichen/Newlines normalisieren
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            result["text"] = "\n".join(lines)
            
            # Limitieren auf erste 50.000 Zeichen (LLM-Token-Limits)
            if len(result["text"]) > 50000:
                result["text"] = result["text"][:50000] + "\n\n[... gekürzt ...]"
            
    except httpx.TimeoutException:
        result["error"] = f"Timeout nach {timeout}s"
    except httpx.ConnectError:
        result["error"] = "Verbindung fehlgeschlagen"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
    
    return result


async def fetch_multiple(urls: list[str], max_concurrent: int = 5) -> list[Dict]:
    """
    Fetcht mehrere URLs parallel (mit Rate-Limiting)
    """
    import asyncio
    
    results = []
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_with_limit(url):
        async with semaphore:
            result = await fetch_url(url)
            await asyncio.sleep(0.5)  # 500ms Pause zwischen Requests
            return result
    
    tasks = [fetch_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Exceptions in Error-Dicts umwandeln
    cleaned_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            cleaned_results.append({
                "url": urls[i],
                "status": 0,
                "content_type": None,
                "text": "",
                "title": "",
                "error": str(result)
            })
        else:
            cleaned_results.append(result)
    
    return cleaned_results
