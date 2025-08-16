# Flask + SQLite User Authentication

A clean, minimal user authentication system built with **Flask** and **SQLite**.

## Features
- Register, Login, Logout
- Password hashing (Werkzeug)
- Session-based auth
- SQLite database (auto-initialized)
- Project structured for easy deployment & testing

## Project Structure
```
flask_auth/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── instance/
│   └── database.db (auto-created)
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   └── 404.html
└── static/
    └── style.css
```

## Quick Start

```bash
# 1) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) (Optional) set a secure secret key
export SECRET_KEY='change-this-in-production'  # Windows PowerShell: $env:SECRET_KEY='...'

# 4) Initialize DB (will be auto-initialized on first run too)
flask --app app.py init-db

# 5) Run the app
flask --app app.py run
# or
python app.py
```

Visit http://127.0.0.1:5000

## Notes
- The **instance/** folder stores the SQLite database. It is created automatically.
- Change `SECRET_KEY` in production.
- To reset the DB, delete `instance/database.db` and run `flask --app app.py init-db`.

## License
MIT
