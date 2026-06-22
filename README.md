# InterviewGenie 🧞‍♂️

AI-powered mock interview question predictor for any job posting. Paste a job description, company info, responsibilities, and requirements — instantly get a structured set of predicted interview questions with detailed answers, explanations, image placeholders, and real references.

![Tech Stack](https://img.shields.io/badge/stack-Flask%2C%20SQLAlchemy%2C%20DeepSeek%20API%2C%20Bootstrap%205-blue)

---

## ✨ Features

- **Field‑agnostic AI** – Works for tech, healthcare, finance, education, arts… any role.
- **Comprehensive Q&A** – General HR, role‑specific technical (basic → advanced), scenario‑based, company‑specific.
- **For every question** you get:
  - Step‑by‑step answer
  - In‑depth explanation
  - Image placeholder (with descriptive alt‑text)
  - Real web references (links to reputable sources)
- **Actions on each set**:
  - **Save** to your history (SQLite)
  - **Print** (browser dialog)
  - **Share** – generate a public link that expires in 7 days (no login needed)
  - **Download as PDF** – beautifully formatted with WeasyPrint
- **User accounts** – secure authentication, password hashing, session management.
- **Modern UI** – responsive Bootstrap 5 design, dark/light mode, smooth animations, card‑based layout.
- **Modular architecture** – easily swap the AI model (DeepSeek, OpenAI, Llama, etc.) via `ai_service.py`.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **uv** package manager: `pip install uv`
- **WeasyPrint system dependencies** (only for PDF export):
  - Ubuntu: `sudo apt install libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev`
  - macOS: `brew install pango gdk-pixbuf libffi`
  - Windows: see [WeasyPrint docs](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)

### 2. Clone & install
```bash
git clone https://github.com/your-username/interview-genie.git
cd interview-genie
uv sync
```

### 3. Set environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in:
```
SECRET_KEY=your-super-secret-key
DEEPSEEK_API_KEY=sk-...
```
(If you prefer OpenAI, set `OPENAI_API_KEY` instead and adjust `ai_service.py` – see below.)

### 4. Run the app
```bash
uv run python run.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) and start preparing for your dream job!

---

## 📦 Project Structure

```
interview-genie/
├── app/
│   ├── __init__.py           # Flask app factory, extensions, blueprint registration
│   ├── models.py             # User, ChatHistory, SharedLink (SQLAlchemy)
│   ├── forms.py              # WTForms for auth & settings
│   ├── routes/
│   │   ├── auth.py           # Login, signup, logout
│   │   ├── main.py           # Landing, dashboard, generation, save, share, PDF
│   │   ├── history.py        # Saved Q&A browsing, search, rename, delete
│   │   ├── share.py          # Public share view (no login required)
│   │   └── account.py        # Change password, delete account
│   ├── services/
│   │   ├── ai_service.py     # DeepSeek (or OpenAI) integration – abstracted
│   │   └── pdf_service.py    # WeasyPrint PDF generation from HTML template
│   ├── templates/            # Jinja2 templates (base, landing, dashboard, history, etc.)
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   └── utils/
│       └── helpers.py        # Decorators, token generation
├── .env.example              # Template for environment variables
├── .gitignore
├── pyproject.toml            # Dependencies & build config
├── uv.lock                   # Locked dependency versions
├── run.py                    # App entry point
└── README.md
```

---

## 🔧 Configuration & Environment

All sensitive values are loaded from a `.env` file using `python-dotenv`.

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask secret key for sessions & CSRF |
| `DEEPSEEK_API_KEY` | Yes (or `OPENAI_API_KEY`) | Your DeepSeek API key |
| `DATABASE_URL` | No | Database URI (defaults to `sqlite:///instance/app.db`) |

For OpenAI, swap the API key and change the client in `app/services/ai_service.py`:
```python
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),   # instead of DEEPSEEK_API_KEY
    base_url=None                           # remove base_url override
)
```
Then use `model="gpt-4o"` (or your preferred model).

---

## 🧠 AI Model Details

**Default model:** `deepseek-chat` (DeepSeek‑V3) via the OpenAI‑compatible endpoint.  
**Why DeepSeek?**
- Costs **~20× less** than GPT‑4o
- Matches GPT‑4o quality on structured outputs
- Native JSON mode support (`response_format: json_object`)
- 64K context window, generous rate limits

The AI service is fully decoupled – you can replace the `generate_interview_questions` function with any LLM call (Groq, Together, local Llama 3, etc.). The rest of the app never touches the model directly.

---

## 🎨 UI & UX

- **Bootstrap 5** + custom CSS (gradients, shadows, cards)
- **Dark/light mode** – persisted in localStorage, toggled via navbar button
- **AJAX generation** – no full page reload, loading spinner with progress feedback
- **Accordion display** – each Q&A neatly collapsed/expanded
- **Responsive** – mobile‑first design
- **Print styles** – browser print dialog works out‑of‑the‑box for the Q&A section

---

## 🔐 Authentication & Security

- **Flask‑Login** for session handling
- **Password hashing** via `werkzeug.security` (salted, secure)
- **CSRF protection** on all forms (Flask‑WTF)
- **SQLite** database with SQLAlchemy ORM (easily swapped for PostgreSQL)
- **Share links** expire after 7 days, contain cryptographically unique tokens
- **Account deletion** removes all user data permanently

---

## 📑 Database Models

**User** – `id`, `full_name`, `email` (unique), `password_hash`, `created_at`  
**ChatHistory** – `id`, `user_id` (FK), input fields, `full_generated_output` (JSON string), `title`, `created_at`  
**SharedLink** – `id`, `chat_history_id` (FK), `token` (unique), `expires_at`

The `full_generated_output` stores the exact structured JSON returned by the AI (including questions, answers, explanations, image URLs, references). This enables easy reloading and sharing.

---

## 🖨️ PDF Export

Uses **WeasyPrint** to render a dedicated HTML template (`pdf_template.html`) to a clean, styled PDF. The PDF includes:
- Header with app name, user’s name, and date
- All Q&A blocks with answers, explanations, images (external URLs), and references
- Page‑break‑friendly layout

No additional setup beyond WeasyPrint’s system libraries (see Prerequisites).

---

## 🗂️ History & Search

- Saved Q&A sets appear on the History page in a searchable, paginated card grid.
- Each item can be **viewed** (with full actions), **renamed**, or **deleted**.
- Clicking “View” reloads the original input and Q&A in the dashboard, enabling re‑save, share, or PDF download.

---

## 📤 Sharing

When a user clicks “Share” on a saved chat:
- A unique token is generated (UUID4)
- Stored in `SharedLink` with a 7‑day expiry
- The public URL (`/share/<token>`) shows the Q&A in a read‑only clean interface – no login required
- After expiry, the page gracefully informs the visitor

---

## 🛠️ Development & Customisation

### Adding a new AI provider
1. Edit `app/services/ai_service.py`
2. Modify the `client` and `generate_interview_questions` function
3. The return format must be a Python `list` of dicts with keys:  
   `question`, `answer`, `explanation`, `image_description`, `image_url`, `references`

### Changing database
Update `SQLALCHEMY_DATABASE_URI` in `app/__init__.py` or via the `.env` variable. SQLAlchemy will automatically handle the rest.

### Adding new routes
Create a new Blueprint in `app/routes/`, register it in `app/__init__.py`.

---

## ✅ Testing the API locally

You can test the AI generation endpoint with `curl`:
```bash
curl -X POST http://127.0.0.1:5000/generate \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <your-csrf-token>" \
  -d '{"job_description": "Python developer", "company_profile":"", "responsibilities":"", "requirements":""}'
```
(You must be logged in to get the CSRF token – easiest to test via the web UI.)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change. Follow PEP 8 and keep every line commented.

---

## 📄 License

https://github.com/tariqnasheed


---

**Now go land that job!** 💼🚀
```
