import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import os
import json

load_dotenv()

# ── TOOL 1: Web Search ────────────────────────────────────────────
def search_web(query: str) -> str:
    """
    Search the web using Serper API and return results.
    """
    try:
        api_key = os.getenv("SERPER_API_KEY")
        
        response = httpx.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            },
            json={
                "q": query,
                "num": 5
            },
            timeout=10
        )
        
        data = response.json()
        results = []
        
        # Get organic search results
        for item in data.get("organic", [])[:5]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"Title: {title}\nSummary: {snippet}\nURL: {link}")
        
        # Also get news if available
        for item in data.get("news", [])[:3]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"[NEWS] Title: {title}\nSummary: {snippet}\nURL: {link}")
        
        if not results:
            return "No results found for this query."
        
        return "\n\n".join(results)
    
    except Exception as e:
        return f"Search failed: {str(e)}"


# ── TOOL 2: Read Webpage ──────────────────────────────────────────
def read_webpage(url: str) -> str:
    """
    Read and extract the main content from any webpage.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")
        
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = "\n".join(lines)
        
        return content[:3000] if len(content) > 3000 else content
    
    except Exception as e:
        return f"Could not read page: {str(e)}"


# ── TOOL 3: Get Current Date ──────────────────────────────────────
def get_current_date() -> str:
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%H:%M')}."


# ── TOOL 4: Calculate ─────────────────────────────────────────────
def calculate(expression: str) -> str:
    try:
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return "Invalid expression. Only basic math is allowed."
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation failed: {str(e)}"


# ── TOOL REGISTRY ─────────────────────────────────────────────────
TOOLS = {
    "search_web": search_web,
    "read_webpage": read_webpage,
    "get_current_date": get_current_date,
    "calculate": calculate,
}

TOOL_DEFINITIONS = [
    {
        "name": "search_web",
        "description": "Search the web for current information, news, facts, or anything you don't know. Use this when you need up-to-date information.",
        "parameters": {
            "query": "The search query string"
        }
    },
    {
        "name": "read_webpage",
        "description": "Read and extract the full content of a webpage. Use this after search_web to get more details from a specific URL.",
        "parameters": {
            "url": "The full URL of the webpage to read"
        }
    },
    {
        "name": "get_current_date",
        "description": "Get today's date and current time.",
        "parameters": {}
    },
    {
        "name": "calculate",
        "description": "Perform mathematical calculations.",
        "parameters": {
            "expression": "The mathematical expression to evaluate"
        }
    }
]