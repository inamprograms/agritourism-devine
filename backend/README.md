Agritourism Devine – Backend

Backend application for the Agritourism Devine Phase 1 MVP, built using Flask.

This service provides REST APIs consumed by the frontend application. It handles server-side processing and integrates with Supabase for data storage. The backend is designed for local development and MVP-level usage.

Tech Stack

Python

Flask

Flask-CORS

Supabase (Python client)

Prerequisites

Python 3.9 or later

pip

Git

Local Setup
Navigate to the backend directory
cd backend

Create a virtual environment
python -m venv venv

Activate the virtual environment

Windows

venv\Scripts\activate


macOS / Linux

source venv/bin/activate

Install dependencies
pip install -r requirements.txt

Environment Variables

Create a .env file in the backend directory by copying the example file:

cp .env.example .env


Update .env with the required values:

FLASK_ENV=development
FLASK_APP=app/__main__.py
FLASK_RUN_PORT=5000

SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

Start the Development Server
flask run


or

python app/__main__.py

Backend URL

The backend will be available at:

http://localhost:5000


Ensure this matches the frontend configuration:

VITE_BACKEND_URL=http://localhost:5000

Notes

This backend is intended for local development and MVP usage

Environment files (.env) are excluded from version control

Virtual environments should not be committed to GitHub
