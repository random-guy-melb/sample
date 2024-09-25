custom_css = """
<style>
    /* Existing chat input styles */
    .stChatInputContainer {
        padding-bottom: 20px !important;
        background: transparent !important;
    }
    .stChatInput {
        display: flex !important;
        align-items: stretch !important;
        background-color: #1E1E1E !important;
        border: none !important;
        border-radius: 25.5px !important;
        padding: 0 !important;
        margin-top: 8.5px !important;
        overflow: hidden !important;
        height: 51px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5) !important;
        width: 85% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* ... (rest of your existing styles for chat input) ... */

    /* Updated styles for chat messages */
    .chat-message {
        display: flex;
        margin-bottom: 20px;
        align-items: flex-start;
        width: 85%;
        margin-left: auto;
        margin-right: auto;
    }
    .chat-message.user {
        flex-direction: row-reverse;
    }
    .chat-message .message-content {
        padding: 15px 20px;
        border-radius: 20px;
        max-width: 80%;
        font-size: 14px !important;
        line-height: 1.5;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .chat-message.assistant .message-content {
        background-color: #2E4057;
        color: #ffffff;
        border-top-left-radius: 5px;
        margin-left: 10px;
    }
    .chat-message.user .message-content {
        background-color: #066AFF;
        color: #ffffff;
        border-top-right-radius: 5px;
        margin-right: 10px;
    }
    /* Ensure consistent font size for all text in message content */
    .chat-message .message-content * {
        font-size: 14px !important;
        margin: 0;
        padding: 0;
    }
    /* Add visual cues for roles */
    .chat-message::before {
        content: '';
        width: 30px;
        height: 30px;
        min-width: 30px;
        border-radius: 50%;
        background-size: cover;
    }
    .chat-message.assistant::before {
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%232E4057"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>');
    }
    .chat-message.user::before {
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23066AFF"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>');
    }
    /* Improve overall layout */
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
</style>
"""
