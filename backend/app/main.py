from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routes.users import router as users_router
from app.routes.auth import router as auth_router
from app.routes.lead import router as lead_router
from app.routes.contact import router as contact_router
from app.routes.notes import router as notes_router
from app.routes.task import router as tasks_router
from app.routes.analytics import router as analytics_router
from app.routes.ai import router as ai_router

app = FastAPI(
    title="My Backend API",
    version="1.0.0"
)


# ─────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Exception Handlers
# ─────────────────────────────────────────────────────────────

@app.exception_handler(TypeError)
async def type_error_handler(
    request: Request,
    exc: TypeError,
):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": str(exc),
        },
    )


# ─────────────────────────────────────────────────────────────
# Root
# ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "API is running"
    }


# ─────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(lead_router)
app.include_router(contact_router)
app.include_router(notes_router)
app.include_router(tasks_router)
app.include_router(analytics_router)
app.include_router(ai_router)