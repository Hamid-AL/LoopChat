# Getting Started Guide

This guide will walk you through setting up and running the LoopChat Django application from scratch.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.12+** (Check with `python --version` or `python3 --version`)
- **Docker Desktop** (for Redis) - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** (optional, for cloning the repository)

## Step 1: Clone or Navigate to the Project

If you're cloning from a repository:
```bash
git clone <repository-url>
cd djangoAuth
```

Or if you already have the project, navigate to the project directory:
```bash
cd djangoAuth
```

## Step 2: Create a Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies.

### Option A: Using Python's venv (Recommended)

```bash
# On Windows
python -m venv venv

# On macOS/Linux
python3 -m venv venv
```

### Option B: Using uv (Fast Python Package Manager)

If you have `uv` installed:
```bash
uv venv
```

This will create a virtual environment in your project directory.

## Step 3: Activate the Virtual Environment

### On Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### On Windows (Command Prompt):
```cmd
venv\Scripts\activate.bat
```

### On macOS/Linux:
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt, indicating the virtual environment is active.

## Step 4: Install Dependencies

### Option A: Using uv (Recommended - Faster)

If you're using `uv`:
```bash
uv pip install -e .
```

Or install dependencies directly:
```bash
uv pip install channels[daphne] channels-redis django
```

### Option B: Using pip

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, you can create one or install directly:
```bash
pip install channels[daphne] channels-redis django
```

Or install from `pyproject.toml`:
```bash
pip install -e .
```

**Note:** The application requires:
- `Django >= 5.2.7`
- `channels[daphne] >= 4.3.1` (for WebSocket support)
- `channels-redis >= 4.3.0` (for Redis channel layer)

## Step 5: Start Redis with Docker

The application uses Redis for WebSocket message brokering. Start Redis using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **Redis** on port `6379`
- **RedisInsight** (optional Redis management UI) on port `8001`

Verify Redis is running:
```bash
docker ps
```

You should see containers named `redis` and `redisinsight` running.

**Alternative:** If you prefer not to use Docker, you can install Redis directly:
- **Windows:** Use WSL or download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
- **macOS:** `brew install redis` then `brew services start redis`
- **Linux:** `sudo apt-get install redis-server` then `sudo systemctl start redis`

If using local Redis, make sure it's running on `127.0.0.1:6379` or update `CHANNEL_LAYERS` in `server/settings.py`.

## Step 6: Configure Database Settings (Optional)

The project uses SQLite by default, which requires no additional configuration. The database file `db.sqlite3` will be created automatically when you run migrations.

If you want to use PostgreSQL or MySQL instead, update the `DATABASES` setting in `server/settings.py`.

## Step 7: Run Database Migrations

Create the database tables by running migrations:

```bash
python manage.py makemigrations
```

This will create migration files for any model changes. Then apply the migrations:

```bash
python manage.py migrate
```

This will create all necessary database tables:
- Django built-in tables (auth_user, sessions, etc.)
- Users app tables (users_profile, users_friendship, users_friendrequest)
- Chat app tables (chat_chatroom, chat_roommessage, chat_directmessage)

## Step 8: Create a Superuser (Optional)

Create an admin account to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:
- Username
- Email address (optional)
- Password (twice)

You can access the admin panel at `http://127.0.0.1:8000/admin/` after starting the server.

## Step 9: Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

Or specify a custom port:
```bash
python manage.py runserver 8000
```

Open your web browser and navigate to:

- **Home/Chat Index:** `http://127.0.0.1:8000/chat/friends`
- **Login Page:** `http://127.0.0.1:8000/users/login/`
- **Signup Page:** `http://127.0.0.1:8000/users/signup/`
- **Admin Panel:** `http://127.0.0.1:8000/admin/` (if you created a superuser)