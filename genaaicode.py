import streamlit as st
import google.generativeai as genai
import requests
import os
from transformers import pipeline

# Configure the Generative AI model
api_key = "AIzaSyDEdlTxz472Kgf_1pKKYnHE8eN2HOvzZFA"
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Hugging Face models
summarizer = pipeline("summarization")
sentiment_analyzer = pipeline("sentiment-analysis")

# Function to fetch README content using GitHub API
def fetch_readme_from_github(repo_url):
    try:
        repo_api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/readme"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(repo_api_url, headers=headers)
        response.raise_for_status()
        readme_data = response.json()
        readme_text = requests.get(readme_data['download_url']).text

        return readme_text

    except Exception as e:
        st.error(f"An error occurred while fetching the README file: {e}")
        return None

# Streamlit App
st.set_page_config(page_title="GitSummarize", page_icon="📄", layout="centered")
st.markdown(
    """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #edf2f7;
            color: #333;
        }
        .stApp {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1, h2, h3 {
            color: #2a9d8f;
        }
        .stButton button {
            background-color: #2a9d8f;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            border: none;
        }
        .stButton button:hover {
            background-color: #21867a;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("GitSummarize")

# Sidebar for options
option = st.sidebar.radio(
    "Choose an option:",
    ("Summarize File", "Summarize GitHub README", "Prompt Text", "Analyze Sentiment")
)

if option == "Summarize File":
    st.header("Summarize a File")
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "md"])

    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")
        st.write("File content read. Summarizing...")

        # Hugging Face summarization
        summary_text = summarizer(file_content, max_length=150, min_length=30, do_sample=False)[0]['summary_text']

        st.subheader("Summary")
        st.write(summary_text)

        # Option to download summary
        st.download_button(
            label="Download Summary",
            data=summary_text,
            file_name="summary.txt",
            mime="text/plain"
        )

elif option == "Summarize GitHub README":
    st.header("Summarize a GitHub README")
    repo_url = st.text_input("Enter the GitHub repository URL")

    if st.button("Fetch and Summarize"):
        if repo_url:
            readme_content = fetch_readme_from_github(repo_url)
            if readme_content:
                st.write("README content fetched. Summarizing...")

                # Hugging Face summarization
                summary_text = summarizer(readme_content, max_length=150, min_length=30, do_sample=False)[0]['summary_text']

                st.subheader("Summary")
                st.write(summary_text)

                # Option to download summary
                st.download_button(
                    label="Download Summary",
                    data=summary_text,
                    file_name="readme_summary.txt",
                    mime="text/plain"
                )
            else:
                st.error("Failed to fetch README content.")
        else:
            st.error("Please enter a valid GitHub repository URL.")

elif option == "Prompt Text":
    st.header("Generate Content from Prompt")
    prompt_text = st.text_area("Enter your prompt:")

    if st.button("Generate"):
        if prompt_text:
            response = model.generate_content(prompt_text)
            st.subheader("Generated Content")
            st.write(response.text)
        else:
            st.error("Please enter a prompt.")

elif option == "Analyze Sentiment":
    st.header("Analyze Sentiment of a Text")
    text_to_analyze = st.text_area("Enter the text to analyze:")

    if st.button("Analyze"):
        if text_to_analyze:
            sentiment_result = sentiment_analyzer(text_to_analyze)[0]
            st.subheader("Sentiment Analysis")
            st.write(f"Label: {sentiment_result['label']}")
            st.write(f"Score: {sentiment_result['score']:.2f}")
        else:
            st.error("Please enter text to analyze.")
