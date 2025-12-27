/**
 * Main JavaScript file for To-Do List application.
 * Handles AJAX interactions for task management.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle task form submission
    const taskForm = document.getElementById('task-form');
    if (taskForm) {
        taskForm.addEventListener('submit', handleTaskCreate);
    }

    // Handle checkbox toggles
    const checkboxes = document.querySelectorAll('.task-checkbox-input');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleTaskToggle);
    });

    // Handle delete buttons
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', handleTaskDelete);
    });
});

/**
 * Handle task creation via AJAX.
 * @param {Event} e - Form submit event
 */
function handleTaskCreate(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const taskInput = form.querySelector('.task-input');
    const inputValue = taskInput.value.trim();
    
    if (!inputValue) {
        return;
    }

    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrfToken);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload page to show new task
            window.location.reload();
        } else {
            alert('Ошибка при добавлении задачи');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Fallback to normal form submission
        form.submit();
    });
}

/**
 * Handle task completion toggle via AJAX.
 * @param {Event} e - Checkbox change event
 */
function handleTaskToggle(e) {
    const checkbox = e.target;
    const taskId = checkbox.dataset.taskId;
    const taskItem = checkbox.closest('.task-item');
    
    // Optimistic UI update
    if (checkbox.checked) {
        taskItem.classList.add('completed');
    } else {
        taskItem.classList.remove('completed');
    }

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/${taskId}/toggle/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
        },
        body: `csrfmiddlewaretoken=${csrfToken}`,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Move task to appropriate section
            const activeList = document.getElementById('active-tasks');
            const completedList = document.getElementById('completed-tasks');
            
            if (data.completed) {
                // Move to completed
                if (completedList) {
                    completedList.appendChild(taskItem);
                }
            } else {
                // Move to active
                if (activeList) {
                    activeList.appendChild(taskItem);
                }
            }
            
            // Update stats
            updateStats();
        } else {
            // Revert optimistic update
            checkbox.checked = !checkbox.checked;
            if (checkbox.checked) {
                taskItem.classList.remove('completed');
            } else {
                taskItem.classList.add('completed');
            }
            alert('Ошибка при обновлении задачи');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Revert optimistic update
        checkbox.checked = !checkbox.checked;
        if (checkbox.checked) {
            taskItem.classList.remove('completed');
        } else {
            taskItem.classList.add('completed');
        }
    });
}

/**
 * Handle task deletion via AJAX.
 * @param {Event} e - Button click event
 */
function handleTaskDelete(e) {
    if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
        return;
    }

    const button = e.target;
    const taskId = button.dataset.taskId;
    const taskItem = button.closest('.task-item');
    
    // Optimistic UI update
    taskItem.style.opacity = '0.5';
    taskItem.style.pointerEvents = 'none';

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/${taskId}/delete/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
        },
        body: `csrfmiddlewaretoken=${csrfToken}`,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Animate removal
            taskItem.style.transition = 'all 0.3s';
            taskItem.style.transform = 'translateX(-100%)';
            taskItem.style.opacity = '0';
            
            setTimeout(() => {
                taskItem.remove();
                updateStats();
                
                // Check if lists are empty and show empty state
                const activeList = document.getElementById('active-tasks');
                const completedList = document.getElementById('completed-tasks');
                if ((!activeList || activeList.children.length === 0) && 
                    (!completedList || completedList.children.length === 0)) {
                    window.location.reload();
                }
            }, 300);
        } else {
            // Revert optimistic update
            taskItem.style.opacity = '1';
            taskItem.style.pointerEvents = 'auto';
            alert('Ошибка при удалении задачи');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Revert optimistic update
        taskItem.style.opacity = '1';
        taskItem.style.pointerEvents = 'auto';
    });
}

/**
 * Update task statistics on the page.
 */
function updateStats() {
    const activeTasks = document.querySelectorAll('#active-tasks .task-item').length;
    const completedTasks = document.querySelectorAll('#completed-tasks .task-item').length;
    const totalTasks = activeTasks + completedTasks;
    
    // Update stat values if elements exist
    const statValues = document.querySelectorAll('.stat-value');
    if (statValues.length >= 3) {
        statValues[0].textContent = totalTasks;
        statValues[1].textContent = completedTasks;
        statValues[2].textContent = activeTasks;
    }
}

