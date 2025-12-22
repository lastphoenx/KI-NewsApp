from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers.templates import router as templates_router
from .routers.runs import router as runs_router
from .routers.output_types import router as output_types_router

app = FastAPI(title="NewsApp API")

# CORS for local development (dashboard on Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

Base.metadata.create_all(bind=engine)

app.include_router(output_types_router)
app.include_router(templates_router)
app.include_router(runs_router)
