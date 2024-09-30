
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

 <script type="text/javascript">
        var link = document.querySelector("link[rel*='icon']");
        if (link) {
            link.remove();
        }
    </script>


custom_css = """
<style>
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
    width: 100% !important;
    margin-right: auto !important;
}

.stChatInput textarea {
    background-color: transparent !important;
    border: none !important;
    padding: 0 17px !important; /* Reduced by 15% from 20px */
    color: white !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    font-size: 18px !important; /* Original font size */
    flex-grow: 1 !important;
    resize: none !important;
    min-height: 51px !important; /* Reduced by 15% from 60px */
    line-height: 51px !important; /* Match the height for single-line vertical centering */
    overflow-x: auto !important; /* Allow horizontal scrolling */
    overflow-y: hidden !important; /* Hide vertical scrollbar */
    white-space: nowrap !important; /* Prevent line breaks */
    text-align: left !important; /* Ensure left alignment */
}

/* Hide scrollbar for Chrome, Safari and Opera */
.stChatInput textarea::-webkit-scrollbar {
    display: none !important;
}

/* Hide scrollbar for IE, Edge and Firefox */
.stChatInput textarea {
    -ms-overflow-style: none !important;  /* IE and Edge */
    scrollbar-width: none !important;  /* Firefox */
}
"""


# Add the header and subheader inside a div with the class fixed-header
st.markdown('''
<div class="fixed-header">
    <h1>Chatbot Header</h1>
    <h2>Your assistant is here to help</h2>  <!-- Subheading -->
</div>
''', unsafe_allow_html=True)
