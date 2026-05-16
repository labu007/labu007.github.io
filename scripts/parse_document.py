#!/usr/bin/env python3
"""
portfolio-system/scripts/parse_document.py
-------------------------------------------
Reads a .docx or .pdf resume and writes structured data to
data/portfolio.json for the frontend to consume.

Usage:
    python parse_document.py ../docs-upload/Dibakar_Barua_Resume.pdf
    python parse_document.py ../docs-upload/Dibakar_Barua_Resume.docx

Schema output (data/portfolio.json):
    header      → name, email, phone, location, linkedin, github
    about       → bio (professional summary)
    education   → list of { degree, institution, location, year, gpa, details[] }
    experience  → list of { role, org, location, period, details[] }
    skills      → dict of { category: [skill, ...] }
    projects    → list of { name, type, period, details[] }
    publications→ list of { title, venue, org, year, abstract }
    awards      → list of { name, year, org }
"""

import sys, re, json, os
from pathlib import Path
from datetime import datetime

# ─── Section aliases ────────────────────────────────────────────────────────
SECTION_MAP = {
    # education
    "education": "education",
    "academic background": "education",
    "academic foundation": "education",
    "qualifications": "education",
    # experience
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "employment": "experience",
    "research experience": "experience",
    # skills
    "skills": "skills",
    "technical skills": "skills",
    "technical expertise": "skills",
    "core competencies": "skills",
    "technologies": "skills",
    # projects
    "projects": "projects",
    "machine learning & data science projects": "projects",
    "ml & data science projects": "projects",
    "selected projects": "projects",
    "research projects": "projects",
    # publications
    "publications": "publications",
    "publications & research": "publications",
    "research publications": "publications",
    "papers": "publications",
    # awards
    "awards": "awards",
    "honors": "awards",
    "achievements": "awards",
    "certifications": "awards",
    "honors & awards": "awards",
    # summary / about
    "summary": "about",
    "professional summary": "about",
    "about": "about",
    "profile": "about",
    "objective": "about",
}

# Skill category keywords for grouping
SKILL_CATEGORIES = [
    "programming languages",
    "ml",
    "deep learning",
    "nlp",
    "generative ai",
    "computer vision",
    "data science",
    "analytics",
    "mlops",
    "tools",
    "databases",
    "cloud",
    "visualization",
]

# ─── Text extraction ─────────────────────────────────────────────────────────

def extract_text_pdf(path: str) -> list[str]:
    """Extract lines from PDF using PyMuPDF."""
    try:
        import fitz  # pymupdf
        doc = fitz.open(path)
        lines = []
        for page in doc:
            for line in page.get_text("text").splitlines():
                lines.append(line)
        return lines
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. Run: pip install pymupdf")

