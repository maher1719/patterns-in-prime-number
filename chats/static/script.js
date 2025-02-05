function askQuestion() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value;
    if (!question.trim()) return;

    const chatArea = document.getElementById('chat-area');
    const webpageList = document.getElementById('webpage-list');

    // Add user message to chat
    chatArea.innerHTML += `
        <div class="message user-message">
            <p>${question}</p>
        </div>
    `;
    questionInput.value = '';

    // Show "Thinking..." message
    chatArea.innerHTML += `
        <div class="message bot-message thinking-message" id="thinking-message">
            <p>Thinking...</p>
        </div>
    `;

    // Clear previous webpage list
    webpageList.innerHTML = '';

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            question: question
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove "Thinking..." message
        const thinkingMessage = document.getElementById('thinking-message');
        if (thinkingMessage) {
            thinkingMessage.remove();
        }
    
        // --- TEMP TEST - Display RAW JSON Response ---
        chatArea.innerHTML += `
            <div class="message bot-message final-answer-message">
                <p>Raw JSON Response: <pre>${JSON.stringify(data, null, 2)}</pre></p>
            </div>
        `;
        chatArea.scrollTop = chatArea.scrollHeight;
    
        // --- Comment out other parts of the .then block ---
        // if (data.expanded_questions && ...) { ... }
        // if (data.webpages && ...) { ... }
    })
    .then(data => {
        // Remove "Thinking..." message
        const thinkingMessage = document.getElementById('thinking-message');
        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        // --- Check for and display specific error message from backend ---
        if (data.error) {
            chatArea.innerHTML += `
                <div class="message bot-message error-message">
                    <p>Error: ${data.error}</p>  </div>`; // Display specific error message
        } // Only display regular bot response if no error
            // --- Display Expanded Questions (if any) ---
            if (data.expanded_questions && data.expanded_questions.length > 0) {
                data.expanded_questions.forEach(expanded_question => {
                    chatArea.innerHTML += `
                        <div class="message bot-message expanded-question-message">
                            <p><b>Expanded Question:</b> ${expanded_question}</p>
                        </div>
                    `;
                });
            }

            // Add bot response to chat (Final Answer)
            chatArea.innerHTML += `
                <div class="message bot-message final-answer-message">
                    <p>${data.response}</p>
                </div>
            `;
        
        chatArea.scrollTop = chatArea.scrollHeight;

        // Display scraped webpages in sidebar
        if (data.webpages && data.webpages.length > 0) {
            webpageList.innerHTML += `<h3>Scraped Webpages</h3>`; // Re-add sidebar heading if webpages exist
            data.webpages.forEach(page => {
                webpageList.innerHTML += `
                    <li><a href="${page.url}" target="_blank">${page.question} - Source</a></li>
                `;
            });
        } else {
            webpageList.innerHTML += `<li>No webpages scraped for this question.</li>`;
        }

    })
    .catch(error => {
        // Generic error handling for fetch failures (network issues, etc.) - unchanged
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