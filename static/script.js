// Get elements from the DOM
const summarizeButton = document.getElementById('summarize-button');
const chatButton = document.getElementById('send-message-button');
const textToSummarize = document.getElementById('text-to-summarize');
const chatMessage = document.getElementById('chat-message');
const summarizedText = document.getElementById('summarized-text');
const chatResponse = document.getElementById('chat-response');
const textToSpeechButton = document.getElementById('text-to-speech-button');
const darkModeButton = document.getElementById('dark-mode-button');
const lightModeButton = document.getElementById('light-mode-button');

// Add event listener to summarize button
summarizeButton.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
        // Get text to summarize
        const text = textToSummarize.value.trim();
        if (!text) {
            alert('Please enter text to summarize');
            return;
        }

        // Send request to summarize endpoint
        const response = await fetch('/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });

        // Check if response was successful
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Get summarized text from response
        const data = await response.json();
        const summary = data.summary;

        // Display summarized text
        summarizedText.innerText = summary;
    } catch (error) {
        console.error('Error summarizing text:', error);
        alert('Error summarizing text. Please try again.');
    }
});

// Add event listener to chat button
chatButton.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
        // Get chat message
        const message = chatMessage.value.trim();
        if (!message) {
            alert('Please enter a message');
            return;
        }

        // Send request to chat endpoint
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        // Check if response was successful
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Get chat response from response
        const data = await response.json();
        const responseText = data.response;

        // Display chat response
        chatResponse.innerText = responseText;
        chatMessage.value = ''; // Clear chat message input
    } catch (error) {
        console.error('Error chatting:', error);
        alert('Error chatting. Please try again.');
    }
});

// Add event listener to text-to-speech button
textToSpeechButton.addEventListener('click', () => {
    const text = summarizedText.innerText;
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = 'en-US';
    speech.volume = 1;
    speech.rate = 1;
    speech.pitch = 1;
    window.speechSynthesis.speak(speech);
});

// Add event listener to dark mode button
darkModeButton.addEventListener('click', () => {
    document.body.classList.add('dark-mode');
    localStorage.setItem('mode', 'dark');
});

// Add event listener to light mode button
lightModeButton.addEventListener('click', () => {
    document.body.classList.remove('dark-mode');
    localStorage.setItem('mode', 'light');
});

// Check local storage for mode
const mode = localStorage.getItem('mode');
if (mode === 'dark') {
    document.body.classList.add('dark-mode');
} else {
    document.body.classList.remove('dark-mode');
}