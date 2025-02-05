function askQuestion() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value;
    if (!question.trim()) return;

    const chatArea = document.getElementById('chat-area');
    const expandedQuestionsArea = document.getElementById('expanded-questions-area');
    const expandedQuestionsList = document.getElementById('expanded-questions-list');
    const expandCheckbox = document.getElementById('expand-checkbox');
    const expandChecked = expandCheckbox.checked;

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

    // Clear previous expanded questions and hide area initially
    expandedQuestionsList.innerHTML += '';
    //expandedQuestionsArea.classList.remove('show');


    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            question: question,
            expand: expandChecked // Send checkbox state to backend
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove "Thinking..." message
        const thinkingMessage = document.getElementById('thinking-message');
        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        // --- Display Expanded Questions and Answers (if expand was checked) ---
        if (data.is_expanded && data.expanded_questions_and_answers && data.expanded_questions_and_answers.length > 0) {
            expandedQuestionsArea.classList.add('show'); // Show expanded questions area
            data.expanded_questions_and_answers.forEach(item => {
                console.log()
                expandedQuestionsList.innerHTML += `
                    <div class="expanded-question">
                        <p><b>Question:</b> ${item.question}</p>
                        <p><b>Answer:</b> ${marked.parse(item.answer)}</p>
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


    })
    .catch(error => {
        // Error handling (unchanged)
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