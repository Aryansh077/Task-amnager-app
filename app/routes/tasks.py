"""
Task management API routes (CRUD operations).
"""

from flask import Blueprint, request, jsonify, session
import logging
from app.models.task import Task
from app.services.websocket import SocketIOHandler

logger = logging.getLogger(__name__)

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

def require_login(f):
    """Decorator to check if user is logged in"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    
    return decorated_function

@tasks_bp.route('', methods=['GET'])
@require_login
def get_all_tasks():
    """
    Get all tasks for the current user
    """
    try:
        user_id = session['user_id']
        tasks = Task.get_all(user_id)
        
        return jsonify({
            'tasks': tasks,
            'count': len(tasks)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        return jsonify({'error': 'Server error'}), 500

@tasks_bp.route('', methods=['POST'])
@require_login
def create_task():
    """
    Create a new task
    Expected JSON: {
        "title": "string",
        "description": "string",
        "priority": "low|medium|high"
    }
    """
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        # Validation
        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        priority = data.get('priority', 'medium')
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'
        
        # Create task
        task = Task.create(
            user_id,
            data['title'],
            data.get('description', ''),
            priority
        )
        
        if task:
            return jsonify({
                'message': 'Task created successfully',
                'task': task
            }), 201
        
        return jsonify({'error': 'Failed to create task'}), 400
    
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({'error': 'Server error'}), 500

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@require_login
def get_task(task_id):
    """Get a specific task"""
    try:
        user_id = session['user_id']
        task = Task.get_by_id(task_id, user_id)
        
        if task:
            return jsonify({'task': task}), 200
        
        return jsonify({'error': 'Task not found'}), 404
    
    except Exception as e:
        logger.error(f"Error fetching task: {e}")
        return jsonify({'error': 'Server error'}), 500

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@require_login
def update_task(task_id):
    """
    Update a task
    Expected JSON: {
        "title": "string (optional)",
        "description": "string (optional)",
        "priority": "low|medium|high (optional)",
        "status": "pending|completed (optional)"
    }
    """
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        # Validate status if provided
        if 'status' in data and data['status'] not in ['pending', 'completed']:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Validate priority if provided
        if 'priority' in data and data['priority'] not in ['low', 'medium', 'high']:
            return jsonify({'error': 'Invalid priority'}), 400
        
        # Update task
        updated_task = Task.update(
            task_id,
            user_id,
            title=data.get('title'),
            description=data.get('description'),
            priority=data.get('priority'),
            status=data.get('status')
        )
        
        if updated_task:
            return jsonify({
                'message': 'Task updated successfully',
                'task': updated_task
            }), 200
        
        return jsonify({'error': 'Task not found'}), 404
    
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return jsonify({'error': 'Server error'}), 500

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@require_login
def delete_task(task_id):
    """Delete a task"""
    try:
        user_id = session['user_id']
        deleted_task = Task.delete(task_id, user_id)
        
        if deleted_task:
            return jsonify({'message': 'Task deleted successfully'}), 200
        
        return jsonify({'error': 'Task not found'}), 404
    
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return jsonify({'error': 'Server error'}), 500
