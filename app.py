"""
Main Flask application entry point.
Initializes the app, configures routes, and starts the server.
"""

from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
from config.config import Config
from config.schema import DatabaseSchema
from app.routes.auth import auth_bp
from app.routes.tasks import tasks_bp
from app.routes.analytics import analytics_bp
from app.services.websocket import SocketIOHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory function"""
    
    # Initialize Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    
    # Initialize CORS
    CORS(app)
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints (API routes)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(analytics_bp)
    
    # WebSocket event handlers
    @socketio.on('connect')
    def on_connect():
        logger.info("Client connected via WebSocket")
        SocketIOHandler.on_connect(socketio)()
    
    @socketio.on('disconnect')
    def on_disconnect():
        logger.info("Client disconnected from WebSocket")
        SocketIOHandler.on_disconnect(socketio)()
    
    # Frontend routes
    @app.route('/')
    def index():
        """Serve the main page"""
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return render_template('index.html')
    
    @app.route('/login')
    def login_page():
        """Serve login page"""
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        """Serve registration page"""
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('register.html')
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return {'error': 'Page not found'}, 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        return {'error': 'Internal server error'}, 500
    
    logger.info("Flask application created successfully")
    return app, socketio

if __name__ == '__main__':
    try:
        # Initialize database schema
        logger.info("Initializing database schema...")
        DatabaseSchema.create_tables()
        logger.info("Database schema initialized")
        
        # Create and run app
        app, socketio = create_app()
        
        logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
        socketio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
    
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
