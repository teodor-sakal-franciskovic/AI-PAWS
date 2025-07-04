from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# needed for Alembic migrations to work
from .models.base import AcademicWritingSchema
from .routers import auth, chapter, group, role, user, feedback

description = """

# Endpoints
## Auth

Endpoints associated with the authorisation to the system, such as the login.

## Users

Endpoints associated with the users of the system, such as the registration, retrieval, and so on.

## Roles

Endpoints associated with the user roles, such as their retrieval.

## Chapters

Endpoints associated with the written chapters, such as the interactive and evaluation mode that analyses the chapters.

## Groups

Endpoints associated with the student groups, such as their creation.

## Feedbacks

Endpoints associated with the paper feedback, such as the additional interactive feedback.
"""

app = FastAPI(
    title="AI-PAWS",
    description=description,
    summary="AI-Powered Academic Writing Support",
    version="0.0.1",  # TODO: Correlate with semantic versioning/pushing to dockerhub
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(role.router)
app.include_router(chapter.router)
app.include_router(group.router)
app.include_router(feedback.router)
