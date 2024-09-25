
import streamlit as st

# Hide Streamlit default elements (MainMenu, footer, deploy and running icons)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stStatus {visibility: hidden;}  /* This hides the "running" and "deploy" icons */
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


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
        width: 100% !important;  /* Changed from 85% to 100% */
        /* Removed margin-left and margin-right to align elements */
    }

    /* Neon animation */
    @keyframes neon-hue-rotate {
        0% {
            box-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 30px #ff00ff, 0 0 40px #ff00ff;
        }
        25% {
            box-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff, 0 0 40px #00ffff;
        }
        50% {
            box-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 30px #ff00ff, 0 0 40px #ff00ff;
        }
        75% {
            box-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00, 0 0 30px #00ff00, 0 0 40px #00ff00;
        }
        100% {
            box-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 30px #ff00ff, 0 0 40px #ff00ff;
        }
    }

    /* Styling for chat input neon effect and raised effect */
    .stTextInput > div > input:focus {
        animation: neon-hue-rotate 2s infinite alternate;
        border: none;
        outline: none;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 0, 0, 0.4);  /* Raised effect */
        transform: translateY(-3px);  /* Slight upward lift */
    }

    /* Styling for header effect */

    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(to right, #066AFF, #15B392);  /* Gradient from #066AFF to #15B392 */
        border: 2px solid white;  /* White border around the header */
        padding: 20px;
        z-index: 9999;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;  /* Center-align the header */
    }
    body {
        padding-top: 120px;  /* Adjust padding to make space for the fixed header */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    h1 {
        color: white; /* Header text color */
        font-size: 32px; /* Main header font size */
        margin: 0;  /* Remove margin */
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4); /* Subtle shadow for raised effect */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    h2 {
        color: white; /* Subheader text color */
        font-size: 20px; /* Subheader font size */
        margin: 5px 0 0 0;  /* Reduce margin between header and subheader */
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    
    /* ... (rest of your existing styles for chat input) ... */

    /* Updated styles for chat messages */
    .chat-message {
        display: flex;
        margin-bottom: 20px;
        align-items: flex-start;
        width: 100%;  /* Changed from 85% to 100% */
        /* Removed margin-left and margin-right to align elements */
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
        max-width: none;  /* Removed max-width to allow full width */
        margin: 0;
    }
</style>
"""


# Add the header and subheader inside a div with the class fixed-header
st.markdown('''
<div class="fixed-header">
    <h1>Chatbot Header</h1>
    <h2>Your assistant is here to help</h2>  <!-- Subheading -->
</div>
''', unsafe_allow_html=True)
