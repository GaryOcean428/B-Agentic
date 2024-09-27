import * as msgs from "./messages.js"

const splitter = document.getElementById('splitter');
const leftPanel = document.getElementById('left-panel');
const container = document.querySelector('.container');
const chatInput = document.getElementById('chat-input');
const chatHistory = document.getElementById('chat-history');
const sendButton = document.getElementById('send-button');
const inputSection = document.getElementById('input-section');
const statusSection = document.getElementById('status-section');
const chatsSection = document.getElementById('chats-section');

let isResizing = false;
let autoScroll = true;

let context = "";

splitter.addEventListener('mousedown', (e) => {
    isResizing = true;
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
});

function resize(e) {
    if (isResizing) {
        const newWidth = e.clientX - container.offsetLeft;
        leftPanel.style.width = `${newWidth}px`;
    }
}

function stopResize() {
    isResizing = false;
    document.removeEventListener('mousemove', resize);
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
        try {
            console.log('Sending message:', message);
            setMessage(Date.now(), 'user', 'User message', message);
            const response = await sendJsonData("/msg", { message: message, ctxid: context });
            console.log('Response received:', response);
            if (response.status === "success") {
                chatInput.value = '';
                adjustTextareaHeight();
                if (response.response) {
                    setMessage(Date.now(), 'agent', 'AI response', response.response);
                }
            } else {
                console.error('Error sending message:', response.message);
                alert('Error sending message: ' + response.message);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Error sending message: ' + error.message);
        }
    }
}

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendButton.addEventListener('click', sendMessage);

function setMessage(id, type, heading, content, kvps = null) {
    console.log('Setting message:', { id, type, heading, content, kvps });
    // Search for the existing message container by id
    let messageContainer = document.getElementById(`message-${id}`);

    if (messageContainer) {
        // Clear the existing container's content if found
        messageContainer.innerHTML = '';
    } else {
        // Create a new container if not found
        const sender = type === 'user' ? 'user' : 'ai';
        messageContainer = document.createElement('div');
        messageContainer.id = `message-${id}`;
        messageContainer.classList.add('message-container', `${sender}-container`);
    }

    const handler = msgs.getHandler(type);
    handler(messageContainer, id, type, heading, content, kvps);

    // If the container was found, it was already in the DOM, no need to append again
    if (!document.getElementById(`message-${id}`)) {
        chatHistory.appendChild(messageContainer);
    }

    if (autoScroll) chatHistory.scrollTop = chatHistory.scrollHeight;
}

function adjustTextareaHeight() {
    chatInput.style.height = 'auto';
    chatInput.style.height = (chatInput.scrollHeight) + 'px';
}

async function sendJsonData(url, data) {
    console.log('Sending JSON data:', { url, data });
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    const jsonResponse = await response.json();
    console.log('Received JSON response:', jsonResponse);

    if (!response.ok) {
        throw new Error(jsonResponse.message || 'Network response was not ok');
    }

    return jsonResponse;
}

function generateGUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0;
        var v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

let lastLogVersion = 0;
let lastLogGuid = ""

async function poll() {
    try {
        const response = await sendJsonData("/poll", { log_from: lastLogVersion, context });
        console.log('Poll response:', response);

        if (response.ok) {
            setContext(response.context)

            if (lastLogGuid != response.log_guid) {
                chatHistory.innerHTML = ""
                lastLogVersion = 0
            }

            if (lastLogVersion != response.log_version) {
                for (const log of response.logs) {
                    setMessage(log.no, log.type, log.heading, log.content, log.kvps);
                }
            }

            //set ui model vars from backend
            const inputAD = Alpine.$data(inputSection);
            inputAD.paused = response.paused;
            const statusAD = Alpine.$data(statusSection);
            statusAD.connected = response.ok;
            const chatsAD = Alpine.$data(chatsSection);
            chatsAD.contexts = response.contexts;

            lastLogVersion = response.log_version;
            lastLogGuid = response.log_guid;
        }
    } catch (error) {
        console.error('Error in poll:', error);
        const statusAD = Alpine.$data(statusSection);
        statusAD.connected = false;
    }
}

window.pauseAgent = async function (paused) {
    const resp = await sendJsonData("/pause", { paused: paused, context });
}

window.resetChat = async function () {
    const resp = await sendJsonData("/reset", { context });
}

window.newChat = async function () {
    setContext(generateGUID());
}

window.killChat = async function (id) {
    const chatsAD = Alpine.$data(chatsSection);
    let found, other
    for (let i = 0; i < chatsAD.contexts.length; i++) {
        if (chatsAD.contexts[i].id == id) {
            found = true
        } else {
            other = chatsAD.contexts[i]
        }
        if (found && other) break
    }

    if (context == id && found) {
        if (other) setContext(other.id)
        else setContext(generateGUID())
    }

    if (found) sendJsonData("/remove", { context: id });
}

window.selectChat = async function (id) {
    setContext(id)
}

const setContext = function (id) {
    if (id == context) return
    context = id
    lastLogGuid = ""
    lastLogVersion = 0
    const chatsAD = Alpine.$data(chatsSection);
    chatsAD.selected = id
}

window.toggleAutoScroll = async function (_autoScroll) {
    autoScroll = _autoScroll;
}

window.toggleJson = async function (showJson) {
    toggleCssProperty('.msg-json', 'display', showJson ? 'block' : 'none');
}

window.toggleThoughts = async function (showThoughts) {
    toggleCssProperty('.msg-thoughts', 'display', showThoughts ? undefined : 'none');
}

function toggleCssProperty(selector, property, value) {
    const styleSheets = document.styleSheets;
    for (let i = 0; i < styleSheets.length; i++) {
        const styleSheet = styleSheets[i];
        const rules = styleSheet.cssRules || styleSheet.rules;
        for (let j = 0; j < rules.length; j++) {
            const rule = rules[j];
            if (rule.selectorText == selector) {
                if (value === undefined) {
                    rule.style.removeProperty(property);
                } else {
                    rule.style.setProperty(property, value);
                }
                return;
            }
        }
    }
}

chatInput.addEventListener('input', adjustTextareaHeight);

setInterval(poll, 250);
