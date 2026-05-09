"""
Analytics API routes.
"""

from flask import Blueprint, jsonify, session
import logging
from app.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

def require_login(f):
    """Decorator to check if user is logged in"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    
    return decorated_function

@analytics_bp.route('/summary', methods=['GET'])
@require_login
def get_analytics_summary():
    """
    Get task analytics summary
    Returns: total tasks, completed tasks, pending tasks, completion percentage
    """
    try:
        user_id = session['user_id']
        stats = AnalyticsService.get_task_statistics(user_id)
        
        return jsonify({
            'analytics': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        return jsonify({'error': 'Server error'}), 500

@analytics_bp.route('/advanced', methods=['GET'])
@require_login
def get_advanced_analytics():
    """
    Get advanced analytics using NumPy calculations
    """
    try:
        user_id = session['user_id']
        analytics = AnalyticsService.get_advanced_analytics(user_id)
        
        return jsonify({
            'advanced_analytics': analytics
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching advanced analytics: {e}")
        return jsonify({'error': 'Server error'}), 500
