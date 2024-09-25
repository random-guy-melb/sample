import streamlit as st

# Custom CSS to completely restyle the chat input and send button
custom_css = """
<style>
    /* Target the specific Streamlit elements */
    .stChatInputContainer {
        padding-bottom: 0px !important;
    }
    .stChatInput {
        display: flex !important;
        align-items: stretch !important;
        background-color: #1E1E1E !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 0 !important;
        margin-top: 10px !important;
        overflow: hidden !important;
        height: 60px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5) !important;
    }
    .stChatInput:focus-within {
        box-shadow: 
            0 5px 15px rgba(192, 192, 192, 0.4),
            0 0 0 2px #1E1E1E,
            0 0 15px #66B2FF,
            0 0 30px #66B2FF !important;
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
        padding: 0 20px !important;
        color: white !important;
        font-family: sans-serif !important;
        font-size: 14px !important;
        flex-grow: 1 !important;
        resize: none !important;
        min-height: 60px !important;
        caret-color: #66B2FF !important; /* Neon blue caret */
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        line-height: 60px !important;
    }
    .stChatInput textarea::placeholder {
        color: #C0C0C0 !important;
        opacity: 0.8 !important;
        transition: opacity 0.3s ease !important;
    }
    .stChatInput textarea:focus::placeholder {
        opacity: 0.5 !important;
    }
    /* Ensure consistent text alignment when typing */
    .stChatInput textarea,
    .stChatInput textarea:not(:placeholder-shown) {
        line-height: 60px !important;
        padding: 0 20px !important;
    }
    .stChatInput button {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        padding: 10px 20px !important;
        cursor: pointer !important;
        transition: background-color 0.3s !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 60px !important;
        height: 100% !important;
    }
    .stChatInput button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    .stChatInput button svg {
        fill: #C0C0C0 !important;
        width: 24px !important;
        height: 24px !important;
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
</style>
"""

# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Your Streamlit app code here
st.title("Chat Input with Neon Glow and Original Send Button")
user_input = st.chat_input("Type a message...")
if user_input:
    st.write(f"You said: {user_input}")