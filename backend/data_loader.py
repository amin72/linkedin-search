import ast
import json
import re
from typing import Any

import pandas as pd


def parse_json_field(field):
    """Parse JSON/string fields that contain lists or dicts"""
    if pd.isna(field) or field is None:
        return []

    if isinstance(field, (list, dict)):
        if isinstance(field, dict):
            return []
        if isinstance(field, list):
            return [item for item in field if item and isinstance(item, str) and item.strip()]
        return field

    if isinstance(field, str):
        if not field or not field.strip():
            return []
        if field == "[]" or field == "['']" or field == "[\"\"]":
            return []
        try:
            result = json.loads(field)
            if isinstance(result, dict):
                return []
            if isinstance(result, list):
                return [item for item in result if item and isinstance(item, str) and item.strip()]
            return result
        except:
            try:
                result = ast.literal_eval(field)
                if isinstance(result, dict):
                    return []
                if isinstance(result, list):
                    return [item for item in result if item and isinstance(item, str) and item.strip()]
                return result
            except:
                if field.strip():
                    return [field.strip()]
                return []

    return field


def is_location(value: str) -> bool:
    """Check if a string looks like a location (city, state, country)"""
    location_indicators = [
        "united states", "united kingdom", "canada", "australia",
        "texas", "california", "new york", "florida", "ohio",
        "street", "avenue", "boulevard", "road", "drive",
        "city", "town", "village", "county", "state"
    ]

    value_lower = value.lower()
    for indicator in location_indicators:
        if indicator in value_lower and "," in value:
            return True

    return False


def extract_location(profile: dict) -> str | None:
    """Extract clean location from profile"""
    location = profile.get("location_name")

    # Skip if location looks like a date or number
    if location and isinstance(location, str):
        if re.search(r"\d{4}-\d{2}-\d{2}", location):
            return None
        if re.match(r"^[\d\.]+$", location.strip()):
            return None
        if re.search(r"\d{4}-\d{2}-\d{2},\s*[\d\.]+", location):
            return None
        if location.startswith(("[", "{")):
            pass
        elif location.strip():
            return location.strip()

    locality = profile.get("location_locality")
    region = profile.get("location_region")
    country = profile.get("location_country")

    if locality and isinstance(locality, str):
        if re.search(r"\d{4}-\d{2}-\d{2}", locality) or re.match(r"^[\d\.]+$", locality.strip()):
            locality = None

    if locality and isinstance(locality, str):
        if locality.startswith(("[", "{")):
            pass
        elif locality.strip():
            parts = [locality.strip()]
            if region and isinstance(region, str) and not region.startswith("[") and region.strip():
                parts.append(region.strip())
            if country and isinstance(country, str) and not country.startswith("[") and country.strip():
                parts.append(country.strip())
            result = ", ".join(parts)
            if re.search(r"\d{4}-\d{2}-\d{2}", result):
                return None
            return result

    if region and isinstance(region, str) and not region.startswith("[") and region.strip():
        parts = [region.strip()]
        if country and isinstance(country, str) and not country.startswith("[") and country.strip():
            parts.append(country.strip())
        result = ", ".join(parts)
        if re.search(r"\d{4}-\d{2}-\d{2}", result):
            return None
        return result

    if country and isinstance(country, str) and not country.startswith("[") and country.strip():
        return country.strip()

    return None


def extract_title(value):
    """Extract clean title from malformed job_title data"""
    if value is None or pd.isna(value):
        return None

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        malformed_patterns = [
            "Specialties:", "Overseas assignments", "H:\\", ".csv(",
            "part-", "New folder", "BreachedData", "LinkedIn-",
            "[", "{", "'company':", "\"company\":", "['", "[\"",
            "\\Users\\", "C:\\", "D:\\", "/home/",
        ]
        for pattern in malformed_patterns:
            if pattern in value:
                return None
        return value

    return None


