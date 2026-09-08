from data import get_profiles, get_skills, get_titles
from fastapi import APIRouter, Query
from models import SearchResponse
from search import search_profiles

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "LinkedIn Profile Search API", "docs": "/docs"}


@router.get("/api/search", response_model=SearchResponse)
async def search(
    q: str | None = Query(None, description="Search keyword"),
    skill: str | None = Query(None, description="Filter by skill"),
    title: str | None = Query(None, description="Filter by job title"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page")
):
    profiles = get_profiles()
    result = search_profiles(profiles, q, skill, title, page, page_size)
    result["filters"] = {
        "skills": get_skills(),
        "titles": get_titles()
    }
    return result


@router.get("/api/filters")
async def get_filters():
    return {
        "skills": get_skills(),
        "titles": get_titles()
    }


@router.get("/api/profiles")
async def get_all_profiles():
    profiles = get_profiles()
    return {
        "total": len(profiles),
        "profiles": profiles
    }
