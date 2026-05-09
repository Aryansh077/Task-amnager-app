"""
Database connection and utilities for PostgreSQL with a SQLite demo fallback.
"""

import logging
import os
import re
import sqlite3

import psycopg2
from psycopg2.extras import RealDictCursor

from config.config import Config

logger = logging.getLogger(__name__)

class Database:
    """Database connection handler"""

    backend = 'postgres'
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'task_management_demo.db')
    
    @staticmethod
    def get_connection():
        """Create and return a database connection"""
        if Database.backend == 'sqlite' or getattr(Config, 'USE_SQLITE', False):
            Database.backend = 'sqlite'
            conn = sqlite3.connect(Database.sqlite_path)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys = ON')
            return conn

        try:
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            Database.backend = 'postgres'
            return conn
        except psycopg2.Error as e:
            logger.warning(f"Database connection error, falling back to SQLite demo mode: {e}")
            Database.backend = 'sqlite'
            conn = sqlite3.connect(Database.sqlite_path)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys = ON')
            return conn

    @staticmethod
    def _convert_query(query):
        """Convert PostgreSQL placeholders to SQLite placeholders."""
        return re.sub(r'%s', '?', query)
    
    @staticmethod
    def execute_query(query, params=None, fetch=False):
        """Execute a query and optionally fetch results"""
        conn = Database.get_connection()
        try:
            if Database.backend == 'sqlite':
                sqlite_query = Database._convert_query(query)
                with conn:
                    cur = conn.cursor()
                    cur.execute(sqlite_query, params or ())
                    if fetch:
                        rows = cur.fetchall()
                        return [dict(row) for row in rows]
                    return None

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())

                if fetch:
                    result = cur.fetchall()
                else:
                    conn.commit()
                    result = None

                return result
        except (psycopg2.Error, sqlite3.Error) as e:
            try:
                conn.rollback()
            except Exception:
                pass
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            conn.close()
