# 🎯 Dibakar Barua — Smart Portfolio System

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
DIBAKAR BARUA
Denton, TX | 940-597-7847 | dibakarlabu@gmail.com | LinkedIn

PROFESSIONAL SUMMARY
Machine Learning Engineer and Data Scientist with 3+ years of experience...

EDUCATION
M.Sc. in Data Science
University of North Texas | Denton, TX
Expected Dec 2026 | GPA: 3.91 / 4.00
Coursework: Machine Learning, Deep Learning, ...

B.Sc. in Computer Science and Software Engineering
American International University Bangladesh | Dhaka, Bangladesh
Aug 2021 | GPA: 3.95 / 4.00
Dean's Honors List, Summa Cum Laude

EXPERIENCE
Graduate Research Assistant — Computer Vision / Deep Learning
Visual Computing & Biometric Security Lab, University of North Texas
Aug 2025 – Present
• Conducting computer vision research on Autism Spectrum Disorder (ASD) detection...
• Designing and evaluating deep learning architectures...

Junior Machine Learning Engineer
Brain Station 23 | Dhaka, Bangladesh
Mar 2022 – Dec 2024
• Designed and delivered end-to-end ML pipelines...
• Cleaned and preprocessed datasets with 100K+ records...

TECHNICAL SKILLS
Programming Languages: Python, SQL, C#, C++, Java, MATLAB
ML / Deep Learning: PyTorch, TensorFlow, Keras, Scikit-learn, XGBoost, LSTM, CNN
NLP & Generative AI: BERT, GPT, HuggingFace Transformers, RAG, LLM Fine-tuning
Computer Vision: OpenCV, EfficientNet-B0, ResNet-50, Grad-CAM
Data Science & Analytics: Pandas, NumPy, SciPy, Feature Engineering, A/B Testing
MLOps & Tools: Docker, Git, Streamlit, REST APIs, Model Deployment
Databases & Cloud: AWS S3, AWS EC2, MySQL, Oracle Database
Visualization: Tableau, Power BI, Matplotlib, Seaborn

MACHINE LEARNING & DATA SCIENCE PROJECTS
PhysicsDenoiseNet | Deep Learning — Image Denoising | Jan – Apr 2026
• Built a physics-informed deep learning model for real-world image denoising...
• Trained on SIDD Small, BSD68, and LOL benchmark datasets...

Clickbait Headline Detection | NLP / Web App | Jan – Apr 2025
• Built and compared Logistic Regression, LSTM, and fine-tuned BERT classifiers...
• BERT achieved 99% classification accuracy...

PUBLICATIONS & RESEARCH
Speaking at the Right Level: Literacy-Controlled Counterspeech Generation with RAG-RL
EMNLP 2025 | Aug 2025
• Developed an LLM-based counterspeech generation system combining RAG and RL...

Autism Spectrum Disorder (ASD) Prediction Using Machine Learning
IJITCS | Aug 2022
• Developed a hybrid SVM + CNN model achieving 94% accuracy...
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
    "name": "Dibakar Barua",
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
