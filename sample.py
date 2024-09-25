import streamlit as st

# Custom CSS to completely restyle the chat input and send button
custom_css = """
<style>
    /* Target the specific Streamlit elements */
    .stChatInputContainer {
        padding-bottom: 0px !important;
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 70% !important; /* Reduced width */
        max-width: 800px !important;
        z-index: 1000 !important;
    }
    .stChatInput {
        display: flex !important;
        align-items: stretch !important;
        background-color: rgba(30, 30, 30, 0.8) !important; /* Semi-transparent background */
        border: none !important;
        border-radius: 25px !important; /* Slightly reduced border radius */
        padding: 0 !important;
        overflow: hidden !important;
        height: 51px !important; /* 15% reduction from 60px */
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5) !important;
    }
    .stChatInput:focus-within {
        box-shadow: 
            0 4px 12px rgba(192, 192, 192, 0.4),
            0 0 0 2px #1E1E1E,
            0 0 12px #66B2FF,
            0 0 24px #66B2FF !important;
        transform: translateY(-2px) !important;
    }
    .stChatInput > div {
        display: flex !important;
        align-items: stretch !important;
        width: 100% !important;
        padding: 0 !important;
        border: none !important;
    }
    .stChatInput textarea {
        background-color: transparent !important;
        border: none !important;
        padding: 0 17px !important; /* Slightly reduced padding */
        color: white !important;
        font-family: sans-serif !important;
        font-size: 13px !important; /* Slightly reduced font size */
        flex-grow: 1 !important;
        resize: none !important;
        min-height: 51px !important;
        caret-color: #66B2FF !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        line-height: 51px !important;
    }
    .stChatInput textarea::placeholder {
        color: #C0C0C0 !important;
        opacity: 0.8 !important;
        transition: opacity 0.3s ease !important;
    }
    .stChatInput textarea:focus::placeholder {
        opacity: 0.5 !important;
    }
    .stChatInput textarea,
    .stChatInput textarea:not(:placeholder-shown) {
        line-height: 51px !important;
        padding: 0 17px !important;
    }
    .stChatInput button {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        padding: 8px 17px !important; /* Slightly reduced padding */
        cursor: pointer !important;
        transition: background-color 0.3s !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 51px !important;
        height: 100% !important;
    }
    .stChatInput button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    .stChatInput button svg {
        fill: #C0C0C0 !important;
        width: 20px !important; /* Slightly reduced size */
        height: 20px !important;
    }
    /* Remove all default focus styles and any unwanted borders */
    .stChatInput *:focus,
    .stChatInput *:hover,
    .stChatInput *:active,
    .stChatInput:focus-within,
    .stChatInput:focus-within > *,
    .stChatInput:focus-within > * > * {
        outline: none !important;
        border: none !important;
    }
    /* Ensure no unwanted border appears */
    .stChatInput,
    .stChatInput > *,
    .stChatInput > * > *,
    .stChatInput:focus-within,
    .stChatInput:focus-within > *,
    .stChatInput:focus-within > * > * {
        border-color: transparent !important;
    }
    /* Adjust main content area to make room for fixed chat input */
    .main .block-container {
        padding-bottom: 80px !important;
    }
</style>
"""

# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Your Streamlit app code here
st.title("Chat Input with Reduced Size and Improved Visibility")
user_input = st.chat_input("Type a message...")
if user_input:
    st.write(f"You said: {user_input}")
