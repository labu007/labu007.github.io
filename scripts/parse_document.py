#!/usr/bin/env python3
"""
portfolio-system/scripts/parse_document.py
-------------------------------------------
Reads a .docx or .pdf resume/CV and writes structured data to
data/portfolio.json for the frontend to consume.

Usage:
    python parse_document.py ../docs-upload/resume.docx
    python parse_document.py ../docs-upload/resume.pdf
"""

import sys
import json
import re
import os
from pathlib import Path

# ─── Section aliases ────────────────────────────────────────────────────────
# Maps any heading variant found in a document → a canonical section key.
SECTION_MAP = {
    # education
    "education": "education",
    "academic background": "education",
    "academic foundation": "education",
    "academic qualifications": "education",
    "qualifications": "education",
    "degrees": "education",

    # experience
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "research experience": "experience",
    "industry experience": "experience",
    "internships": "experience",

    # skills
    "skills": "skills",
    "technical skills": "skills",
    "technical expertise": "skills",
    "core competencies": "skills",
    "competencies": "skills",
    "tools & technologies": "skills",
    "tools and technologies": "skills",
    "programming languages": "skills",

    # projects
    "projects": "projects",
    "research projects": "projects",
    "key projects": "projects",
    "selected projects": "projects",
    "portfolio": "projects",

    # publications
    "publications": "publications",
    "research publications": "publications",
    "papers": "publications",
    "journal articles": "publications",
    "conference papers": "publications",
    "preprints": "publications",

    # awards
    "awards": "awards",
    "honors": "awards",
    "honours": "awards",
    "achievements": "awards",
    "awards & honors": "awards",
    "awards and honors": "awards",
    "recognition": "awards",
    "scholarships": "awards",

    # about / summary
    "summary": "about",
    "about": "about",
    "profile": "about",
    "objective": "about",
    "professional summary": "about",
    "about me": "about",
    "overview": "about",

    # certifications
    "certifications": "certifications",
    "certificates": "certifications",
    "courses": "certifications",
    "online courses": "certifications",
    "professional development": "certifications",

    # leadership
    "leadership": "leadership",
    "service": "leadership",
    "volunteer": "leadership",
    "community service": "leadership",
    "extracurricular": "leadership",
    "activities": "leadership",
}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()

def detect_section(text: str) -> str | None:
    """Return canonical section key if text looks like a section heading."""
    key = normalise(text)
    return SECTION_MAP.get(key)

def looks_like_heading(para) -> bool:
    """Heuristic for docx paragraphs: bold, short, all-caps, or heading style."""
    t = para.text.strip()
    if not t:
        return False
    if para.style and para.style.name and para.style.name.startswith("Heading"):
        return True
    # Bold + short
    all_bold = all(run.bold for run in para.runs if run.text.strip())
    if all_bold and len(t) < 60:
        return True
    # ALL CAPS short line
    if t.isupper() and len(t) < 60:
        return True
    return False

def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

# ─── DOCX parser ─────────────────────────────────────────────────────────────

def parse_docx(path: str) -> dict:
    from docx import Document
    doc = Document(path)
    sections: dict[str, list[str]] = {}
    current = None
    header_info: dict = {}   # name, email, links etc. from top of doc

    # First pass: grab contact info from the very first non-section lines
    preamble_done = False

    for para in doc.paragraphs:
        text = clean(para.text)
        if not text:
            continue

        # Check if this paragraph is a section heading
        sec = detect_section(text)
        if sec or looks_like_heading(para):
            resolved = sec if sec else None
            if resolved:
                current = resolved
                if current not in sections:
                    sections[current] = []
                preamble_done = True
                continue
            else:
                # Unknown heading — treat as new unlabelled block, keep current
                pass

        if not preamble_done:
            # We're still in the header area — try to extract contact info
            _extract_contact(text, header_info)
            # If no section yet and this is name-like (first non-empty line)
            if "name" not in header_info:
                header_info["name"] = text
            continue

        if current:
            sections[current].append(text)

    return {"header": header_info, "sections": sections}

