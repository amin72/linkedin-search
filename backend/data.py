import os

from data_loader import get_all_skills, get_all_titles, load_profiles

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
