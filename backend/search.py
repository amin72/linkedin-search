
def search_profiles(
    profiles: list[dict],
    q: str | None = None,
    skill: str | None = None,
    title: str | None = None,
    page: int = 1,
    page_size: int = 10
) -> dict:
    """Search and filter profiles with pagination"""

    results = profiles.copy()

    # Keyword search
    if q and q.strip():
        q_lower = q.strip().lower()
        filtered = []
        for p in results:
            search_fields = [
                p.get('full_name', ''),
                p.get('job_title', ''),
                p.get('job_company_name', ''),
                p.get('summary', ''),
                p.get('industry', ''),
            ]

            if p.get('skills') and isinstance(p['skills'], list):
                search_fields.extend([str(s).lower() for s in p['skills'] if s])

            matches = False
            for field in search_fields:
                if field and q_lower in str(field).lower():
                    matches = True
                    break

            if matches:
                filtered.append(p)
        results = filtered

    # Filter by skill
    if skill and skill.strip():
        skill_lower = skill.strip().lower()
        filtered = []
        for p in results:
            if p.get('skills') and isinstance(p['skills'], list):
                for s in p['skills']:
                    if s and skill_lower in str(s).lower():
                        filtered.append(p)
                        break
        results = filtered

    # Filter by job title
    if title and title.strip():
        title_lower = title.strip().lower()
        filtered = []
        for p in results:
            if p.get('job_title') and title_lower in str(p['job_title']).lower():
                filtered.append(p)
        results = filtered

    # Pagination
    total = len(results)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_results = results[start_idx:end_idx]

    # Convert to ProfileResponse objects
    from models import ProfileResponse
    profile_responses = [ProfileResponse(**p) for p in paginated_results]

    return {
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'results': profile_responses
    }
