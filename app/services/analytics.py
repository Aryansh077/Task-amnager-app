"""
Analytics service using Pandas and NumPy.
Calculates task statistics and completion rates.
"""

import pandas as pd
import numpy as np
import logging
from config.database import Database

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for task analytics and statistics"""
    
    @staticmethod
    def get_task_statistics(user_id):
        """Get comprehensive task statistics for a user"""
        try:
            query = """
                SELECT id, status, priority, created_at
                FROM tasks
                WHERE user_id = %s;
            """
            result = Database.execute_query(query, (user_id,), fetch=True)
            
            if not result:
                return {
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'pending_tasks': 0,
                    'completion_percentage': 0.0,
                    'tasks_by_priority': {},
                    'status_distribution': {}
                }
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(result)
            
            # Calculate statistics
            total_tasks = len(df)
            completed_tasks = len(df[df['status'] == 'completed'])
            pending_tasks = len(df[df['status'] == 'pending'])
            completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Status distribution
            status_dist = df['status'].value_counts().to_dict()
            
            # Priority distribution
            priority_dist = df['priority'].value_counts().to_dict()
            
            stats = {
                'total_tasks': int(total_tasks),
                'completed_tasks': int(completed_tasks),
                'pending_tasks': int(pending_tasks),
                'completion_percentage': round(float(completion_percentage), 2),
                'status_distribution': {str(k): int(v) for k, v in status_dist.items()},
                'priority_distribution': {str(k): int(v) for k, v in priority_dist.items()}
            }
            
            logger.info(f"Analytics calculated for user {user_id}")
            return stats
        
        except Exception as e:
            logger.error(f"Error calculating analytics: {e}")
            raise
    
    @staticmethod
    def get_advanced_analytics(user_id):
        """Get advanced analytics using NumPy"""
        try:
            query = """
                SELECT id, status, priority, created_at
                FROM tasks
                WHERE user_id = %s;
            """
            result = Database.execute_query(query, (user_id,), fetch=True)
            
            if not result:
                return {
                    'trend': 'No data',
                    'average_priority': None,
                    'completion_rate': 0.0
                }
            
            df = pd.DataFrame(result)
            
            # Priority scoring for advanced analytics
            priority_map = {'low': 1, 'medium': 2, 'high': 3}
            df['priority_score'] = df['priority'].map(priority_map)
            
            # Calculate advanced metrics
            avg_priority_score = float(np.mean(df['priority_score']))
            completion_rate = float(
                (df['status'] == 'completed').sum() / len(df) * 100
                if len(df) > 0 else 0
            )
            
            priority_labels = {1: 'Low', 2: 'Medium', 3: 'High'}
            avg_priority = priority_labels.get(round(avg_priority_score), 'Medium')
            
            analytics = {
                'average_priority': avg_priority,
                'completion_rate': round(completion_rate, 2),
                'task_count': len(df),
                'high_priority_count': int((df['priority'] == 'high').sum()),
                'completed_count': int((df['status'] == 'completed').sum())
            }
            
            logger.info(f"Advanced analytics calculated for user {user_id}")
            return analytics
        
        except Exception as e:
            logger.error(f"Error calculating advanced analytics: {e}")
            raise
