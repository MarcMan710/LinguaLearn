# LinguaLearn

LinguaLearn is a comprehensive language learning platform designed to help users master new languages through interactive lessons, personalized practice, and gamified experiences.

## Features

*   **Structured Courses:** Browse courses by language level (Beginner to Mastery).
*   **Diverse Lesson Types:** Engage with Vocabulary, Grammar, and Listening lessons.
*   **Interactive Learning:**
    *   Vocabulary items with translations, examples, and pronunciation.
    *   Grammar rules with explanations and practice exercises.
    *   Audio tasks with transcripts and questions.
*   **Pronunciation Practice:** Exercises with AI-powered feedback (requires OpenAI API key).
*   **User Progress Tracking:** Monitor completed lessons and scores.
*   **Gamification:**
    *   Earn XP for activities and level up.
    *   Maintain daily streaks.
    *   Unlock achievements.
*   **Leaderboards:** Compete with other learners.
*   **Personalization:**
    *   Set user preferences for learning goals and lesson types.
    *   Receive personalized lesson recommendations.
*   **Notifications:** Stay informed with daily reminders, progress updates, and more.
*   **Word of the Day:** Learn a new word daily.

## Tech Stack

*   **Backend:**
    *   Python
    *   Django
    *   Django REST Framework (for API)
    *   SQLite (default database)
*   **Frontend:**
    *   React
    *   TypeScript
    *   Vite
*   **APIs:**
    *   OpenAI API (for pronunciation feedback)

## Prerequisites

Before you begin, ensure you have the following installed:

*   Python (3.8+ recommended)
*   Pip (Python package installer)
*   Node.js (16.x or higher recommended)
*   npm (Node package manager, comes with Node.js)

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Backend Setup:**
    *   Navigate to the backend directory:
        ```bash
        cd backend
        ```
    *   Create and activate a virtual environment:
        ```bash
        python -m venv venv
        # On Windows
        source venv/Scripts/activate
        # On macOS/Linux
        source venv/bin/activate
        ```
    *   Install Python dependencies:
        ```bash
        pip install -r requirements.txt
        ```
        *(Note: A `requirements.txt` would be ideal. Currently, you might need to install packages like `django`, `djangorestframework`, `psycopg2-binary` (if using PostgreSQL), `openai`, `corsheaders`, `djangorestframework-simplejwt` manually or generate a `requirements.txt` using `pip freeze > requirements.txt` after installing them).*
    *   **Environment Variables:**
        Create a `.env` file in the `backend/` or `backend/backend/` directory (where `settings.py` can access it). Add your OpenAI API key:
        ```env
        OPENAI_API_KEY=your_openai_api_key_here
        ```
        *(Ensure `settings.py` is configured to load this, e.g., using `python-dotenv`)*.
    *   Apply database migrations:
        ```bash
        python manage.py migrate
        ```
    *   Create a superuser (optional, for admin access):
        ```bash
        python manage.py createsuperuser
        ```

3.  **Frontend Setup:**
    *   Navigate to the frontend directory (from the root):
        ```bash
        cd frontend
        ```
    *   Install Node.js dependencies:
        ```bash
        npm install
        ```
    *   **Environment Variables (Frontend):**
        If your frontend needs to connect to a specific backend URL other than a relative path, create a `.env` file in the `frontend/` directory:
        ```env
        VITE_API_BASE_URL=http://localhost:8000/api
        ```
        *(Ensure your frontend code uses `import.meta.env.VITE_API_BASE_URL`)*.


## Running the Application

1.  **Run the Backend Server:**
    *   Ensure you are in the `backend/` directory with the virtual environment activated.
    *   Start the Django development server:
        ```bash
        python manage.py runserver
        ```
    *   The backend will typically be available at `http://127.0.0.1:8000/`.

2.  **Run the Frontend Development Server:**
    *   Ensure you are in the `frontend/` directory.
    *   Start the Vite development server:
        ```bash
        npm run dev
        ```
    *   The frontend will typically be available at `http://localhost:5173/`.

## Project Structure

```
.
├── backend/            # Django backend application
│   ├── backend/        # Django project configuration (settings.py, urls.py)
│   ├── courses/        # Django app for courses, lessons, progress, etc.
│   ├── users/          # Django app for user management (models, views)
│   ├── media/          # For user-uploaded files
│   ├── static/         # For static files (CSS, JS, images for Django templates)
│   ├── venv/           # Python virtual environment
│   ├── manage.py       # Django's command-line utility
│   └── requirements.txt # Python dependencies 
├── frontend/           # React frontend application (Vite)
│   ├── public/         # Static assets for the frontend
│   ├── src/            # Frontend source code (components, pages, etc.)
│   ├── package.json    # Frontend dependencies and scripts
│   └── vite.config.ts  # Vite configuration
├── venv/               # Project-level virtual environment (alternative location)
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── db.sqlite3          # Default SQLite database file
├── LICENSE             # Project license information
└── README.md           # This file
```

## License

This project is licensed under the terms of the [LICENSE](./LICENSE) file.
