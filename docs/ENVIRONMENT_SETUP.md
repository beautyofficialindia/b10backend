# ENVIRONMENT_SETUP.md

## Local Development Initialization

1. **Clone and create Virtual Environment:**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

2. **Install exact dependencies:**
```bash
pip install -r backend/requirements.txt
```

3. **Configure the Environment File:**
Copy `backend/.env.example` to `backend/.env`.
```bash
cp backend/.env.example backend/.env
```
Open `backend/.env` and replace `your-secret-key` and the `OPENROUTER_API_KEY` with real credentials.

4. **Migrate the Database:**
```bash
cd backend
python manage.py migrate
```

5. **Generate the First Admin Account:**
This command reads `ADMIN_USERNAME` and `ADMIN_PASSWORD` from your `.env` file and provisions the security Groups.
```bash
python manage.py create_initial_admin
```

6. **Start the Development Server:**
```bash
python manage.py runserver
```
