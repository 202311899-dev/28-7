document.addEventListener('DOMContentLoaded', () => {
    const todoList = document.getElementById('todo-list');
    const todoForm = document.getElementById('todo-form');
    const errorContainer = document.getElementById('error-container');
    const userNameEl = document.getElementById('user-name');

    // 1. Load Parent Todos from API
    async function loadTodos() {
        try {
            const response = await fetch('/api/todos');

            // Redirect if session is expired or unauthorized
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }

            const todos = await response.json();
            renderTodoList(todos);
        } catch (error) {
            console.error('Error fetching todos:', error);
            showError('Unable to load tasks. Please try again.');
        }
    }

    // 2. Render Todo List Items
    function renderTodoList(todos) {
        todoList.innerHTML = '';

        if (!todos || todos.length === 0) {
            todoList.innerHTML = `
                <li style="text-align: center; color: #64748b; padding: 20px 0;">
                    No tasks found. Create one above!
                </li>
            `;
            return;
        }

        todos.forEach(todo => {
            const li = document.createElement('li');
            li.className = 'todo-item';

            const descriptionHTML = todo.description 
                ? `<div class="todo-desc">${escapeHTML(todo.description)}</div>` 
                : '';

            li.innerHTML = `
                <a href="/todos/${todo.id}" class="todo-link">
                    <div>
                        <div class="todo-title">${escapeHTML(todo.title)}</div>
                        ${descriptionHTML}
                    </div>
                    <span style="color: #64748b; font-weight: bold;">&rarr;</span>
                </a>
            `;
            todoList.appendChild(li);
        });
    }

    // 3. Handle Add New Task Form Submission
    todoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorContainer.innerHTML = '';

        const titleInput = document.getElementById('title');
        const descriptionInput = document.getElementById('description');

        const title = titleInput.value.trim();
        const description = descriptionInput.value.trim();

        if (!title) return;

        try {
            const response = await fetch('/api/todos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    description: description || null,
                    parent_todo_id: null
                })
            });

            if (response.ok) {
                titleInput.value = '';
                descriptionInput.value = '';
                loadTodos(); // Reload dashboard tasks dynamically
            } else {
                const data = await response.json();
                showError(data.error || 'Failed to add task.');
            }
        } catch (error) {
            console.error('Error creating todo:', error);
            showError('Server connection error. Failed to save task.');
        }
    });

    // Utility: Display error banners
    function showError(message) {
        errorContainer.innerHTML = `<div class="alert-error">${message}</div>`;
    }

    // Utility: Escape user text to prevent XSS
    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    // Initial fetch
    loadTodos();

    // Fetch user name on load
async function fetchUserInfo() {
    try {
        const res = await fetch('/api/me');
        if (res.ok) {
            const user = await res.json();
            const nameSpan = document.getElementById('user-name');
            if (nameSpan) nameSpan.textContent = user.name;
        }
    } catch (err) {
        console.error('Failed to load user info:', err);
    }
}

fetchUserInfo();
});