import os

def create_upload_directories():
    """Create necessary upload directories"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dirs = [
        'static/uploads/photos',
        'static/uploads/pyqp',
        'templates/auth',
        'templates/debug'
    ]
    
    for dir_path in upload_dirs:
        full_path = os.path.join(base_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"Created directory: {full_path}")
    
    print("All directories created successfully!")

if __name__ == '__main__':
    create_upload_directories()