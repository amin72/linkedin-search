from typing import Any

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    job_title: str | None = None
    job_company_name: str | None = None
    location_name: str | None = None
    location_locality: str | None = None
    location_region: str | None = None
    location_country: str | None = None
    linkedin_url: str | None = None
    linkedin_username: str | None = None
    skills: list[str] = []
    summary: str | None = None
    experience: list[Any] = []
    education: list[Any] = []
    inferred_salary: str | None = None
    inferred_years_experience: str | None = None
    industry: str | None = None


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    results: list[ProfileResponse]
    filters: dict | None = None
