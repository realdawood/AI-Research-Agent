import json
import queue
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from pipeline import research_pipeline


app = FastAPI(
    title="AI Research Agent",
    description="AI-powered research and report generation system",
    version="1.0.0"
)


# --------------------------------
# CORS
# --------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    topic: str


# --------------------------------
# Health
# --------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# --------------------------------
# Streaming research
# --------------------------------

@app.post("/api/research")
def research(request: ResearchRequest):

    if not request.topic.strip():
        return {
            "error": "Please enter a research topic."
        }

    events = queue.Queue()

    def send_progress(event):
        events.put({
            "type": "progress",
            **event
        })

    def run_pipeline():

        try:

            result = research_pipeline(
                request.topic,
                progress_callback=send_progress
            )

            events.put({
                "type": "result",
                "data": {
                    "topic": request.topic,
                    "report": result["report"],
                    "feedback": result["feedback"],
                    "sources": result["sources"]
                }
            })

        except Exception as e:

            events.put({
                "type": "error",
                "message": str(e)
            })

        finally:

            events.put({
                "type": "done"
            })

    thread = threading.Thread(
        target=run_pipeline,
        daemon=True
    )

    thread.start()

    def event_stream():

        while True:

            event = events.get()

            yield f"data: {json.dumps(event)}\n\n"

            if event["type"] == "done":
                break

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# --------------------------------
# Frontend
# --------------------------------

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


@app.get("/")
def home():
    return FileResponse("frontend/index.html")