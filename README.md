# AI Research Agent

An AI-powered research assistant that searches the web, reads relevant sources, generates a research report, and evaluates the report using a critic agent.

If the report receives a low score, the system performs additional targeted research, reads the new sources, rewrites the report, and evaluates it again.

## Features

* 🔎 Web search using Tavily
* 🤖 AI-powered search and reader agents
* 🌐 Web scraping for deeper source content
* 📝 Automated research report generation
* 🧐 AI critic for report evaluation
* 🔄 Iterative research and improvement loop
* 📚 Source collection and display
* ⚡ FastAPI backend
* 🎨 Responsive HTML/CSS/JavaScript frontend
* 🛡️ Bounded retries to prevent infinite improvement loops

## How It Works

The system follows an iterative research workflow:

```text
User Topic
    ↓
Search Agent
    ↓
Reader Agent
    ↓
Report Writer
    ↓
Critic
    ↓
Score >= 7?
   ├── Yes → Final Report
   │
   └── No → Additional Research
                 ↓
              Reader Agent
                 ↓
              Rewrite Report
                 ↓
                Critic
                 ↺
```

The system allows a maximum of two improvement cycles after the initial report.

## Project Structure

```text
AI-Research-Agent/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── agents.py
├── pipeline.py
├── tools.py
├── main.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

## Technologies Used

* Python
* LangChain
* LangChain Agents
* OpenRouter
* Tavily Search
* FastAPI
* HTML
* CSS
* JavaScript
* BeautifulSoup
* Requests
* Pydantic

## Agent Architecture

### Search Agent

The Search Agent uses the web search tool to find recent and reliable information related to the user's topic.

### Reader Agent

The Reader Agent selects a relevant URL from the search results and uses the web scraping tool to retrieve deeper content from the source.

### Report Writer

The Writer LLM combines the search results and scraped content to generate a structured research report.

### Critic

The Critic evaluates the generated report and provides:

* Score
* Strengths
* Areas to improve
* Overall verdict

### Iterative Improvement

If the critic gives the report a score below 7/10, the system performs targeted additional research based on the critic's feedback.

The new information is then read, added to the existing research, and used to rewrite the report.

This process can repeat for a maximum of two improvement cycles.

## API Endpoints

### Health Check

```http
GET /health
```

Returns:

```json
{
  "status": "healthy"
}
```

### Research

```http
POST /api/research
```

Request:

```json
{
  "topic": "Artificial Intelligence in Healthcare"
}
```

The endpoint returns the generated report, critic feedback, and collected sources.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/realdawood/AI-Research-Agent.git
cd AI-Research-Agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example`.

```env
TAVILY_API_KEY=your_tavily_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

Never commit your `.env` file to GitHub.

### 5. Run the application

```bash
uvicorn main:app --reload
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

## Example Workflow

For a topic such as:

```text
Impact of Generative AI on Software Development
```

the system:

1. Searches the web for recent information.
2. Identifies relevant sources.
3. Scrapes a source for deeper content.
4. Generates a research report.
5. Sends the report to the critic.
6. Evaluates the report.
7. If the score is below 7/10, performs additional targeted research.
8. Reads the additional source.
9. Rewrites the report.
10. Runs the critic again.
11. Returns the final report and sources.

## Environment Variables

Create a `.env` file containing:

```env
TAVILY_API_KEY=
OPENROUTER_API_KEY=
```

You can use `.env.example` as a template.

## Limitations

This project is designed as a learning and portfolio project.

Web scraping may not work correctly with every website because some websites use:

* JavaScript-rendered content
* Bot protection
* Authentication
* Paywalls
* Rate limiting
* Restricted access

The quality of the generated report also depends on the quality and availability of the retrieved sources.

## Future Improvements

Possible future improvements include:

* More reliable structured source handling
* Better source selection
* Improved research-stage progress indicators
* More robust error handling
* Automated testing
* Logging and monitoring
* More advanced evaluation methods
* Production deployment

## Project Purpose

This project was built to practice and demonstrate practical Generative AI and Agentic AI concepts, including tool calling, web research, web scraping, multi-step agent workflows, report generation, evaluation, and iterative improvement.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
