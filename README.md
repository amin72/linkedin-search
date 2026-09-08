```markdown
# LinkedIn Profile Search Application

A production-grade LinkedIn profile search engine built with FastAPI and vanilla JavaScript.

## Features

- Keyword search across names, skills, companies, titles, and summaries
- Filter profiles by skills and job titles
- Pagination with page controls
- Profile cards displaying name, job title, company, location, skills, summary, and LinkedIn links
- Automatic parsing and cleaning of nested JSON fields from CSV data

## Tech Stack

**Backend:** FastAPI, Pandas, Pydantic, Python 3.10+

**Frontend:** Vanilla JavaScript, jQuery, Pico CSS

## Project Structure

```
backend/
├── app.py          # FastAPI application entry point
├── routes.py       # API route definitions
├── data.py         # Data loading and caching
├── data_loader.py  # CSV parsing and cleaning
├── search.py       # Search and filtering logic
├── models.py       # Pydantic models
└── dataset.csv     # LinkedIn profile data

frontend/
├── index.html      # Main HTML page
├── script.js       # Frontend logic
└── style.css       # Custom styles
```

## Installation

### Backend Setup

```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
python -m http.server 3000
```

Open http://localhost:3000 in your browser.

## API Endpoints

### GET /api/search
Search and filter LinkedIn profiles.

**Parameters:**
- `q` - Search keyword
- `skill` - Filter by skill
- `title` - Filter by job title
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 10, max: 100)

### GET /api/filters
Get available skills and job titles.

### GET /api/profiles
Get all profiles (debugging endpoint).

## Development

```bash
ruff check backend/
ruff format backend/
```

## License

MIT
```