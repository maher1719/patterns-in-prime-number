// static/script.js (Complete, with loadThread modification)

function askQuestion() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value;
    if (!question.trim()) return;

    const chatArea = document.getElementById('chat-area');
    const expandCheckbox = document.getElementById('expand-checkbox');
    const expandChecked = expandCheckbox.checked;
    const downloadLinkContainer = document.getElementById('download-link-container');
    const currentThreadIdInput = document.getElementById('current-thread-id');
    const currentThreadId = currentThreadIdInput.value;

    const numQuestions = document.getElementById('num-questions').value;
    const summarizeChecked = document.getElementById('summarize-checkbox').checked;
    const textbooksChecked = document.getElementById('textbooks-checkbox').checked;
    const moreQuestionsChecked = document.getElementById('more-questions-checkbox').checked;

    chatArea.innerHTML += `
        <div class="message user-message">
            <p>${marked.parse(question)}</p>
        </div>
    `;
    questionInput.value = '';

    chatArea.innerHTML += `
        <div class="message bot-message thinking-message" id="thinking-message">
            <p>Thinking...</p>
        </div>
    `;
    downloadLinkContainer.innerHTML = '';

    const formData = new URLSearchParams();
    formData.append('question', question);
    formData.append('expand', expandChecked);
    formData.append('num_questions', numQuestions);
    formData.append('summarize', summarizeChecked);
    formData.append('textbooks', textbooksChecked);
    formData.append('more_questions', moreQuestionsChecked);
    formData.append('current_thread_id', currentThreadId);

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

        (data.messages || []).forEach(message => {
            const messageClass = message.role === 'user' ? 'user-message' : 'bot-message';
            chatArea.innerHTML += `
                <div class="message ${messageClass}">
                    <p>${marked.parse(message.content, { sanitize: false })}</p>
                </div>
            `;
        });

        chatArea.scrollTop = chatArea.scrollHeight;

        if (data.thread_id) {
            currentThreadIdInput.value = data.thread_id;
        }
        if (data.filename && data.thread_id) {
            downloadLinkContainer.innerHTML = `<a href="/download/${data.filename}" download>Download Conversation</a>`;

            const newThreadLink = document.querySelector(`.thread-list-item a[data-thread-id="${data.thread_id}"]`);
            if (newThreadLink) {
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



document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('theme-toggle');
    const optionsToggle = document.getElementById('options-toggle');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const optionsSidebar = document.getElementById('options-sidebar');
    const body = document.body;
    const expandCheckbox = document.getElementById('expand-checkbox');
    const numQuestionsInput = document.getElementById('num-questions');
    const optionButtons = document.querySelectorAll('.option-button');
    const newThreadButton = document.getElementById('new-thread-button');

    // Initialize current_thread_id, handling null/None case
    let current_thread_id = null;
    if (current_thread_id === null) {
        current_thread_id = ''; // Or any other default value you want
    }

     // --- Theme Toggle ---
        const currentTheme = localStorage.getItem('theme') || 'light';
        body.setAttribute('data-theme', currentTheme);

        themeToggleButton.addEventListener('click', () => {
            const newTheme = body.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });

        // --- Options Toggle ---
         optionsToggle.addEventListener('click', () => {
          optionsSidebar.classList.toggle('show'); //show the options
        });

        // --- Sidebar Toggle ---
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });

         // --- Enable/Disable Options based on Expand ---
        function updateOptionStates() {
            const isExpanded = expandCheckbox.checked;
            numQuestionsInput.disabled = !isExpanded;

            optionButtons.forEach(button => {
                button.classList.toggle('disabled', !isExpanded);
                const checkbox = button.previousElementSibling;
                if(!isExpanded){
                    checkbox.checked = false;
                }
                checkbox.disabled = !isExpanded;
            });
        }

        updateOptionStates();
        expandCheckbox.addEventListener('change', updateOptionStates);


         // --- Thread link click ---
        document.querySelectorAll('.thread-list-item a').forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault(); // Prevent default link behavior
                const threadId = this.dataset.threadId;
                loadThread(threadId);
            });
        });

      // --- New Thread Button ---
        newThreadButton.addEventListener('click', () => {
          // Clear current chat, reset thread ID, clear input
          document.getElementById('chat-area').innerHTML = `
              <div class="message bot-message">
                  <p>Welcome! Ask me anything.</p>
              </div>
          `;
          document.getElementById('current-thread-id').value = '';
          document.getElementById('question-input').value = '';
          document.getElementById('download-link-container').innerHTML = '';

           // Remove 'active' class from all thread list items
            document.querySelectorAll('.thread-list-item').forEach(item => {
                item.classList.remove('active');
            });
      });


       // --- update Download link---
        function updateDownloadLink(threadId) {
            if(!threadId){
                document.getElementById('download-link-container').innerHTML = '';
                return;
            }
                // Create dummy form data (we only need thread ID, but server expects a POST)
                const formData = new URLSearchParams();
                formData.append('question', 'dummy'); // Dummy question
                formData.append('current_thread_id', threadId);
                formData.append('expand', 'false'); // dummy to pass server side checks
                //fetch to get file name
                fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.filename) {
                         // Update the download link with the correct filename and thread ID
                        document.getElementById('download-link-container').innerHTML = `<a href="/download/${data.filename}" download>Download Conversation</a>`;
                    }
                })
                .catch(error => {
                    console.error("Error fetching for download link update", error);
                });
        }

});