def clean_summary(value):
    """Remove phone numbers and other noise from summary"""
    if value is None or pd.isna(value):
        return None

    if isinstance(value, str):
        if value == "[]" or value == "['']" or value == "[\"\"]":
            return None

        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = ast.literal_eval(value)
                if isinstance(parsed, list):
                    cleaned_items = [str(item).strip() for item in parsed if item and str(item).strip()]
                    if not cleaned_items:
                        return None
                    value = " ".join(cleaned_items)
            except:
                pass

    if isinstance(value, list):
        cleaned_items = [str(item).strip() for item in value if item and str(item).strip()]
        if not cleaned_items:
            return None
        value = " ".join(cleaned_items)

    if isinstance(value, str):
        value_clean = value.strip()

        if re.match(r"^[\d\.]+$", value_clean):
            return None

        words = value_clean.split()
        if len(words) < 3 or len(value_clean) < 15:
            return None

        phone_pattern = r"\+?\d{1,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4,5}"
        cleaned = re.sub(phone_pattern, "", value)
        cleaned = re.sub(r"\[\'\+?\d{10,15}\'(?:,\s*\'\+?\d{10,15}\')*\]", "", cleaned)
        cleaned = re.sub(r"\[\s*\]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned = cleaned.strip(",;:. ")
        if not cleaned or len(cleaned) < 15 or len(cleaned.split()) < 3:
            return None
        return cleaned

    return None


def is_empty_summary(value) -> bool:
    """Check if summary is empty or contains only empty strings"""
    if value is None:
        return True

    if isinstance(value, list):
        if not value:
            return True
        for item in value:
            if item and str(item).strip():
                return False
        return True

    if isinstance(value, str):
        return not value.strip()

    return True


def is_malformed_row(profile: dict) -> bool:
    """Check if a row contains malformed data"""
    malformed_patterns = [
        "Specialties:", "Overseas assignments", "H:\\", ".csv(",
        "part-", "New folder", "BreachedData", "LinkedIn-",
        "\\Users\\", "C:\\", "D:\\", "E:\\", "/home/", "/Users/",
        ".txt", ".csv", ".json", "H:/", "C:/",
    ]

    for key, value in profile.items():
        if isinstance(value, str):
            for pattern in malformed_patterns:
                if pattern in value:
                    return True

            if ":" in value and ("\\" in value or "/" in value):
                return True

            if key in ["location_name", "location_locality", "location_region"]:
                if re.search(r"\d{4}-\d{2}-\d{2}", value):
                    return True
                if re.match(r"^[\d\.]+$", value.strip()):
                    return True

    return False


def load_profiles(csv_path: str) -> list[dict[str, Any]]:
    """Load and parse LinkedIn profiles from CSV"""
    df = pd.read_csv(
        csv_path,
        dtype=str,
        keep_default_na=False,
        engine="python",
        on_bad_lines="skip"
    )

    profiles = []
    for _, row in df.iterrows():
        try:
            profile = row.to_dict()

            full_name = profile.get("full_name", "")
            if isinstance(full_name, str):
                if "H:\\" in full_name or "Specialties:" in full_name or "Overseas assignments" in full_name:
                    continue
                if ":" in full_name and ("\\" in full_name or "/" in full_name):
                    continue

            nested_fields = [
                "skills", "experience", "education", "profiles",
                "certifications", "languages", "location_names",
                "regions", "countries", "street_addresses",
            ]

            for field in nested_fields:
                if field in profile:
                    profile[field] = parse_json_field(profile[field])

            if "experience" in profile and not isinstance(profile["experience"], list):
                profile["experience"] = []
            if "education" in profile and not isinstance(profile["education"], list):
                profile["education"] = []
            if "profiles" in profile and not isinstance(profile["profiles"], list):
                profile["profiles"] = []

            for key, value in profile.items():
                if value == "" or value == "[]" or isinstance(value, float) and pd.isna(value):
                    profile[key] = None

            if "skills" in profile:
                raw_skills = profile.get("skills")
                if isinstance(raw_skills, list):
                    cleaned = []
                    for s in raw_skills:
                        if s and isinstance(s, str) and s.strip():
                            if s.strip().startswith("+") and any(c.isdigit() for c in s.strip()):
                                continue
                            if not is_location(s.strip()):
                                cleaned.append(s.strip())
                    profile["skills"] = cleaned
                else:
                    profile["skills"] = []

            profile["location_name"] = extract_location(profile)

            if is_malformed_row(profile):
                continue

            if "job_title" in profile:
                profile["job_title"] = extract_title(profile.get("job_title"))

            if "summary" in profile:
                profile["summary"] = clean_summary(profile.get("summary"))
                if is_empty_summary(profile.get("summary")):
                    continue

            if profile.get("job_title") is None:
                has_valid_data = False
                for key in ["full_name", "first_name", "last_name"]:
                    if profile.get(key) and isinstance(profile.get(key), str):
                        has_valid_data = True
                        break
                if not has_valid_data:
                    continue

            profiles.append(profile)
        except Exception:
            continue

    return profiles


def get_all_skills(profiles: list[dict]) -> list[str]:
    """Extract all unique skills from profiles"""
    skills_set = set()
    for p in profiles:
        if p.get("skills") and isinstance(p["skills"], list):
            for skill in p["skills"]:
                if skill and isinstance(skill, str):
                    skill_clean = skill.strip()
                    if skill_clean and len(skill_clean) > 2:
                        skills_set.add(skill_clean)

    return sorted(skills_set)


def get_all_titles(profiles: list[dict]) -> list[str]:
    """Extract all unique job titles from profiles"""
    titles_set = set()
    for p in profiles:
        title = p.get("job_title")
        if title and isinstance(title, str):
            title_clean = title.strip()
            if title_clean and len(title_clean) > 2:
                titles_set.add(title_clean)

    return sorted(titles_set)
