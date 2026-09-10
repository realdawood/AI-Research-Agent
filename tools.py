import os
import requests
from langchain.tools import tool
from bs4 import BeautifulSoup
from langchain_tavily import TavilySearch
from rich import print
from dotenv import load_dotenv

load_dotenv()

tavily = TavilySearch(api_key = os.getenv("TAVILY_API_KEY"), max_results = 3, search_depth = "basic")

@tool
def web_search(query: str) -> str:
    """
    search the web for recent and reliable information on the asked topic from the internet and returns title, snippets and URLs.
    """
    result = tavily.invoke({"query": query})

    output = []

    for r in result['results']:
        output.append(
            f"Title : {r['title']}\n"
            f"URL : {r['url']}\n"
            f"Snippet : {r['content'][:300]}\n"
        )
    return "\n----\n".join(output)

@tool
def web_scrap(url : str) -> str:
    """
    scrape and return clear text content from given URL for deeper reading"""
    try:
        resp = requests.get(url, headers={"User-Agent" : "Mozilla/5.0"}, timeout=20)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "footer", "style", "nav"]):
            tag.decompose()
        return soup.get_text(separator= " ", strip = True)[:3000]
    except Exception as e:
        return f"could not Scrape URL {str(e)}"