def _extract_contact(text: str, info: dict):
    email_m = re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
    if email_m:
        info["email"] = email_m.group()
    phone_m = re.search(r"[\+\d][\d\s\-\(\)]{7,}", text)
    if phone_m:
        info["phone"] = phone_m.group().strip()
    url_m = re.search(r"(https?://\S+|linkedin\.com\S*|github\.com\S*)", text, re.I)
    if url_m:
        u = url_m.group()
        if "linkedin" in u.lower():
            info["linkedin"] = u
        elif "github" in u.lower():
            info["github"] = u
        else:
            info.setdefault("links", []).append(u)
    loc_m = re.search(r"\b([A-Z][a-z]+(?:,\s*[A-Z]{2,})?)\b", text)
    if loc_m and "location" not in info and len(text) < 40:
        info["location"] = text

# ─── PDF parser ──────────────────────────────────────────────────────────────

def parse_pdf(path: str) -> dict:
    import fitz  # pymupdf
    doc = fitz.open(path)
    sections: dict[str, list[str]] = {}
    current = None
    header_info: dict = {}
    preamble_done = False
    all_lines: list[tuple[str, float]] = []  # (text, font_size)

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                line_text = " ".join(span["text"] for span in line["spans"]).strip()
                if not line_text:
                    continue
                # Use max font size in line as heading indicator
                max_size = max(span["size"] for span in line["spans"])
                all_lines.append((line_text, max_size))

    # Determine heading threshold: lines significantly larger than median body size
    if all_lines:
        sizes = sorted(s for _, s in all_lines)
        median_size = sizes[len(sizes) // 2]
        heading_threshold = median_size * 1.15
    else:
        heading_threshold = 13.0

    for text, size in all_lines:
        cleaned = clean(text)
        if not cleaned:
            continue

        sec = detect_section(cleaned)
        is_heading = size >= heading_threshold or cleaned.isupper()

        if sec:
            current = sec
            if current not in sections:
                sections[current] = []
            preamble_done = True
            continue
        elif is_heading and not preamble_done:
            # Likely the person's name at the top
            if "name" not in header_info:
                header_info["name"] = cleaned
            continue

        if not preamble_done:
            _extract_contact(cleaned, header_info)
            continue

        if current:
            sections[current].append(cleaned)

    return {"header": header_info, "sections": sections}

# ─── Post-processor: structure raw lines into typed objects ──────────────────

def structure_sections(raw: dict) -> dict:
    """
    Convert raw line lists into typed structured objects per section.
    This is a best-effort heuristic — works well for standard CV formats.
    """
    out = {}
    s = raw.get("sections", {})

    # ABOUT: just join paragraphs
    if "about" in s:
        out["about"] = {"bio": " ".join(s["about"])}

    # EDUCATION
    if "education" in s:
        out["education"] = _parse_entries(s["education"], kind="education")

    # EXPERIENCE
    if "experience" in s:
        out["experience"] = _parse_entries(s["experience"], kind="experience")

    # SKILLS: try to detect categories
    if "skills" in s:
        out["skills"] = _parse_skills(s["skills"])

    # PROJECTS
    if "projects" in s:
        out["projects"] = _parse_entries(s["projects"], kind="project")

    # PUBLICATIONS
    if "publications" in s:
        out["publications"] = _parse_publications(s["publications"])

    # AWARDS
    if "awards" in s:
        out["awards"] = _parse_awards(s["awards"])

    # CERTIFICATIONS
    if "certifications" in s:
        out["certifications"] = _parse_entries(s["certifications"], kind="cert")

    # LEADERSHIP
    if "leadership" in s:
        out["leadership"] = _parse_entries(s["leadership"], kind="leadership")

    return out

def _parse_entries(lines: list[str], kind: str) -> list[dict]:
    """Group lines into entry dicts. Each entry starts with a 'title' line."""
    entries = []
    current: dict | None = None
    for line in lines:
        line = clean(line)
        if not line:
            continue
        # Year pattern signals a new entry boundary
        year_m = re.search(r"\b(19|20)\d{2}\b", line)
        # Short line (< 80 chars) with no leading dash/bullet = likely a title
        is_title = len(line) < 90 and not line.startswith(("-", "•", "·", "*", "–"))
        if is_title and (year_m or (current is None)):
            if current:
                entries.append(current)
            current = {"title": line, "details": [], "year": ""}
            if year_m:
                current["year"] = year_m.group()
        else:
            if current is None:
                current = {"title": line, "details": [], "year": ""}
            else:
                current["details"].append(line.lstrip("-•·* –").strip())
    if current:
        entries.append(current)
    return entries

def _parse_skills(lines: list[str]) -> list[dict]:
    """Detect skill categories (e.g. 'Languages: Python, R') or flat lists."""
    categories = []
    cat: dict | None = None
    for line in lines:
        line = clean(line)
        if not line:
            continue
        # Category header pattern: "Label: item1, item2" or "Label:" alone
        cat_m = re.match(r"^([A-Za-z &/]+):\s*(.*)", line)
        if cat_m:
            label = cat_m.group(1).strip()
            items_str = cat_m.group(2).strip()
            items = [i.strip() for i in re.split(r"[,;|]", items_str) if i.strip()]
            if cat:
                categories.append(cat)
            cat = {"category": label, "items": items}
        else:
            items = [i.strip() for i in re.split(r"[,;|•·]", line) if i.strip()]
            if cat:
                cat["items"].extend(items)
            else:
                cat = {"category": "General", "items": items}
    if cat:
        categories.append(cat)
    return categories

def _parse_publications(lines: list[str]) -> list[dict]:
    pubs = []
    current = None
    for line in lines:
        line = clean(line)
        if not line:
            continue
        year_m = re.search(r"\b(20\d{2}|19\d{2})\b", line)
        if year_m or (current is None):
            if current:
                pubs.append(current)
            current = {
                "title": line,
                "year": year_m.group() if year_m else "",
                "venue": "",
                "type": "journal" if any(w in line.lower() for w in ["journal","ieee","nature","science"]) else "conference"
            }
        else:
            if current:
                if not current["venue"]:
                    current["venue"] = line
    if current:
        pubs.append(current)
    return pubs

def _parse_awards(lines: list[str]) -> list[dict]:
    awards = []
    for line in lines:
        line = clean(line)
        if not line:
            continue
        year_m = re.search(r"\b(20\d{2}|19\d{2})\b", line)
        awards.append({
            "name": line,
            "year": year_m.group() if year_m else "",
            "org": ""
        })
    return awards

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_document.py <path/to/resume.docx|pdf>")
        sys.exit(1)

    doc_path = sys.argv[1]
    if not os.path.exists(doc_path):
        print(f"❌  File not found: {doc_path}")
        sys.exit(1)

    ext = Path(doc_path).suffix.lower()
    print(f"📄  Parsing {ext.upper()} file: {doc_path}")

    if ext == ".docx":
        raw = parse_docx(doc_path)
    elif ext == ".pdf":
        raw = parse_pdf(doc_path)
    else:
        print("❌  Unsupported file type. Use .docx or .pdf")
        sys.exit(1)

    structured = structure_sections(raw)

    output = {
        "meta": {
            "source_file": Path(doc_path).name,
            "generated": __import__("datetime").datetime.utcnow().isoformat() + "Z"
        },
        "header": raw.get("header", {}),
        "sections": structured
    }

    out_path = Path(__file__).parent.parent / "data" / "portfolio.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅  Extracted sections: {list(structured.keys())}")
    print(f"📦  Written to: {out_path}")

if __name__ == "__main__":
    main()
