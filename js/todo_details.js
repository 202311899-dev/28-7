document.addEventListener('DOMContentLoaded', () => {
    const taskTitleEl = document.getElementById('task-title');
    const taskDescEl = document.getElementById('task-description');
    const subtaskList = document.getElementById('subtask-list');
    const subtaskForm = document.getElementById('subtask-form');
    const errorContainer = document.getElementById('error-container');

    // Extract the task ID from the current page URL (e.g. /todos/3 -> "3")
    const urlParts = window.location.pathname.split('/');
    const todoId = urlParts[urlParts.length - 1];

    // 1. Fetch Task and its Subtasks from the API
    async function loadTaskDetails() {
        try {
            const response = await fetch('/api/todos');
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }

            const parentTodos = await response.json();
            
            // Find the parent todo matching our URL ID
            const currentTodo = parentTodos.find(item => item.id == todoId);

            if (!currentTodo) {
                showError('Task not found.');
                taskTitleEl.textContent = 'Task Not Found';
                return;
            }

            // Set Title & Description
            document.title = `${currentTodo.title} - Details`;
            taskTitleEl.textContent = currentTodo.title;
            taskDescEl.textContent = currentTodo.description || 'No description provided.';

            // Render Subtasks
            renderSubtasks(currentTodo.subtodos || []);

        } catch (error) {
            console.error('Error loading task details:', error);
            showError('Failed to load task details.');
        }
    }

    // 2. Render Subtasks List
    function renderSubtasks(subtasks) {
        subtaskList.innerHTML = '';

        if (subtasks.length === 0) {
            subtaskList.innerHTML = `
                <li style="text-align: center; color: #64748b; padding: 20px 0;">
                    No subtasks yet. Add one above!
                </li>
            `;
            return;
        }

        subtasks.forEach(subtask => {
            const li = document.createElement('li');
            li.className = 'todo-item';
            li.style.padding = '12px 16px';
            li.style.fontWeight = '500';
            li.textContent = subtask.title;
            subtaskList.appendChild(li);
        });
    }

    // 3. Handle Subtask Form Submission
    subtaskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorContainer.innerHTML = '';

        const titleInput = document.getElementById('subtask-title');
        const title = titleInput.value.trim();

        if (!title) return;

        try {
            const response = await fetch('/api/todos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    parent_todo_id: parseInt(todoId)
                })
            });

            if (response.ok) {
                titleInput.value = '';
                loadTaskDetails(); // Reload to reflect newly added subtask
            } else {
                const data = await response.json();
                showError(data.error || 'Failed to add subtask.');
            }
        } catch (error) {
            console.error('Error adding subtask:', error);
            showError('Server connection error.');
        }
    });

    function showError(message) {
        errorContainer.innerHTML = `<div class="alert-error">${message}</div>`;
    }

    // Initial load
    loadTaskDetails();
});