from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# needed for Alembic migrations to work
from .models.base import AcademicWritingSchema  # noqa: F401
from .routers import (
    assignment,
    auth,
    chapter,
    course,
    feedback,
    group,
    role,
    submission_mode,
    user,
)

description = """

# Endpoints
## Auth

Endpoints associated with the authorisation to the system, such as the login.

## Users

Endpoints associated with the users of the system, such as the registration, retrieval, and so on.

## Roles

Endpoints associated with the user roles, such as their retrieval.

## Chapters

Endpoints associated with the written chapters, such as their retrieval.

## Groups

Endpoints associated with the student groups, such as their creation.

## Feedbacks

Endpoints associated with the paper feedback, such as the additional interactive feedback.

## Assignments

Endpoints associated with the assignments, such as their creation.

## Submission modes

Endpoints associated with the submission modes, such as their retrieval.

## Course

Endpoints associated with course creation.
"""

app = FastAPI(
    title="AI-PAWS",
    description=description,
    summary="AI-Powered Academic Writing Support",
    version="0.0.1",
    contact={
        "name": "Teodor Sakal Francišković",
        "email": "teodor.sakal_franciskovic@uns.ac.rs",
    },
    license_info={
        "name": "Apache 2.0 - License information",
        "identifier": "MIT",
    },
    docs_url="/documentation",
    redoc_url=None,
)

"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    """Health check endpoint for App Runner"""
    return {"status": "healthy", "message": "AI-PAWS API is running"}


@app.get("/health")
async def detailed_health_check():
    """Detailed health check with basic diagnostics"""
    from .settings import settings

    return {
        "status": "healthy",
        "environment": settings.environment,
        "use_aws_secrets": settings.use_aws_secrets,
    }


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(role.router)
app.include_router(chapter.router)
app.include_router(group.router)
app.include_router(feedback.router)
app.include_router(assignment.router)
app.include_router(submission_mode.router)
app.include_router(course.router)
