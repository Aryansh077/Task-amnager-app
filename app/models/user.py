"""
User model and authentication logic.
Handles user registration, login, and authentication.
"""

import hashlib
import logging
from config.database import Database

logger = logging.getLogger(__name__)

class User:
    """User model for authentication"""
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def register(username, email, password):
        """Register a new user"""
        try:
            password_hash = User.hash_password(password)
            query = """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id, username, email;
            """
            result = Database.execute_query(
                query,
                (username, email, password_hash),
                fetch=True
            )
            logger.info(f"User {username} registered successfully")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise
    
    @staticmethod
    def login(username, password):
        """Authenticate user and return user data"""
        try:
            password_hash = User.hash_password(password)
            query = """
                SELECT id, username, email
                FROM users
                WHERE username = %s AND password_hash = %s;
            """
            result = Database.execute_query(
                query,
                (username, password_hash),
                fetch=True
            )
            
            if result:
                logger.info(f"User {username} logged in successfully")
                return result[0]
            
            logger.warning(f"Failed login attempt for user {username}")
            return None
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        try:
            query = "SELECT id, username, email FROM users WHERE id = %s;"
            result = Database.execute_query(query, (user_id,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            raise
