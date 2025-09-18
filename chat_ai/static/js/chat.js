// Обработчики для форм
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch('/login/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Ошибка входа: ' + (data.error || 'Неизвестная ошибка'));
                }
            });
        });

        document.getElementById('registerForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch('/register/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Ошибка регистрации: ' + JSON.stringify(data.errors));
                }
            });
        });

        document.getElementById('topUpForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch('/top_up_balance/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('userBalance').textContent = data.new_balance;
                    alert('Баланс успешно пополнен!');
                } else {
                    alert('Ошибка: ' + data.error);
                }
            });
        });

        document.getElementById('logoutBtn').addEventListener('click', function() {
            fetch('/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(() => location.reload());
        });

        let currentChatId = null;

        // Данные о провайдерах и их моделях
        const availableProviders = window.availableProviders;

        // Статус моделей (можно обновлять динамически)
        const modelStatus = {
            'mistral-small': '🟢 Доступен',
            'mistral-medium': '🟡 Ограничен',
            'mistral-large-latest': '🟡 Ограничен',
            'gpt-4o': '🟢 Доступен',
            'gpt-4o-mini': '🟢 Доступен'
        };

        document.getElementById('new-chat-btn').addEventListener('click', createNewChat);
        document.getElementById('send-btn').addEventListener('click', sendMessage);
        document.getElementById('edit-title-btn').addEventListener('click', editTitle);
        document.getElementById('message-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        // Обработчик изменения провайдера
        document.getElementById('provider-select').addEventListener('change', function() {
            updateModelSelect(this.value);
        });

        document.getElementById('chat-list').addEventListener('click', function(e) {
            if (e.target.closest('.chat-item') && !e.target.classList.contains('delete-chat-btn')) {
                const chatItem = e.target.closest('.chat-item');
                currentChatId = chatItem.dataset.chatId;
                loadChat(currentChatId);
            } else if (e.target.classList.contains('delete-chat-btn')) {
                e.stopPropagation();
                const chatId = e.target.dataset.chatId;
                deleteChat(chatId);
            }
        });

        function createNewChat() {
            fetch('/create_chat/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                currentChatId = data.chat_id;
                addChatToList(data.chat_id, data.title);
                loadChat(data.chat_id);
            });
        }

        function addChatToList(chatId, title) {
            const chatList = document.getElementById('chat-list');
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-item';
            chatItem.dataset.chatId = chatId;
            chatItem.style.opacity = '0';
            chatItem.style.transform = 'translateY(-20px)';
            chatItem.innerHTML = `
                <div class="chat-item-content">
                    <div class="chat-title">${title}</div>
                    <div class="chat-meta">
                        <small class="text-muted">Just now</small>
                    </div>
                </div>
                <button class="delete-chat-btn" data-chat-id="${chatId}" title="Delete chat">
                    <span class="icon">🗑️</span>
                </button>
            `;
            chatList.insertBefore(chatItem, chatList.firstChild);
            // Animate in
            setTimeout(() => {
                chatItem.style.transition = 'all 0.3s ease';
                chatItem.style.opacity = '1';
                chatItem.style.transform = 'translateY(0)';
            }, 10);
        }

        function loadChat(chatId) {
            fetch(`/chat/${chatId}/messages/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('chat-title').textContent = data.title;
                document.getElementById('chat-area').style.display = 'flex';
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML = '';
                data.messages.forEach(msg => {
                    addMessage(msg);
                });
            });
        }

        function sendMessage() {
            const input = document.getElementById('message-input');
            const sendBtn = document.getElementById('send-btn');
            const content = input.value.trim();
            if (!content || !currentChatId) return;

            const provider = document.getElementById('provider-select').value;
            const model = document.getElementById('model-select').value;

            // Immediately add user message to UI
            const userMessage = {
                id: Date.now(), // temporary id
                content: content,
                is_user: true,
                provider: provider,
                model: model,
                created_at: new Date().toISOString()
            };
            addMessage(userMessage);
            input.value = '';

            // Disable input and button
            input.disabled = true;
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<div class="loading"></div>';

            // Add loading AI message
            const loadingMessage = {
                id: Date.now() + 1,
                content: '<div class="typing"><span></span><span></span><span></span></div>',
                is_user: false,
                provider: provider,
                model: model,
                created_at: new Date().toISOString()
            };
            addMessage(loadingMessage);
            const loadingMessageDiv = document.querySelector('.messages .message:last-child');

            fetch('/send_message/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    chat_id: currentChatId,
                    content: content,
                    provider: provider,
                    model: model
                })
            })
            .then(response => response.json())
            .then(data => {
                // Remove loading message
                loadingMessageDiv.remove();
                // Add real AI message
                addMessage(data.ai_message);
                document.getElementById('chat-title').textContent = data.chat_title;
                updateChatTitleInList(currentChatId, data.chat_title);
            })
            .finally(() => {
                // Re-enable input and button
                input.disabled = false;
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                input.focus();
            });
        }

        function addMessage(msg) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${msg.is_user ? 'user-message' : 'ai-message'}`;
            // For loading message, content is already HTML, for others replace newlines
            const contentHtml = msg.content.includes('<div class="typing">') ? msg.content : msg.content.replace(/\n/g, '<br>');
            messageDiv.innerHTML = `<div class="message-content">${contentHtml}</div>`;
            messagesDiv.appendChild(messageDiv);
            // Smooth scroll to the new message
            messageDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }

        function editTitle() {
            const titleElement = document.getElementById('chat-title');
            const currentTitle = titleElement.textContent;
            const newTitle = prompt('Enter new title:', currentTitle);
            if (newTitle && newTitle !== currentTitle) {
                fetch(`/chat/${currentChatId}/update_title/`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({ title: newTitle })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        titleElement.textContent = newTitle;
                        updateChatTitleInList(currentChatId, newTitle);
                    }
                });
            }
        }

        function updateChatTitleInList(chatId, title) {
            const chatItems = document.querySelectorAll('.chat-item');
            chatItems.forEach(item => {
                if (item.dataset.chatId == chatId) {
                    item.querySelector('.chat-title').textContent = title;
                }
            });
        }

        function deleteChat(chatId) {
            if (confirm('Are you sure you want to delete this chat?')) {
                fetch(`/chat/${chatId}/delete/`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        removeChatFromList(chatId);
                        if (currentChatId == chatId) {
                            document.getElementById('chat-area').style.display = 'none';
                            currentChatId = null;
                        }
                    }
                });
            }
        }

        function removeChatFromList(chatId) {
            const chatItems = document.querySelectorAll('.chat-item');
            chatItems.forEach(item => {
                if (item.dataset.chatId == chatId) {
                    item.remove();
                }
            });
        }

        function updateModelSelect(providerKey) {
            const modelSelect = document.getElementById('model-select');
            const provider = availableProviders[providerKey];

            if (provider && provider.models) {
                modelSelect.innerHTML = '';
                provider.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;

                    // Disable if backend marked model as unavailable
                    if (model.available === false) {
                        option.disabled = true;
                        option.textContent += ' (Unavailable)';
                    }

                    // Добавляем статус если доступен
                    const status = modelStatus[model.id];
                    if (status) {
                        option.textContent += ` ${status}`;
                    }

                    modelSelect.appendChild(option);
                });
            }
        }

        // Инициализация модели для текущего провайдера
        document.addEventListener('DOMContentLoaded', function() {
            const providerSelect = document.getElementById('provider-select');
            updateModelSelect(providerSelect.value);
        });