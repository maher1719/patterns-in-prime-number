// static/script.js (No changes needed)
function askQuestion() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value;
    if (!question.trim()) return;

    const chatArea = document.getElementById('chat-area');
    const expandCheckbox = document.getElementById('expand-checkbox');
    const expandChecked = expandCheckbox.checked;
    const downloadLinkContainer = document.getElementById('download-link-container');

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
    formData.append('num_questions', numQuestions); // Add num_questions
    formData.append('summarize', summarizeChecked); // Add summarize
    formData.append('textbooks', textbooksChecked);   // Add textbooks
    formData.append('more_questions', moreQuestionsChecked);


    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData  // Use the constructed formData
    })
    .then(response => response.json())
    .then(data => {
        const thinkingMessage = document.getElementById('thinking-message');
        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        // Display *all* messages in the chat area
        (data.messages || []).forEach(message => {
          const messageClass = message.role === 'user' ? 'user-message' : 'bot-message';
          chatArea.innerHTML += `
              <div class="message ${messageClass}">
                  <p>${marked.parse(message.content, { sanitize: false })}</p>
              </div>
          `;
      });

        chatArea.scrollTop = chatArea.scrollHeight;

        // Add download link (if filename is provided)
        if (data.filename) {
            downloadLinkContainer.innerHTML = `<a href="/download/${data.filename}" download>Download Conversation</a>`;
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


// --- Dark Mode Toggle ---
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('theme-toggle');
    const body = document.body;

    // Check for saved theme preference
    const currentTheme = localStorage.getItem('theme') || 'light';
    body.setAttribute('data-theme', currentTheme);

    themeToggleButton.addEventListener('click', () => {
        const newTheme = body.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme); // Save preference
    });
});