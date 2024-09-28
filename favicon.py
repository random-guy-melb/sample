import streamlit as st
from PIL import Image
import base64

def add_logo(logo_path, width, height):
    """Read and return a resized logo"""
    logo = Image.open(logo_path)
    modified_logo = logo.resize((width, height))
    return modified_logo

my_logo = add_logo(logo_path="assets/your_favicon.png", width=50, height=50)
st.set_page_config(page_title="Your App Title", page_icon=my_logo)
