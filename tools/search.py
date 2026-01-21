from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 5) -> str:
    """
    Searches the web for the given query.
    """
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No results found."
            
        formatted = ""
        for i, res in enumerate(results, 1):
            formatted += f"{i}. {res['title']}\n   {res['href']}\n   {res['body'][:200]}...\n\n"
            
        return formatted
        
    except Exception as e:
        return f"Error performing search: {str(e)}"