def extract_text_docx(path: str) -> list[str]:
    """Extract lines from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(path)
        lines = []
        for para in doc.paragraphs:
            lines.append(para.text)
        return lines
    except ImportError:
        raise RuntimeError("python-docx not installed. Run: pip install python-docx")

def extract_lines(path: str) -> list[str]:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return extract_text_pdf(path)
    elif ext == ".docx":
        return extract_text_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .pdf or .docx")

# ─── Header parsing ──────────────────────────────────────────────────────────

EMAIL_RE  = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE  = re.compile(r"[\+\(]?[0-9][0-9\s\-\(\)]{7,}[0-9]")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.I)
GITHUB_RE   = re.compile(r"github\.com/[\w\-]+", re.I)

def parse_header(lines: list[str]) -> dict:
    header = {"name": "", "email": "", "phone": "", "location": "", "linkedin": "", "github": "", "links": []}
    # First non-empty line is likely the name
    for line in lines[:8]:
        stripped = line.strip()
        if stripped and not EMAIL_RE.search(stripped) and not PHONE_RE.search(stripped):
            if len(stripped.split()) >= 2 and stripped[0].isupper():
                header["name"] = stripped
                break

    for line in lines[:20]:
        if EMAIL_RE.search(line) and not header["email"]:
            header["email"] = EMAIL_RE.search(line).group()
        if PHONE_RE.search(line) and not header["phone"]:
            raw = PHONE_RE.search(line).group().strip()
            header["phone"] = raw
        if LINKEDIN_RE.search(line) and not header["linkedin"]:
            m = LINKEDIN_RE.search(line).group()
            header["linkedin"] = "https://" + m
        if GITHUB_RE.search(line) and not header["github"]:
            m = GITHUB_RE.search(line).group()
            header["github"] = "https://" + m
        # location heuristic: "City, ST" or "City, Country"
        loc_match = re.search(r"[A-Z][a-z]+(,\s*[A-Z]{2}|,\s*[A-Z][a-z]+)", line)
        if loc_match and not header["location"] and "linkedin" not in line.lower():
            header["location"] = loc_match.group()
    return header

# ─── Section splitter ────────────────────────────────────────────────────────

def split_sections(lines: list[str]) -> dict[str, list[str]]:
    """Split raw lines into named sections."""
    sections: dict[str, list[str]] = {"_header": []}
    current = "_header"
    header_done = False

    for line in lines:
        stripped = line.strip()
        key = stripped.lower().rstrip(":").strip()

        if key in SECTION_MAP:
            current = SECTION_MAP[key]
            header_done = True
            if current not in sections:
                sections[current] = []
            continue

        if not header_done:
            sections["_header"].append(line)
        else:
            if current not in sections:
                sections[current] = []
            sections[current].append(line)

    return sections

# ─── Section parsers ─────────────────────────────────────────────────────────

def parse_about(lines: list[str]) -> dict:
    bio = " ".join(l.strip() for l in lines if l.strip())
    return {"bio": bio}

def parse_education(lines: list[str]) -> list[dict]:
    entries = []
    current = None
    for line in lines:
        s = line.strip()
        if not s:
            continue
        # New entry if line looks like a degree title
        degree_kws = ["b.sc", "m.sc", "phd", "bachelor", "master", "doctor",
                      "b.s.", "m.s.", "b.e.", "m.e.", "mba"]
        is_degree = any(kw in s.lower() for kw in degree_kws)
        # Or institution line (ends with year range or "Present")
        is_institution = re.search(r"\d{4}", s) and len(s.split()) <= 10

        if is_degree:
            if current:
                entries.append(current)
            current = {"degree": s, "institution": "", "location": "", "year": "", "gpa": "", "details": []}
        elif current and not current["institution"] and "university" in s.lower() or "institute" in s.lower() or "college" in s.lower():
            current["institution"] = s
        elif current and re.search(r"\d{4}", s) and not current["year"]:
            current["year"] = s
        elif current and re.search(r"gpa|cgpa|grade", s, re.I):
            current["gpa"] = s
        elif current:
            current["details"].append(s)

    if current:
        entries.append(current)
    return entries

def parse_experience(lines: list[str]) -> list[dict]:
    entries = []
    current = None

    for line in lines:
        s = line.strip()
        if not s:
            continue
        # Detect new role: line with a dash/em-dash separating role from org, or role-like capitalized line
        is_role = ("—" in s or " - " in s or re.match(r"^[A-Z][^a-z]{0,3}[A-Z]", s)) and len(s.split()) <= 15
        is_period = re.search(r"\d{4}\s*[–\-]\s*(\d{4}|Present|present|Current|current)", s)
        is_bullet = s.startswith("•") or s.startswith("-") or s.startswith("·")

        if is_period and not is_bullet:
            if current:
                # period belongs to current entry
                current["period"] = s
        elif is_bullet:
            if current:
                current["details"].append(s.lstrip("•-· ").strip())
        elif is_role and not is_bullet and len(s) > 8:
            if current:
                entries.append(current)
            current = {"role": s, "org": "", "location": "", "period": "", "details": []}
        elif current and not current["org"] and len(s) > 3:
            # Check if it looks like an org/company line
            if not re.search(r"\d{4}", s):
                current["org"] = s
        elif current:
            current["details"].append(s)

    if current:
        entries.append(current)
    return entries

def parse_skills(lines: list[str]) -> dict:
    """Parse skills into categories."""
    result = {}
    current_category = "General"

    for line in lines:
        s = line.strip()
        if not s:
            continue
        # Detect category header: ends with colon or matches known categories
        if s.endswith(":") or any(kw in s.lower() for kw in SKILL_CATEGORIES):
            current_category = s.rstrip(":")
            result[current_category] = []
        else:
            # Split by comma, semicolon, or pipe
            skills = re.split(r"[,;|]", s)
            skills = [sk.strip() for sk in skills if sk.strip()]
            if current_category not in result:
                result[current_category] = []
            result[current_category].extend(skills)

    return result

def parse_projects(lines: list[str]) -> list[dict]:
    entries = []
    current = None

    for line in lines:
        s = line.strip()
        if not s:
            continue
        is_bullet = s.startswith("•") or s.startswith("-") or s.startswith("·")
        is_period = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*(20\d\d)", s)

        if is_bullet:
            if current:
                current["details"].append(s.lstrip("•-· ").strip())
        elif is_period and current:
            current["period"] = s
        elif not is_bullet and len(s) > 5 and s[0].isupper():
            if "|" in s or "—" in s:
                parts = re.split(r"[|—]", s)
                if current:
                    entries.append(current)
                current = {"name": parts[0].strip(), "type": parts[1].strip() if len(parts) > 1 else "", "period": "", "details": []}
            else:
                if current:
                    entries.append(current)
                current = {"name": s, "type": "", "period": "", "details": []}
        elif current:
            current["details"].append(s)

    if current:
        entries.append(current)
    return entries

def parse_publications(lines: list[str]) -> list[dict]:
    entries = []
    current = None
    for line in lines:
        s = line.strip()
        if not s:
            continue
        is_bullet = s.startswith("•") or s.startswith("-")
        is_venue = re.search(r"(EMNLP|IJITCS|NeurIPS|ICML|ACL|ICLR|CVPR|ICCV|AAAI|arXiv|IEEE|ACM)", s)
        is_year = re.match(r"(Published|Accepted|Submitted)?\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*20\d\d", s)

        if is_bullet:
            if current:
                current["abstract"] = (current.get("abstract", "") + " " + s.lstrip("•- ")).strip()
        elif is_venue and current:
            current["venue"] = s
        elif is_year and current:
            current["year"] = s
        elif not is_bullet and len(s) > 10 and s[0].isupper():
            if current:
                entries.append(current)
            current = {"title": s, "venue": "", "org": "", "year": "", "abstract": ""}
        elif current:
            current["abstract"] = (current.get("abstract", "") + " " + s).strip()

    if current:
        entries.append(current)
    return entries

def parse_awards(lines: list[str]) -> list[dict]:
    entries = []
    for line in lines:
        s = line.strip().lstrip("•-· ")
        if not s:
            continue
        year_m = re.search(r"20\d\d", s)
        entries.append({
            "name": re.sub(r"\s*20\d\d\s*", "", s).strip(" |—-"),
            "year": year_m.group() if year_m else "",
            "org": ""
        })
    return entries

# ─── Main assembler ──────────────────────────────────────────────────────────

def parse_resume(path: str) -> dict:
    lines = extract_lines(path)
    raw_sections = split_sections(lines)

    header = parse_header(raw_sections.get("_header", []))

    result = {
        "meta": {
            "source_file": Path(path).name,
            "generated": datetime.utcnow().isoformat() + "Z",
            "version": "2.0"
        },
        "header": header,
        "sections": {}
    }

    parser_map = {
        "about":        parse_about,
        "education":    parse_education,
        "experience":   parse_experience,
        "skills":       parse_skills,
        "projects":     parse_projects,
        "publications": parse_publications,
        "awards":       parse_awards,
    }

    for section_key, parser_fn in parser_map.items():
        raw = raw_sections.get(section_key, [])
        if raw:
            result["sections"][section_key] = parser_fn(raw)

    return result

# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_document.py <path/to/resume.pdf|.docx>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = Path(__file__).parent.parent / "data" / "portfolio.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📄 Parsing: {input_path}")
    data = parse_resume(input_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Written to: {output_path}")
    print(f"   Name:         {data['header']['name']}")
    print(f"   Sections:     {list(data['sections'].keys())}")
    for k, v in data['sections'].items():
        count = len(v) if isinstance(v, list) else len(v.keys()) if isinstance(v, dict) else 1
        print(f"   └─ {k}: {count} item(s)")
