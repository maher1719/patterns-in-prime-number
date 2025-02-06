// static/script.js (No changes needed)

function askQuestion() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value;
    if (!question.trim()) return;

    const chatArea = document.getElementById('chat-area');
    const expandCheckbox = document.getElementById('expand-checkbox');
    const expandChecked = expandCheckbox.checked;
    const downloadLinkContainer = document.getElementById('download-link-container');
    const currentThreadIdInput = document.getElementById('current-thread-id');
    const currentThreadId = currentThreadIdInput.value;  // Get current thread ID


    // Get values from new input fields
    const numQuestions = document.getElementById('num-questions').value;
    const summarizeChecked = document.getElementById('summarize-checkbox').checked;
    const textbooksChecked = document.getElementById('textbooks-checkbox').checked;
    const moreQuestionsChecked = document.getElementById('more-questions-checkbox').checked;

    // Add user message to chat (using Markdown)
      chatArea.innerHTML += `
        <div class="message user-message">
            <p>${marked.parse(question)}</p>
        </div>
    `;
    questionInput.value = '';

    // Show "Thinking..." message
    chatArea.innerHTML += `
        <div class="message bot-message thinking-message" id="thinking-message">
            <p>Thinking...</p>
        </div>
    `;
      // Clear previous download link
    downloadLinkContainer.innerHTML = '';


    // Construct form data
    const formData = new URLSearchParams();
    formData.append('question', question);
    formData.append('expand', expandChecked);
    formData.append('num_questions', numQuestions);
    formData.append('summarize', summarizeChecked);
    formData.append('textbooks', textbooksChecked);
    formData.append('more_questions', moreQuestionsChecked);
    formData.append('current_thread_id', currentThreadId); // Send current thread ID


    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const thinkingMessage = document.getElementById('thinking-message');
        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        // Append new messages to the chat area
        (data.messages || []).forEach(message => {
            const messageClass = message.role === 'user' ? 'user-message' : 'bot-message';
            chatArea.innerHTML += `
                <div class="message ${messageClass}">
                    <p>${marked.parse(message.content, { sanitize: false })}</p>
                </div>
            `;
        });

        chatArea.scrollTop = chatArea.scrollHeight;

        // Update current thread ID (important for new threads)
        if (data.thread_id) {
            currentThreadIdInput.value = data.thread_id;
        }
        // Add download link (if filename is provided) and thread id not empty
        if (data.filename && data.thread_id) {
            downloadLinkContainer.innerHTML = `<a href="/download/${data.filename}" download>Download Conversation</a>`;

             // Add 'active' class to the new thread in the sidebar
            const newThreadLink = document.querySelector(`.thread-list-item a[data-thread-id="${data.thread_id}"]`);
            if (newThreadLink) {
                // Remove 'active' from all other threads
                document.querySelectorAll('.thread-list-item').forEach(item => {
                    item.classList.remove('active');
                });
                newThreadLink.closest('.thread-list-item').classList.add('active');
            }

        }


    })
    .catch(error => {
        const thinkingMessage = document.getElementById('thinking-message');
        if (thinkingMessage) {
            thinkingMessage.remove();
        }
        chatArea.innerHTML += `
            <div class="message bot-message error-message">
                <p>Error: Could not get response. Please try again.</p>
            </div>
        `;
        console.error('Error:', error);
    });
}


function loadThread(threadId) {
    fetch(`/thread/${threadId}`)
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newChatArea = doc.querySelector('.chat-area'); // Get the whole chat-area
        const currentThreadIdInput = doc.getElementById('current-thread-id');
        const newThreadId = currentThreadIdInput ? currentThreadIdInput.value : null;

        // --- Apply marked.parse to each message ---
        if (newChatArea) { // Check if newChatArea exists
            const messageDivs = newChatArea.querySelectorAll('.message > p');
            messageDivs.forEach(p => {
              p.innerHTML = marked.parse(p.textContent, { sanitize: false });
            });
             document.getElementById('chat-area').innerHTML = newChatArea.innerHTML; // Set innerHTML *after* processing
        }


        document.getElementById('current-thread-id').value = newThreadId;
        updateDownloadLink(newThreadId);

        document.querySelectorAll('.thread-list-item').forEach(item => {
            item.classList.remove('active');
        });
        const activeThreadLink = document.querySelector(`.thread-list-item a[data-thread-id="${newThreadId}"]`);

        if (activeThreadLink) {
            activeThreadLink.closest('.thread-list-item').classList.add('active');
        }
    })
    .catch(error => console.error('Error loading thread:', error));
}