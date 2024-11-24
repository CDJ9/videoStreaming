"# videoStreaming"
put into one terminal python main.py
put into another terminal python -m http.server 8080

go to http://localhost:8080 in 2 windows
in one window type a name and click create room.
copy the code it gives you and put into the other window and hit join room
pick a video as the leader (the window you hit create room in) and push play
you should be able to see that it matches in the other window.
Play pause is a little finicky.


pip install passlib python-jose[cryptography] python-multipart sqlalchemy pymysql bcrypt


```markdown
# Video Sync

A real-time video synchronization application that allows users to watch YouTube videos together.

## Setup Instructions

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the application:
```bash
python run.py
```

4. Open your browser and navigate to:
```
http://localhost:8000
```

## Features
- Create and join video watching rooms
- Synchronized video playback
- Video search functionality
- Real-time chat (coming soon)
- Video chat capabilities

## Development
- Frontend code is in the `frontend` directory
- Backend code is in the `backend` directory
- Run with debug mode: `python run.py`
```

7. Migration Steps:

1. Create the new directory structure:
```bash
mkdir -p backend/{api,config,models} frontend/{static/{css,js},templates}
```

2. Copy all the files to their new locations:
```bash
# Create necessary __init__.py files
touch backend/__init__.py backend/api/__init__.py backend/config/__init__.py backend/models/__init__.py

# Copy frontend files
cp index.html frontend/templates/
mv frontend/templates/index.html frontend/static/

# Create and populate all new files as shown above
```

3. Update import paths in all Python files to reflect the new structure.

8. Additional Configuration:

Create a `.gitignore` file:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# IDE
.vscode/
.idea/

# Logs
*.log

# Environment variables
.env
```

9. Development Workflow:

1. Start the application:
```bash
python run.py
```

2. The application will now serve:
- Frontend static files from `frontend/static`
- API endpoints from `backend/api/routes.py`
- WebSocket connections through `backend/api/websocket.py`

3. Make changes to:
- Frontend: Edit files in `frontend/static`
- Backend: Edit files in `backend/`
- Configuration: Edit `backend/config/settings.py`

The application will automatically reload when you make changes to any Python files.

10. Key Improvements:

1. Separation of Concerns:
   - Frontend and backend code are now clearly separated
   - Static files are organized by type (CSS, JS, etc.)
   - Backend functionality is split into logical modules

2. Maintainability:
   - Each component has a single responsibility
   - Configuration is centralized in `settings.py`
   - Code is more modular and easier to test

3. Scalability:
   - Easy to add new features by creating new modules
   - Clear structure for adding new API endpoints
   - Simple to add new frontend components

4. Development Experience:
   - Automatic reload during development
   - Clear file organization
   - Easy to locate and modify specific functionality