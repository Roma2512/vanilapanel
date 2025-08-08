// Функция для показа всплывающего сообщения
function showPopup(message, type = 'info', duration = 3000) {
    const popup = document.createElement('div');
    popup.className = `popup ${type}`;
    popup.textContent = message;
    document.body.appendChild(popup);
    
    setTimeout(() => {
        popup.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        popup.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(popup);
        }, 300);
    }, duration);
}

// Функция для показа диалога подтверждения
async function showConfirm(message) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'popup-overlay';
        
        const popup = document.createElement('div');
        popup.className = 'confirm-popup';
        
        popup.innerHTML = `
            <div class="confirm-message">${message}</div>
            <div class="confirm-buttons">
                <button class="confirm-button confirm-yes">Да</button>
                <button class="confirm-button confirm-no">Нет</button>
            </div>
        `;
        
        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        
        popup.querySelector('.confirm-yes').addEventListener('click', () => {
            document.body.removeChild(overlay);
            resolve(true);
        });
        
        popup.querySelector('.confirm-no').addEventListener('click', () => {
            document.body.removeChild(overlay);
            resolve(false);
        });
    });
}

// Функция для показа диалога ввода
async function showPrompt(message, defaultValue = '') {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'popup-overlay';
        
        const popup = document.createElement('div');
        popup.className = 'prompt-popup';
        
        popup.innerHTML = `
            <div class="prompt-message">${message}</div>
            <input type="text" class="prompt-input" value="${defaultValue}" autofocus>
            <div class="prompt-buttons">
                <button class="prompt-button prompt-ok">OK</button>
                <button class="prompt-button prompt-cancel">Отмена</button>
            </div>
        `;
        
        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        
        const input = popup.querySelector('.prompt-input');
        
        popup.querySelector('.prompt-ok').addEventListener('click', () => {
            document.body.removeChild(overlay);
            resolve(input.value);
        });
        
        popup.querySelector('.prompt-cancel').addEventListener('click', () => {
            document.body.removeChild(overlay);
            resolve(null);
        });
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                document.body.removeChild(overlay);
                resolve(input.value);
            }
        });
    });
}