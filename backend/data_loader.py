import ast
import json
from typing import Any

import pandas as pd


def parse_json_field(field):
    """Parse JSON/string fields that contain lists or dicts"""
    if pd.isna(field) or field is None:
        return []
    if isinstance(field, (list, dict)):
        return field
    if isinstance(field, str):
        try:
            return json.loads(field)
        except:
            try:
                return ast.literal_eval(field)
            except:
                return []
    return field

def load_profiles(csv_path: str) -> list[dict[str, Any]]:
    """Load and parse LinkedIn profiles from CSV"""
    df = pd.read_csv(
        csv_path, 
        dtype=str, 
        keep_default_na=False,
        engine='python',
        on_bad_lines='skip'
    )

    profiles = []
    for _, row in df.iterrows():
        profile = row.to_dict()
        
        nested_fields = ['skills', 'experience', 'education', 'profiles', 
                         'certifications', 'languages', 'location_names', 
                         'regions', 'countries', 'street_addresses']
        for field in nested_fields:
            if field in profile:
                profile[field] = parse_json_field(profile[field])
        
        profile = {k: v if v != '' and v != '[]' else None for k, v in profile.items()}
        profiles.append(profile)

    return profiles

def get_all_skills(profiles: list[dict]) -> list[str]:
    """Extract all unique skills from profiles"""
    skills_set = set()
    for p in profiles:
        if p.get('skills') and isinstance(p['skills'], list):
            for skill in p['skills']:
                if skill and isinstance(skill, str):
                    skill_clean = skill.strip()
                    # Skip if it looks like a phone number
                    if skill_clean.startswith('+') and any(c.isdigit() for c in skill_clean):
                        continue
                    if len(skill_clean) > 2:
                        skills_set.add(skill_clean)
    return sorted(skills_set)


def get_all_titles(profiles: list[dict]) -> list[str]:
    """Extract all unique job titles from profiles"""
    # Words/patterns that indicate it's NOT a real job title
    BAD_PATTERNS = [
        'accounts', 'active pest control', 'alan plummer associates', 'amazon',
        'american family insurance', 'amideast', 'ashland inc', 'automotive',
        'aviation & aerospace', 'bae-systems', 'baker-college', 'biotechnology',
        'chai pani', 'combat capabilities development', 'computer & network security',
        'construction', 'cushman & wakefield', 'defense & space', 'do it best',
        'durham va', 'editorial', 'education management', 'electrical/electronic',
        'entertainment', 'environmental services', 'expedia', 'financial services',
        'florida-atlantic-university', 'franklin iq', 'gehealthcare',
        'georgia-school-boards', 'government administration', 'higher education',
        'hospital & health care', 'hubbard', 'human resources', 'idaho-state-university',
        'information technology', 'information_technology', 'instrumental music',
        'insurance', 'international affairs', 'investment', 'job_title', 'julch trucking',
        'kbr-inc', 'law enforcement', 'lawyer', 'legal services',
        'logistics and supply chain', 'management consulting', 'manager',
        'manitowoc-crane', 'marine toys', 'marketing and advertising', 'mcsg',
        'medical devices', 'medical practice', 'medical solutions', 'metlife',
        'military', 'mustang public schools', 'nasa langley', 'non-profit',
        "o'melveny", 'oil & energy', 'orange county rescue mission',
        'phoenix-college', 'photography', 'product', 'professor',
        'project_management', 'prudential', 'public policy',
        'public relations and communications', 'public safety', 'real estate',
        'religious institutions', 'research', 'rs&h', 'security and investigations',
        'semiconductors', 'sentry insurance', 'service-tech-av', 'sham',
        'studenterbolaget', 'telecommunications', 'tgs_220114', 'the-andersons',
        'utilities', 'writing'
    ]
    
    titles_set = set()
    for p in profiles:
        title = p.get('job_title')
        if title and isinstance(title, str):
            title_clean = title.strip()
            
            # Skip if it looks like JSON or a list
            if title_clean.startswith(('[', '{')):
                continue

            # Skip if contains brackets or quotes
            if '[' in title_clean or '{' in title_clean:
                continue

            # Skip if too short
            if len(title_clean) < 5:
                continue

            # Skip if it's in the bad patterns list
            skip = False
            for bad in BAD_PATTERNS:
                if bad in title_clean.lower():
                    skip = True
                    break
            if skip:
                continue
            
            titles_set.add(title_clean)
    
    return sorted(titles_set)
