custom_css = """
<style>
    /* Existing chat input styles */
    .stChatInputContainer {
        padding-bottom: 0px !important;
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
    /* ... (rest of your existing styles) ... */

    /* Updated styles for chat messages */
    .chat-message {
        display: flex;
        margin-bottom: 15px;
        align-items: flex-start;
        width: 85%;
        margin-left: auto;
        margin-right: auto;
    }
    .chat-message.user {
        justify-content: flex-end;
    }
    .chat-message .message-content {
        padding: 10px 15px;
        border-radius: 20px;
        max-width: 70%;
        font-size: 12px !important;
        line-height: 1.4;
    }
    .chat-message.assistant .message-content {
        background-color: #2E4057;
        color: #ffffff;
        border-top-left-radius: 0;
    }
    .chat-message.user .message-content {
        background-color: #066AFF;
        color: #ffffff;
        border-top-right-radius: 0;
    }
    /* Ensure consistent font size for all text in message content */
    .chat-message .message-content * {
        font-size: 12px !important;
        margin: 0;
        padding: 0;
    }
</style>
"""
