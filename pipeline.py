import re

from agents import search_agent, reader_agent, writer_chain, critic_chain


def research_pipeline(topic: str, progress_callback=None) -> dict:

    def progress(stage, message, percent, data=None):
        if progress_callback:
            progress_callback({
                "stage": stage,
                "message": message,
                "percent": percent,
                "data": data or {}
            })

    state = {}

    # --------------------------------
    # 1. Search
    # --------------------------------

    progress(
        "search",
        "Searching the web for reliable information...",
        10
    )

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

    if isinstance(state["search_results"], list):
        state["search_results"] = "\n".join(
            str(item) for item in state["search_results"]
        )

    state["sources"] = re.findall(
        r'https?://[^\s\]\[<>"\']+',
        state["search_results"]
    )

    progress(
        "search",
        f"Web search completed — found {len(state['sources'])} sources.",
        25,
        {
            "sources": state["sources"]
        }
    )

    # --------------------------------
    # 2. Read / Scrape
    # --------------------------------

    progress(
        "reader",
        "Reading and analyzing the most relevant source...",
        30
    )

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

    progress(
        "reader",
        "Source analysis completed.",
        50
    )

    # --------------------------------
    # 3. Write report
    # --------------------------------

    progress(
        "writer",
        "Generating the research report...",
        55
    )

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

    progress(
        "writer",
        "Research report generated.",
        75
    )

    # --------------------------------
    # 4. Critic + feedback loop
    # --------------------------------

    max_retries = 2

    for attempt in range(max_retries + 1):

        progress(
            "critic",
            f"Quality check in progress (review {attempt + 1})...",
            80
        )

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

        progress(
            "critic",
            f"Quality review completed — score: {score}/10",
            88,
            {
                "score": score
            }
        )

        if score >= 7:
            break

        if attempt == max_retries:
            break

        # --------------------------------
        # Additional research
        # --------------------------------

        progress(
            "additional_search",
            "The report needs improvement. Gathering additional research...",
            60
        )

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

        if isinstance(additional_results, list):
            additional_results = "\n".join(
                str(item) for item in additional_results
            )

        combined_research += (
            f"\n\nADDITIONAL RESEARCH:\n{additional_results}"
        )

        progress(
            "rewrite",
            "Revising the report using the additional research...",
            70
        )

        # --------------------------------
        # Rewrite
        # --------------------------------

        state["report"] = writer_chain.invoke(
            {
                "topic": topic,
                "research": combined_research
            }
        )

        progress(
            "rewrite",
            "Report revised. Running another quality check...",
            78
        )

    # --------------------------------
    # Complete
    # --------------------------------

    progress(
        "complete",
        "Research completed successfully.",
        100,
        {
            "score": score
        }
    )

    return {
        "search_results": state["search_results"],
        "scrape_results": state["scrape_results"],
        "report": state["report"],
        "feedback": state["feedback"],
        "sources": state["sources"]
    }