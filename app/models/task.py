"""
Task model for database operations.
Handles CRUD operations for tasks.
"""

import logging
from config.database import Database
from datetime import datetime

logger = logging.getLogger(__name__)

class Task:
    """Task model for database operations"""
    
    @staticmethod
    def create(user_id, title, description, priority='medium'):
        """Create a new task"""
        try:
            query = """
                INSERT INTO tasks (user_id, title, description, priority, status)
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id, user_id, title, description, priority, status, created_at;
            """
            result = Database.execute_query(
                query,
                (user_id, title, description, priority),
                fetch=True
            )
            logger.info(f"Task created for user {user_id}")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    @staticmethod
    def get_all(user_id):
        """Get all tasks for a user"""
        try:
            query = """
                SELECT id, title, description, priority, status, created_at, updated_at
                FROM tasks
                WHERE user_id = %s
                ORDER BY created_at DESC;
            """
            result = Database.execute_query(query, (user_id,), fetch=True)
            return result if result else []
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
            raise
    
    @staticmethod
    def get_by_id(task_id, user_id):
        """Get a specific task by ID"""
        try:
            query = """
                SELECT id, title, description, priority, status, created_at, updated_at
                FROM tasks
                WHERE id = %s AND user_id = %s;
            """
            result = Database.execute_query(query, (task_id, user_id), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error fetching task: {e}")
            raise
    
    @staticmethod
    def update(task_id, user_id, title=None, description=None, priority=None, status=None):
        """Update a task"""
        try:
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = %s")
                params.append(title)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if priority is not None:
                updates.append("priority = %s")
                params.append(priority)
            if status is not None:
                updates.append("status = %s")
                params.append(status)
            
            if not updates:
                return Task.get_by_id(task_id, user_id)
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.extend([task_id, user_id])
            
            query = f"""
                UPDATE tasks
                SET {', '.join(updates)}
                WHERE id = %s AND user_id = %s
                RETURNING id, title, description, priority, status, created_at, updated_at;
            """
            
            result = Database.execute_query(query, params, fetch=True)
            logger.info(f"Task {task_id} updated")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise
    
    @staticmethod
    def delete(task_id, user_id):
        """Delete a task"""
        try:
            query = "DELETE FROM tasks WHERE id = %s AND user_id = %s RETURNING id;"
            result = Database.execute_query(query, (task_id, user_id), fetch=True)
            logger.info(f"Task {task_id} deleted")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            raise
