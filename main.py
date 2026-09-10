from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pipeline import research_pipeline


app = FastAPI(
    title="AI Research Agent",
    description="AI-powered research and report generation system",
    version="1.0.0"
)


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    topic: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/api/research")
def research(request: ResearchRequest):

    if not request.topic.strip():
        return {
            "error": "Please enter a research topic."
        }

    result = research_pipeline(request.topic)

    return {
        "topic": request.topic,
        "report": result["report"],
        "feedback": result["feedback"],
        "sources": result["sources"]
}


# Serve frontend
app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


@app.get("/")
def home():
    return FileResponse("frontend/index.html")