from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import category, chat, dashboard, database, feedback, health, knowledge, llm, safety, vector


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(database.router)
app.include_router(category.router)
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(safety.router)
app.include_router(feedback.router)
app.include_router(dashboard.router)
app.include_router(vector.router)
app.include_router(llm.router)
