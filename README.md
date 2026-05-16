# Portfolio System

A **document-driven portfolio website** that automatically reads your resume (`.docx` or `.pdf`) and updates your live site. No manual HTML editing required.

---

## 🗂 Project Structure

```
portfolio-system/
├── index.html                     ← Portfolio website (reads data/portfolio.json)
├── data/
│   └── portfolio.json             ← Auto-generated from your resume (commit this)
├── docs-upload/
│   └── Dibakar_Barua_Resume.pdf   ← DROP YOUR RESUME HERE to trigger auto-update
├── scripts/
│   └── parse_document.py          ← Python parser (PDF + DOCX)
└── .github/
    └── workflows/
        └── parse_cv.yml           ← GitHub Actions automation
```

---

## 🚀 First-Time Setup (10 minutes)

### 1. Create your GitHub repo

Name it: `yourusername.github.io` → Set to **Public**

### 2. Upload all files preserving the folder structure above

### 3. Enable GitHub Pages

`Settings → Pages → Branch: main → Folder: / (root) → Save`

### 4. Enable GitHub Actions

`Settings → Actions → General → Allow all actions → Save`

Your site is live at `https://yourusername.github.io`

---

## 📄 How to Update Your Portfolio

1. **Edit your resume** (PDF or DOCX) using the format below
2. **Upload it** to the `docs-upload/` folder on GitHub
3. **Wait ~60 seconds** — GitHub Actions parses it automatically
4. **Refresh your site** — content is updated ✅

---

## 📝 Recommended Resume Format (for best auto-parsing)

Structure your PDF or Word doc with these **exact section headings**:

```
First_Name Last_Name
Address | Contact | email | LinkedIn

PROFESSIONAL SUMMARY
Write summary of your own.

EDUCATION


EXPERIENCE


TECHNICAL SKILLS


MACHINE LEARNING & DATA SCIENCE PROJECTS

```

---

## 🔧 Running the Parser Locally

```bash
# Install dependencies
pip install pymupdf python-docx

# Parse your resume
python scripts/parse_document.py docs-upload/Dibakar_Barua_Resume.pdf

# Output: data/portfolio.json (auto-generated)
```

---

## 🗂 portfolio.json Schema

```json
{
  "meta": { "source_file": "...", "generated": "...", "version": "2.0" },
  "header": {
    "name": "First_name Last_name",
    "email": "...", "phone": "...", "location": "...",
    "linkedin": "...", "github": "..."
  },
  "sections": {
    "about":    { "bio": "..." },
    "education":    [ { "degree": "...", "institution": "...", "location": "...", "year": "...", "gpa": "...", "details": [] } ],
    "experience":   [ { "role": "...", "org": "...", "location": "...", "period": "...", "details": [] } ],
    "skills":       { "Category": ["skill1", "skill2"] },
    "projects":     [ { "name": "...", "type": "...", "period": "...", "details": [] } ],
    "publications": [ { "title": "...", "venue": "...", "org": "...", "year": "...", "abstract": "..." } ],
    "awards":       [ { "name": "...", "year": "...", "org": "..." } ]
  }
}
```

---

## 🎨 Design Features

- Dark editorial aesthetic with frosted glass cards
- Playfair Display serif headings + DM Sans body + DM Mono for labels
- Responsive mobile navigation with hamburger menu
- **📸 Background photo upload** — click "Set Background" (bottom-right) to upload any photo as the full-page background
- Smooth section animations on load
- Gold accent color system throughout

---

## ⚙️ Supported Section Aliases

The parser recognizes these section headings (case-insensitive):

| Heading in your document | Maps to |
|---|---|
| Education / Academic Foundation | education |
| Experience / Work Experience / Professional Experience | experience |
| Skills / Technical Skills / Technical Expertise | skills |
| Projects / Machine Learning & Data Science Projects | projects |
| Publications / Publications & Research | publications |
| Awards / Honors / Achievements | awards |
| Summary / Professional Summary / About | about |
