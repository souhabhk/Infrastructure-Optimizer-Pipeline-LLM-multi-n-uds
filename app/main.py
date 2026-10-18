from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Infrastructure Optimizer",
    description="Turns infrastructure log metrics into a structured optimisation report.",
    version="0.1.0",
)
app.include_router(router)
