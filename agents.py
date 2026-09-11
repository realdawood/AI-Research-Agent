from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

from tools import web_scrap, web_search


# --------------------------------
# Local LLM
# --------------------------------

llm = ChatOllama(
    model="qwen3:1.7b",
    temperature=0
)


# --------------------------------
# Agents
# --------------------------------

def search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )


def reader_agent():
    return create_agent(
        model=llm,
        tools=[web_scrap]
    )


# --------------------------------
# Writer
# --------------------------------

writer = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a professional research analyst.

Write clear, natural and easy-to-read research reports.

The report will be displayed directly inside a web application.

Formatting rules:
- Do not use triple backticks or code fences.
- Do not wrap the report in ``` or ```markdown.
- Do not use tables.
- Do not use excessive Markdown formatting.
- Do not use unnecessary bold text.
- Do not use horizontal lines.
- Do not use placeholder text.
- Do not say "Prepared for".
- Avoid unnecessary academic language.
- Avoid repetitive statements.

Use exactly these headings:

Introduction
Key Findings
Conclusion
Sources

Keep the writing factual, concise and professional."""
    ),

    (
        "human",
        """Research the following topic using the information provided.

Topic: {topic}

Research:
{research}

Write the final report using this structure:

# Introduction

A short introduction to the topic.

# Key Findings

Provide 3-5 important findings.
Explain each finding in a few clear paragraphs.

# Conclusion

Give a concise overall assessment.

# Sources

List the URLs used in the research.
"""
    )
])

writer_chain = writer | llm | StrOutputParser()


# --------------------------------
# Critic
# --------------------------------

critic = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. Be sharp and honest."
    ),

    (
        "human",
        """Review the search report below and evaluate it strictly.

Report:
{report}

Respond in exactly this format:

Score: X/10

Strengths:
1. ...
2. ...

Areas to Improve:
1. ...
2. ...

One-line Verdict:
...

Do not use Markdown.
Do not use asterisks.
Do not use hashtags.
Do not use bullet symbols.
Do not use code fences."""
    )
])

critic_chain = critic | llm | StrOutputParser()