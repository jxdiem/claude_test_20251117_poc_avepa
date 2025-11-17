// Main Application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize authentication
    Auth.init();

    // Setup login form
    setupLoginForm();
});

// Setup login form
function setupLoginForm() {
    const loginForm = document.getElementById('login-form');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            await Auth.login(username, password);
        } catch (error) {
            // Error già gestito in Auth.login
            console.error('Login failed:', error);
        }
    });

    // Quick login buttons per demo
    addQuickLoginButtons();
}

// Add quick login buttons for demo users
function addQuickLoginButtons() {
    const demoUsers = document.querySelector('.demo-users ul');

    demoUsers.querySelectorAll('li').forEach(li => {
        const text = li.textContent;
        const match = text.match(/(\w+) \/ (\w+)/);

        if (match) {
            const username = match[1];
            const password = match[2];

            li.style.cursor = 'pointer';
            li.style.padding = '8px';
            li.style.borderRadius = '4px';
            li.style.transition = 'background 0.2s';

            li.addEventListener('mouseenter', () => {
                li.style.background = '#f0f0f0';
            });

            li.addEventListener('mouseleave', () => {
                li.style.background = 'transparent';
            });

            li.addEventListener('click', async () => {
                document.getElementById('username').value = username;
                document.getElementById('password').value = password;

                try {
                    await Auth.login(username, password);
                } catch (error) {
                    console.error('Quick login failed:', error);
                }
            });

            li.title = 'Clicca per login rapido';
        }
    });
}
