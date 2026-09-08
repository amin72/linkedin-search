import os

from data_loader import get_all_skills, get_all_titles, load_profiles
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from models import SearchResponse
from search import search_profiles

app = FastAPI(
    title="LinkedIn Profile Search API",
    description="Search and filter LinkedIn profiles",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load profiles (lazy loading)
PROFILES = None
ALL_SKILLS = None
ALL_TITLES = None


def get_profiles():
    global PROFILES
    if PROFILES is None:
        csv_path = os.path.join(os.path.dirname(__file__), 'dataset.csv')
        PROFILES = load_profiles(csv_path)
    return PROFILES


def get_skills():
    global ALL_SKILLS
    if ALL_SKILLS is None:
        ALL_SKILLS = get_all_skills(get_profiles())
    return ALL_SKILLS


def get_titles():
    global ALL_TITLES
    if ALL_TITLES is None:
        ALL_TITLES = get_all_titles(get_profiles())
    return ALL_TITLES


@app.get("/")
async def root():
    return {"message": "LinkedIn Profile Search API", "docs": "/docs"}


@app.get("/api/search", response_model=SearchResponse)
async def search(
    q: str | None = Query(None, description="Search keyword"),
    skill: str | None = Query(None, description="Filter by skill"),
    title: str | None = Query(None, description="Filter by job title"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page")
):
    """Search and filter LinkedIn profiles"""
    profiles = get_profiles()
    result = search_profiles(profiles, q, skill, title, page, page_size)

    # Add filters to response
    result['filters'] = {
        'skills': get_skills(),
        'titles': get_titles()
    }

    return result


@app.get("/api/filters")
async def get_filters():
    """Get available filters (skills and titles)"""
    return {
        'skills': get_skills(),
        'titles': get_titles()
    }


@app.get("/api/profiles")
async def get_all_profiles():
    """Get all profiles (for debugging)"""
    profiles = get_profiles()
    return {
        'total': len(profiles),
        'profiles': profiles
    }
