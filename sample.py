import streamlit as st

# Custom CSS to completely restyle the chat input and send button
custom_css = """
<style>
    /* Ensure the chat input container doesn't affect surrounding areas */
    .stChatInputContainer {
        padding-bottom: 0px !important;
        background: transparent !important;
    }
    /* Target the specific Streamlit elements */
    .stChatInput {
        display: flex !important;
        align-items: stretch !important;
        background-color: #1E1E1E !important;
        border: none !important;
        border-radius: 25.5px !important; /* Reduced by 15% from 30px */
        padding: 0 !important;
        margin-top: 8.5px !important; /* Reduced by 15% from 10px */
        overflow: hidden !important;
        height: 51px !important; /* Reduced by 15% from 60px */
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5) !important; /* Slightly reduced shadow */
        width: 85% !important; /* Set width to 85% of original */
        margin-left: auto !important;
        margin-right: auto !important;
    }
    .stChatInput:focus-within {
        box-shadow: 
            0 4px 13px rgba(192, 192, 192, 0.4),
            0 0 0 2px #1E1E1E,
            0 0 13px #66B2FF,
            0 0 25px #66B2FF !important;
        transform: translateY(-2px) !important;
    }
    .stChatInput > div {
        display: flex !important;
        align-items: stretch !important;
        width: 100% !important;
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }
    .stChatInput textarea {
        background-color: transparent !important;
        border: none !important;
        padding: 0 17px !important; /* Reduced by 15% from 20px */
        color: white !important;
        font-family: sans-serif !important;
        font-size: 12px !important; /* Reduced by 15% from 14px */
        flex-grow: 1 !important;
        resize: none !important;
        min-height: 51px !important; /* Reduced by 15% from 60px */
        caret-color: #66B2FF !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        line-height: 51px !important; /* Reduced by 15% from 60px */
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
        line-height: 51px !important; /* Reduced by 15% from 60px */
        padding: 0 17px !important; /* Reduced by 15% from 20px */
    }
    .stChatInput button {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        padding: 8.5px 17px !important; /* Reduced by 15% from 10px 20px */
        cursor: pointer !important;
        transition: background-color 0.3s !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 51px !important; /* Reduced by 15% from 60px */
        height: 100% !important;
    }
    .stChatInput button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    .stChatInput button svg {
        fill: #C0C0C0 !important;
        width: 20px !important; /* Reduced by ~15% from 24px */
        height: 20px !important; /* Reduced by ~15% from 24px */
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
    /* Ensure background transparency */
    .stChatInput, .stChatInput > *, .stChatInput > * > * {
        background-color: transparent !important;
    }
    .stChatInput > div:first-child {
        background-color: #1E1E1E !important;
    }
</style>
"""

# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Your Streamlit app code here
st.title("Chat Input with Reduced Size and Improved Layout")
user_input = st.chat_input("Type a message...")
if user_input:
    st.write(f"You said: {user_input}")
