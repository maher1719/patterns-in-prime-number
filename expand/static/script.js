function askQuestion() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value;
    if (!question.trim()) return;

    const chatArea = document.getElementById('chat-area');
    const webpageList = document.getElementById('webpage-list');
    const expandedQuestionsArea = document.getElementById('expanded-questions-area'); // Get expanded questions area
    const expandedQuestionsList = document.getElementById('expanded-questions-list'); // Get expanded questions list
    const finalAnswerArea = document.getElementById('final-answer-area'); // Get final answer area
    const finalAnswerContent = document.getElementById('final-answer-content'); // Get final answer content
    const expandCheckbox = document.getElementById('expand-checkbox'); // Get checkbox element
    const expandQuestion = expandCheckbox.checked; // Get checkbox state (true/false)


    // Add user message to chat
    chatArea.innerHTML += `
        <div class="message user-message">
            <p>${question}</p>
        </div>
    `;
    questionInput.value = '';

    // Show "Thinking..." message in final answer area
    finalAnswerContent.innerHTML = `
        <div class="message bot-message thinking-message" id="thinking-message">
            <p>Thinking...</p>
        </div>
    `;

    // Hide expanded questions area and clear webpage list on new question
    expandedQuestionsArea.style.display = 'none'; // Hide expanded questions area
    webpageList.innerHTML = '';
    expandedQuestionsList.innerHTML = ''; // Clear expanded question list


    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            question: question,
            expand_question: expandQuestion // Send checkbox state to backend
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove "Thinking..." message
        const thinkingMessage = document.getElementById('thinking-message');
        if (thinkingMessage) {
            thinkingMessage.remove();
        }

        // --- Check for and display specific error message from backend ---
        if (data.error) {
            finalAnswerContent.innerHTML = `
                <div class="message bot-message error-message">
                    <p>Error: ${data.error}</p>  </div>`; // Display error in final answer area
        } else { // Only display regular bot response if NO error
            // --- Display Expanded Questions (if any and if checkbox was checked) ---
            if (expandQuestion && data.expanded_questions && data.expanded_questions.length > 0) {
                expandedQuestionsArea.style.display = 'block'; // Show expanded questions area
                data.expanded_questions.forEach(expanded_question => {
                    expandedQuestionsList.innerHTML += `
                        <li>${expanded_question}</li>
                    `;
                });
            } else {
                expandedQuestionsArea.style.display = 'none'; // Hide if no expanded questions or checkbox unchecked
            }


            // Add bot response to Final Answer Area (Final Answer)
            finalAnswerContent.innerHTML = `
                <div class="message bot-message final-answer-message">
                    <p>${data.response}</p>
                </div>
            `;
        }
        chatArea.scrollTop = chatArea.scrollHeight;

        // Display scraped webpages in sidebar (unchanged)
        if (data.webpages && data.webpages.length > 0) {
            webpageList.innerHTML += `<h3>Scraped Webpages</h3>`;
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
        // Generic error handling (unchanged)
        const thinkingMessage = document.getElementById('thinking-message');
        if (thinkingMessage) {
            thinkingMessage.remove();
        }
        finalAnswerContent.innerHTML += `
            <div class="message bot-message error-message">
                <p>Error: Could not get response. Please try again.</p>
            </div>
        `;
        console.error('Fetch Error:', error);
    });
}