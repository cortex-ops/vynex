const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const filePreviewContainer = document.getElementById('file-preview-container');
const fileNameEl = document.getElementById('file-name');
const removeFileBtn = document.getElementById('remove-file-btn');
const overlayBody = document.querySelector('.flex-1.flex.flex-col'); // Get the main body
const toggleBtn = document.getElementById('toggle-overlay'); // Get toggle button

let attachedFile = null;
let isMinimized = false; // State for toggling

// --- Event Listeners ---

// Toggle minimize/maximize
toggleBtn.addEventListener('click', () => {
    isMinimized = !isMinimized;
    overlayBody.classList.toggle('hidden');
    
    // Toggle icon
    if (isMinimized) {
        toggleBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
        </svg>`;
    } else {
        toggleBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>`;
    }
});

// Handle sending message on button click
sendBtn.addEventListener('click', handleSend);

// Handle sending message on "Enter" key press
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});

// Handle file upload button click
uploadBtn.addEventListener('click', () => {
    fileInput.click();
});

// Handle file selection
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        attachedFile = file;
        fileNameEl.textContent = file.name;
        filePreviewContainer.classList.remove('hidden');
        filePreviewContainer.classList.add('flex');
    }
});

// Handle remove file button
removeFileBtn.addEventListener('click', () => {
    attachedFile = null;
    fileInput.value = null; // Reset the file input
    filePreviewContainer.classList.add('hidden');
    filePreviewContainer.classList.remove('flex');
});

// --- Core Functions ---

/**
 * Handles sending the user's message and/or file
 */
async function handleSend() {
    const userInput = chatInput.value.trim();

    if (!userInput && !attachedFile) {
        return; // Don't send empty messages
    }

    // Keep file and text separate for the API call
    const textToSend = userInput;
    const fileToSend = attachedFile;

    // 1. Add user message to chat
    let userMessage = userInput;
    if (fileToSend) {
        userMessage = userInput ? `${userInput} [${fileToSend.name}]` : `[${fileToSend.name}]`;
    }
    addUserMessage(userMessage);

    // 2. Clear inputs
    chatInput.value = '';
    removeFileBtn.click(); // This will clear the file state

    // 3. Show typing indicator
    const thinkingMessage = addBotMessage("Thinking...", true);

    // 4. Call your backend API
    try {
        // *** THIS IS WHERE YOU CALL YOUR PYTHON (Flask/FastAPI) BACKEND ***
        const botResponse = await callGeminiAPI(textToSend, fileToSend);

        // 5. Update typing indicator with actual response
        thinkingMessage.querySelector('p').textContent = botResponse;
        console.log(botResponse);

    } catch (error) {
        console.error("Error calling API:", error);
        thinkingMessage.querySelector('p').textContent = "Sorry, I ran into an error. Please try again.";
        thinkingMessage.classList.add('bg-red-500'); // Optional: error styling
    } finally {
        // Remove the "thinking" animation class
        thinkingMessage.querySelector('p').classList.remove('animate-pulse');
        scrollToBottom();
    }
}

/**
 * Converts a File object to a Base64 string.
 * @param {File} file - The file to convert
 * @returns {Promise<string>} - A promise that resolves with the Base64 data URL
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

/**
 * Calls your Python backend API
 * @param {string} text - The user's text input
 * @param {File} file - The attached file (or null)
 * @returns {Promise<string>} - A promise that resolves with the bot's response
 */
async function callGeminiAPI(text, file) {
    console.log("Calling Python backend with:");
    console.log("Text:", text);
    console.log("File:", file ? file.name : "None");

    // const-api-key = ""; // Your Gemini API Key
    const apiUrl = "http://127.0.0.1:5000/chat"; // Example: Local Flask server URL

    let fileData = null;
    let fileMimeType = null;

    if (file) {
        // Convert file to Base64. The result includes the data URL prefix (e.g., "data:image/png;base64,")
        const base64String = await fileToBase64(file);
        // Split the prefix from the actual data
        const parts = base64String.split(';base64,');
        fileMimeType = parts[0].split(':')[1];
        fileData = parts[1]; // Just the Base64 data
    }

    // Construct the payload for your Python backend
    const payload = {
        text: text,
        file_data: fileData,      // This will be the Base64 string
        file_mime_type: fileMimeType // e.g., "image/png" or "text/plain"
    };

    // Your Python backend will receive this JSON.
    // In Flask, you'd get this with `data = request.json`
    // `data['text']`
    // `data['file_data']` (which you'll need to base64.b64decode())
    // `data['file_mime_type']`

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json(); // Assuming your backend returns JSON { "response": "..." }

        return result.response; // Get the text response from the JSON

    } catch (error) {
        console.error("Failed to fetch from backend:", error);
        return "Error: Could not connect to the backend service.";
    }
}

// --- UI Helper Functions ---

/**
 * Adds a user message bubble to the chat container
 * @param {string} message - The text to display
 */
function addUserMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'flex items-start space-x-3 justify-end';
    messageEl.innerHTML = `
        <div class="bg-indigo-600 p-3 rounded-lg rounded-br-none shadow-md max-w-xs md:max-w-md">
            <p class="text-sm text-white" style="white-space: pre-wrap; word-wrap: break-word;">${escapeHTML(message)}</p>
        </div>
        <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-600 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
        </div>
    `;
    chatContainer.appendChild(messageEl);
    scrollToBottom();
}

/**
 * Adds a bot message bubble to the chat container
 * @param {string} message - The text to display
 * @param {boolean} [isThinking=false] - Whether to show a typing indicator
 * @returns {HTMLElement} - The message element that was added
 */
function addBotMessage(message, isThinking = false) {
    const messageEl = document.createElement('div');
    messageEl.className = 'flex items-start space-x-3';
    
    const thinkingClass = isThinking ? 'animate-pulse' : '';
    
    messageEl.innerHTML = `
        <div class="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M12 21v-1" />
            </svg>
        </div>
        <div class="bg-gray-700 p-3 rounded-lg rounded-tl-none shadow-md max-w-xs md:max-w-md">
            <p class="text-sm text-gray-200 ${thinkingClass}" style="white-space: pre-wrap; word-wrap: break-word;">${escapeHTML(message)}</p>
        </div>
    `;  
    chatContainer.appendChild(messageEl);
    scrollToBottom();
    return messageEl;
}

/**
 * Scrolls the chat container to the bottom
 */
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Escapes HTML to prevent XSS
 * @param {string} str - The string to escape
 * @returns {string} - The escaped string
 */
function escapeHTML(str) {
    return str.replace(/[&<>"']/g, function(m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m];
    });
}