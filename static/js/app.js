// Main Application JavaScript
// Handles tasks management and real-time updates

// Initialize Socket.IO
const socket = io();

// Elements
const tasksList = document.getElementById('tasksList');
const addTaskBtn = document.getElementById('addTaskBtn');
const addTaskForm = document.getElementById('addTaskForm');
const taskForm = document.getElementById('taskForm');
const cancelBtn = document.getElementById('cancelBtn');
const logoutBtn = document.getElementById('logoutBtn');
const notification = document.getElementById('notification');
const navLinks = document.querySelectorAll('.nav-link');

// State
let currentEditTaskId = null;

// ============ Navigation ============
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.dataset.section;
        switchSection(section);
    });
});

function switchSection(section) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    
    // Remove active from all nav links
    navLinks.forEach(link => link.classList.remove('active'));
    
    // Show selected section
    const sectionElement = document.getElementById(`${section}-section`);
    if (sectionElement) {
        sectionElement.classList.add('active');
    }
    
    // Mark nav link as active
    event.target.classList.add('active');
    
    // Load data if needed
    if (section === 'tasks') {
        loadTasks();
    } else if (section === 'analytics') {
        loadAnalytics();
    }
}

// ============ Logout ============
logoutBtn.addEventListener('click', async () => {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        console.error('Logout error:', error);
        showNotification('Error during logout', 'error');
    }
});

// ============ Task Management ============
addTaskBtn.addEventListener('click', () => {
    currentEditTaskId = null;
    taskForm.reset();
    document.querySelector('#addTaskForm h3').textContent = 'Create New Task';
    addTaskForm.classList.add('show');
    addTaskForm.classList.remove('hidden');
});

cancelBtn.addEventListener('click', () => {
    addTaskForm.classList.remove('show');
    addTaskForm.classList.add('hidden');
    taskForm.reset();
});

taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        priority: document.getElementById('taskPriority').value,
        status: document.getElementById('taskStatus').value
    };
    
    try {
        if (currentEditTaskId) {
            // Update task
            const response = await fetch(`/api/tasks/${currentEditTaskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            if (response.ok) {
                showNotification('Task updated successfully', 'success');
                addTaskForm.classList.remove('show');
                addTaskForm.classList.add('hidden');
                loadTasks();
            } else {
                showNotification(data.error || 'Failed to update task', 'error');
            }
        } else {
            // Create new task
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            if (response.ok) {
                showNotification('Task created successfully', 'success');
                addTaskForm.classList.remove('show');
                addTaskForm.classList.add('hidden');
                taskForm.reset();
                loadTasks();
            } else {
                showNotification(data.error || 'Failed to create task', 'error');
            }
        }
    } catch (error) {
        console.error('Form submission error:', error);
        showNotification('An error occurred', 'error');
    }
});

async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        
        if (data.tasks && data.tasks.length > 0) {
            renderTasks(data.tasks);
        } else {
            tasksList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <p>No tasks yet. Create one to get started!</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        tasksList.innerHTML = '<p class="loading">Error loading tasks</p>';
    }
}

function renderTasks(tasks) {
    tasksList.innerHTML = '';
    
    tasks.forEach(task => {
        const taskCard = document.createElement('div');
        taskCard.className = `task-card ${task.priority}-priority`;
        taskCard.innerHTML = `
            <div class="task-header">
                <div>
                    <h3 class="task-title">${escapeHtml(task.title)}</h3>
                    <div class="task-meta">
                        <span>📅 ${formatDate(task.created_at)}</span>
                        <span>👤 ${task.priority.toUpperCase()}</span>
                    </div>
                </div>
            </div>
            ${task.description ? `<p class="task-description">${escapeHtml(task.description)}</p>` : ''}
            <div>
                <span class="task-badge badge-${task.status}">${task.status.toUpperCase()}</span>
                <span class="task-badge badge-${task.priority}">${task.priority.toUpperCase()}</span>
            </div>
            <div class="task-footer">
                <div class="task-actions">
                    <button class="btn btn-edit" onclick="editTask(${task.id})">Edit</button>
                    <button class="btn btn-delete" onclick="deleteTask(${task.id})">Delete</button>
                </div>
                <label>
                    <input type="checkbox" 
                        onchange="toggleTaskStatus(${task.id}, this.checked)"
                        ${task.status === 'completed' ? 'checked' : ''}>
                    Mark Complete
                </label>
            </div>
        `;
        tasksList.appendChild(taskCard);
    });
}

async function editTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`);
        const data = await response.json();
        
        if (data.task) {
            const task = data.task;
            document.getElementById('taskTitle').value = task.title;
            document.getElementById('taskDescription').value = task.description || '';
            document.getElementById('taskPriority').value = task.priority;
            document.getElementById('taskStatus').value = task.status;
            
            currentEditTaskId = taskId;
            document.querySelector('#addTaskForm h3').textContent = 'Edit Task';
            addTaskForm.classList.add('show');
            addTaskForm.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading task:', error);
        showNotification('Error loading task', 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Task deleted successfully', 'success');
            loadTasks();
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to delete task', 'error');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showNotification('Error deleting task', 'error');
    }
}

async function toggleTaskStatus(taskId, completed) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                status: completed ? 'completed' : 'pending'
            })
        });
        
        if (response.ok) {
            showNotification(
                completed ? 'Task marked as completed' : 'Task marked as pending',
                'success'
            );
            loadTasks();
        } else {
            showNotification('Failed to update task status', 'error');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showNotification('Error updating task', 'error');
    }
}

// ============ Analytics ============
async function loadAnalytics() {
    try {
        // Load basic analytics
        const statsResponse = await fetch('/api/analytics/summary');
        const statsData = await statsResponse.json();
        
        if (statsData.analytics) {
            const stats = statsData.analytics;
            document.getElementById('totalTasks').textContent = stats.total_tasks;
            document.getElementById('completedTasks').textContent = stats.completed_tasks;
            document.getElementById('pendingTasks').textContent = stats.pending_tasks;
            document.getElementById('completionPercentage').textContent = 
                stats.completion_percentage + '%';
            
            // Render status distribution
            const statusDist = document.getElementById('statusDistribution');
            statusDist.innerHTML = '';
            for (const [status, count] of Object.entries(stats.status_distribution || {})) {
                const item = document.createElement('div');
                item.className = 'distribution-item';
                item.innerHTML = `
                    <span>${status}</span>
                    <strong>${count}</strong>
                `;
                statusDist.appendChild(item);
            }
        }
        
        // Load advanced analytics
        const advResponse = await fetch('/api/analytics/advanced');
        const advData = await advResponse.json();
        
        if (advData.advanced_analytics) {
            const adv = advData.advanced_analytics;
            document.getElementById('avgPriority').textContent = adv.average_priority || '-';
            document.getElementById('highPriorityCount').textContent = adv.high_priority_count || 0;
            document.getElementById('advCompletionRate').textContent = 
                (adv.completion_rate || 0) + '%';
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        showNotification('Error loading analytics', 'error');
    }
}

// ============ WebSocket Events ============
socket.on('connect', () => {
    console.log('Connected to WebSocket');
});

socket.on('task_update', (data) => {
    console.log('Task update received:', data);
    showNotification(`Task ${data.action}: ${JSON.stringify(data.task)}`, 'info');
    loadTasks();
});

socket.on('notification', (data) => {
    showNotification(data.message, data.type);
});

socket.on('disconnect', () => {
    console.log('Disconnected from WebSocket');
});

// ============ Utilities ============
function showNotification(message, type = 'info') {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 4000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============ Initialize ============
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
});
