import os
import shutil

def setup_project_structure():
    # Project root directory (current directory)
    root_dir = os.getcwd()
    
    # Create necessary directories
    directories = [
        'frontend/static/css',
        'frontend/static/js',
        'frontend/templates',
        'backend/api',
        'backend/config',
        'backend/models'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
    # Create necessary __init__.py files
    init_locations = [
        'backend',
        'backend/api',
        'backend/config',
        'backend/models'
    ]
    
    for location in init_locations:
        init_file = os.path.join(location, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'a').close()
            
    # Move index.html to correct location
    if os.path.exists('index.html'):
        shutil.copy('index.html', 'frontend/static/index.html')

if __name__ == "__main__":
    setup_project_structure()
    print("Project structure setup complete!")