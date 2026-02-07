from flask import Flask
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    @app.route('/')
    def hello():
        return {
            "message": "Welcome to the Phase 5 Backend API",
            "status": "running",
            "environment": os.environ.get('FLASK_ENV', 'development')
        }

    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "backend"}

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)