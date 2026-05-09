"""
Database schema initialization and management.
Creates all necessary tables for the Task Management System.
"""

from config.database import Database
import logging

logger = logging.getLogger(__name__)

class DatabaseSchema:
    """Initialize and manage database schema"""

    @staticmethod
    def _get_queries():
        if Database.backend == 'sqlite':
            return [
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """,
            ]

        return [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,

            # Tasks table
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]
    
    @staticmethod
    def create_tables():
        """Create all required database tables"""
        conn = Database.get_connection()
        queries = DatabaseSchema._get_queries()
        
        try:
            cur = conn.cursor()
            try:
                for query in queries:
                    cur.execute(query)
                conn.commit()
                logger.info("Database tables created successfully")
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating tables: {e}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def drop_tables():
        """Drop all tables (use with caution)"""
        conn = Database.get_connection()

        if Database.backend == 'sqlite':
            queries = [
                "DROP TABLE IF EXISTS tasks;",
                "DROP TABLE IF EXISTS users;"
            ]
        else:
            queries = [
                "DROP TABLE IF EXISTS tasks CASCADE;",
                "DROP TABLE IF EXISTS users CASCADE;"
            ]
        
        try:
            cur = conn.cursor()
            try:
                for query in queries:
                    cur.execute(query)
                conn.commit()
                logger.info("Database tables dropped successfully")
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error dropping tables: {e}")
            raise
        finally:
            conn.close()
