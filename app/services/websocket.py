"""
WebSocket event handlers for real-time task updates and notifications.
"""

import logging
from flask import session, request
from flask_socketio import emit, join_room, leave_room

logger = logging.getLogger(__name__)

class SocketIOHandler:
    """Handler for WebSocket events"""
    
    # Store connected users
    connected_users = {}
    
    @staticmethod
    def on_connect(socketio):
        """Handle client connection"""
        def handle_connect():
            user_id = session.get('user_id')
            if user_id:
                SocketIOHandler.connected_users[user_id] = request.sid
                join_room(f'user_{user_id}')
                logger.info(f"User {user_id} connected via WebSocket")
                emit('connect_response', {'status': 'Connected', 'message': 'Connected to real-time updates'})
        
        return handle_connect
    
    @staticmethod
    def on_disconnect(socketio):
        """Handle client disconnection"""
        def handle_disconnect():
            user_id = session.get('user_id')
            if user_id and user_id in SocketIOHandler.connected_users:
                del SocketIOHandler.connected_users[user_id]
                leave_room(f'user_{user_id}')
                logger.info(f"User {user_id} disconnected")
        
        return handle_disconnect
    
    @staticmethod
    def emit_task_update(socketio, user_id, task_data, action='update'):
        """Emit task update to connected user"""
        try:
            socketio.emit(
                'task_update',
                {
                    'action': action,
                    'task': task_data,
                    'timestamp': pd.Timestamp.now().isoformat()
                },
                room=f'user_{user_id}'
            )
            logger.info(f"Task update emitted to user {user_id}")
        except Exception as e:
            logger.error(f"Error emitting task update: {e}")
    
    @staticmethod
    def emit_notification(socketio, user_id, message, notification_type='info'):
        """Emit notification to connected user"""
        try:
            socketio.emit(
                'notification',
                {
                    'type': notification_type,
                    'message': message,
                    'timestamp': pd.Timestamp.now().isoformat()
                },
                room=f'user_{user_id}'
            )
            logger.info(f"Notification sent to user {user_id}")
        except Exception as e:
            logger.error(f"Error emitting notification: {e}")

# Import pandas here to avoid circular imports
import pandas as pd
