import os
import streamlit as st
import requests

LANGFLOW_API_URL = os.getenv("LANGFLOW_API_URL", "http://langflow:7860")

st.title("Parallax AI")

user_input = st.text_input("Enter your prompt:")

if st.button("Submit") and user_input:
    st.info("Langflow integration not yet configured")
    # TODO: Add Langflow API call here
    # response = requests.post(f"{LANGFLOW_API_URL}/api/v1/run/...", json={...})