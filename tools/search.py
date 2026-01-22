try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

import httpx
from bs4 import BeautifulSoup

def fetch_article_content(url: str, max_length: int = 1000) -> str:
    """
    Fetch and extract main text content from a URL.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = httpx.get(url, headers=headers, timeout=5, follow_redirects=True)
        
        if response.status_code != 200:
            return "(Content unavailable)"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, nav, footer
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
        
        # Try to find main content
        content = soup.find('article') or soup.find('main') or soup.find('body')
        
        if not content:
            return "(Could not extract content)"
        
        # Get text and clean it
        text = content.get_text(separator=' ', strip=True)
        text = ' '.join(text.split())  # Remove extra whitespace
        
        return text[:max_length] + "..." if len(text) > max_length else text
    
    except Exception as e:
        return f"(Error fetching content: {e})"


def search_web(query: str, max_results: int = 3, fetch_content: bool = True) -> dict:
    """
    Searches the web using DuckDuckGo and optionally fetches full article content.
    Returns dict with 'content' (formatted text) and 'sources' (list of URLs).
    """
    try:
        print(f"[SEARCH] Searching for: {query}")
        
        ddg = DDGS()
        # Restrict to past month ('m') for financial news
        # Append current year to query to force relevance
        from datetime import datetime
        current_year = datetime.now().year
        search_query = f"{query} {current_year}"
        print(f"[SEARCH] Modified query: {search_query}")
        
        results = list(ddg.text(search_query, max_results=max_results, timelimit='m'))
        
        print(f"[SEARCH] Found {len(results)} results")
        
        if not results:
            return {"content": "No results found.", "sources": []}
        
        formatted = ""
        sources = []
        
        for i, res in enumerate(results, 1):
            title = res.get('title', 'No title')
            href = res.get('href', res.get('link', 'No URL'))
            snippet = res.get('body', res.get('snippet', ''))
            
            # Store source for citation
            sources.append({"title": title, "url": href})
            
            formatted += f"\n{'='*60}\n"
            formatted += f"Result {i}: {title}\n"
            formatted += f"URL: {href}\n\n"
            
            if fetch_content and href and not href.startswith('javascript'):
                print(f"[SEARCH] Fetching content from: {href[:50]}...")
                content = fetch_article_content(href)
                formatted += f"Content:\n{content}\n"
            else:
                formatted += f"Snippet: {snippet}\n"
        
        return {"content": formatted, "sources": sources}
    
    except Exception as e:
        print(f"[SEARCH ERROR] {type(e).__name__}: {e}")
        return {"content": f"Search failed: {str(e)}", "sources": []}

if __name__ == "__main__":
    print("Testing search with content extraction...")
    result = search_web("Bitcoin price drop reasons", max_results=2)
    print(result)
