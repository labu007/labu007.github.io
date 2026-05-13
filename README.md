# 🎯 Smart Portfolio System

A **document-driven portfolio website** that automatically reads your CV/resume (`.docx` or `.pdf`) and updates your live site — no manual HTML editing required.

---

## 🗂 Project Structure

```
your-portfolio/
├── index.html              ← Your portfolio website (reads data/portfolio.json)
├── data/
│   └── portfolio.json      ← Auto-generated from your CV (commit this too)
├── docs-upload/
│   └── resume.docx         ← DROP YOUR CV HERE
├── scripts/
│   └── parse_document.py   ← Parser script (Python)
└── .github/
    └── workflows/
        └── parse_cv.yml    ← GitHub Actions automation
```

---

## 🚀 First-Time Setup (10 minutes)

### 1. Create your GitHub repo

```
yourusername.github.io
```

Set it to **Public**.

### 2. Upload all these files keeping the folder structure above

### 3. Enable GitHub Pages

`Settings → Pages → Branch: main → Folder: / (root) → Save`

### 4. Enable GitHub Actions

`Settings → Actions → General → Allow all actions → Save`

---

## 📄 How to Update Your Portfolio

It's a single step:

1. **Edit your CV** (Word or PDF) using the format below
2. **Upload it** to the `docs-upload/` folder on GitHub
3. **Wait ~60 seconds** — GitHub Actions parses it automatically
4. **Refresh your site** — it's updated

That's it. No HTML editing. No coding.

---

## 📝 Recommended CV Format (for best parsing)

Structure your Word/PDF document with these **exact section headings** (bold or Heading style):

```
YOUR FULL NAME
your.email@university.edu
+1 (555) 000-0000
City, Country
https://linkedin.com/in/yourname
https://github.com/yourusername
https://scholar.google.com/citations?user=XXXX

────────────────────────────

Summary

I am a graduate student in Data Science at the University of North Texas...

────────────────────────────

Education

Master of Science in Data Science — University of North Texas
2023 – Present
Thesis: A Novel Deep Learning Framework for EEG-Based Emotion Recognition
Advisor: Prof. [Name]
GPA: 3.9 / 4.0

Bachelor of Science in Computer Engineering — [University]
2019 – 2023
First Class Honours, GPA: 3.85/4.0
Dean's List 2022, 2023

────────────────────────────

Experience

Graduate Research Assistant — [Lab Name], University of North Texas
2023 – Present
Leading experiments in EEG signal classification
Developed preprocessing pipelines reducing time by 40%
Co-authored 2 papers under review

Data Science Intern — [Company], Dallas TX
Summer 2023
Built ML pipeline for customer churn prediction
Improved F1-score by 18% through feature engineering

────────────────────────────

Skills

Programming Languages: Python, MATLAB, R, C++, JavaScript
ML / AI: PyTorch, TensorFlow, Scikit-learn, HuggingFace
Data & Analysis: Pandas, NumPy, SQL, Tableau
Dev Tools: Git, Docker, Linux, LaTeX
Web & Viz: Streamlit, FastAPI, D3.js, Plotly

────────────────────────────

Projects

EEG Emotion Recognition Framework
type:research
Novel deep learning architecture achieving 94.2% accuracy on DEAP dataset
Outperforms SOTA by 8.3% using hybrid CNN-Transformer design
Manuscript in preparation for IEEE Transactions

Open-Source EEG Preprocessing Toolkit
type:engineering
Python library used by 12+ labs worldwide
200+ GitHub stars, fully documented

────────────────────────────

Publications

A Hybrid CNN-Transformer for EEG-Based Emotion Recognition
IEEE Transactions on Neural Systems and Rehabilitation Engineering
2024

Cross-Subject EEG Transfer Learning via Domain Adaptation
Proceedings of IEEE EMBC 2023
2023

────────────────────────────

Awards

Best Paper Award — IEEE EMBC 2024
2024
IEEE

Graduate Research Fellowship
2023
NSF

────────────────────────────

Certifications

Deep Learning Specialization — Coursera / Andrew Ng
2023
5-course specialization covering CNNs, RNNs, and Transformers
```

---

## 🔑 Section Heading Aliases

The parser recognises **many variations** of each section name:

| Section in site | Also detected as |
|---|---|
| Education | Academic Background, Academic Foundation, Degrees |
| Experience | Work Experience, Research Experience, Internships |
| Skills | Technical Skills, Core Competencies, Tools & Technologies |
| Projects | Research Projects, Key Projects, Selected Projects |
| Publications | Research Publications, Papers, Journal Articles |
| Awards | Honors, Achievements, Recognition, Scholarships |
| About | Summary, Profile, Objective, Overview |
| Certifications | Certificates, Online Courses, Professional Development |

---

## 🔄 Running Locally (optional)

```bash
# Install dependencies
pip install python-docx pymupdf

# Parse your document
python scripts/parse_document.py docs-upload/resume.docx

# Open the site locally — use a local server (not file://)
npx serve .
# or
python -m http.server 8000
```

> ⚠️ The site uses `fetch('./data/portfolio.json')` which requires an HTTP server, not `file://` direct open.

---

## ⚙️ How It Works

```
You push docs-upload/resume.docx
         ↓
GitHub Actions triggers (parse_cv.yml)
         ↓
parse_document.py runs
  ├── Detects .docx or .pdf
  ├── Extracts header (name, email, links)
  ├── Detects section headings automatically
  └── Structures content into typed objects
         ↓
data/portfolio.json written & committed
         ↓
index.html fetches portfolio.json on load
  ├── Renders hero with your name & stats
  ├── Builds every section dynamically
  └── Preserves all UI animations & dark mode
         ↓
GitHub Pages serves updated site ✅
```

---

## 🛡 Security Notes

- No API keys or secrets needed
- All parsing runs inside GitHub Actions (free)
- `portfolio.json` is public — don't put private info in your CV
- GitHub Pages is static — no server, no database

---

## 🔧 Customisation Tips

**Change accent color:** In `index.html` find `--a: #00e5b0;` and replace with any hex color.

**Add your profile photo:** Replace the initials avatar with an `<img>` tag in `buildHero()`.

**Add a section (e.g. Leadership):** Add a builder function in `index.html` following the same pattern, and add the heading alias to `SECTION_MAP` in `parse_document.py`.

**Manual override:** Edit `data/portfolio.json` directly for any field you want full control over.
