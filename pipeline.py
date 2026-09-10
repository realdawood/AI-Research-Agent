import re
from agents import search_agent, reader_agent, writer_chain, critic_chain


def research_pipeline(topic: str) -> dict:

    state = {}

    # 1. Search
    search = search_agent()

    search_result = search.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Find recent, reliable information on the {topic}"
                }
            ]
        }
    )

    state["search_results"] = search_result["messages"][-1].content

    state["sources"] = re.findall(
    r'https?://[^\s\]\[<>"\']+',
    state["search_results"]
)

    # 2. Read / Scrape
    reader = reader_agent()

    reader_result = reader.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Based on the following search results about '{topic}', "
                        f"pick the URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n"
                        f"{state['search_results'][:800]}"
                    )
                }
            ]
        }
    )

    state["scrape_results"] = reader_result["messages"][-1].content

    # 3. Write report
    combined_research = (
        f"SEARCH RESULT:\n{state['search_results']}\n\n"
        f"SCRAPED RESULT:\n{state['scrape_results']}"
    )

    state["report"] = writer_chain.invoke(
        {
            "topic": topic,
            "research": combined_research
        }
    )

    # 4. Critic + feedback loop
    max_retries = 2

    for attempt in range(max_retries + 1):

        state["feedback"] = critic_chain.invoke(
            {
                "report": state["report"]
            }
        )

        score_match = re.search(
    r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10",
    state["feedback"]
)

        score = float(score_match.group(1)) if score_match else 0

        if score >= 7:
            break

        if attempt == max_retries:
            break

        # Additional research
        search = search_agent()

        additional_research = search.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"The research report about '{topic}' received "
                            f"a score of {score}/10.\n\n"
                            f"Critic feedback:\n{state['feedback']}\n\n"
                            f"Find additional reliable information that "
                            f"addresses these weaknesses."
                        )
                    }
                ]
            }
        )

        additional_results = additional_research["messages"][-1].content

        combined_research += (
            f"\n\nADDITIONAL RESEARCH:\n{additional_results}"
        )

        # Rewrite
        state["report"] = writer_chain.invoke(
            {
                "topic": topic,
                "research": combined_research
            }
        )

    return {
        "search_results": state["search_results"],
        "scrape_results": state["scrape_results"],
        "report": state["report"],
        "feedback": state["feedback"],
        "sources": state["sources"]
    }
