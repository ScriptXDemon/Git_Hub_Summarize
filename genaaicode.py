import streamlit as st
import google.generativeai as genai
import os
import requests
import docx
import PyPDF2

# Configure the Generative AI model
api_key = "AIzaSyDEdlTxz472Kgf_1pKKYnHE8eN2HOvzZFA"
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

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
    
# Function to read DOCX files
def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to read PDF files
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return "\n".join(text)

# Function to fetch code from a GitHub repository and explain it
def fetch_and_explain_code_from_github(repo_url):
    try:
        repo_api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/contents"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(repo_api_url, headers=headers)
        response.raise_for_status()
        repo_contents = response.json()

        # List of supported file extensions and their languages
        file_extensions = {
            '.py': 'Python',
            '.java': 'Java',
            '.js': 'JavaScript',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.go': 'Go',
            '.ts': 'TypeScript',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.rs': 'Rust',
            '.dart': 'Dart',
            '.scala': 'Scala',
            '.r': 'R',
            '.pl': 'Perl',
            '.sh': 'Shell',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'React'
        }

        code_files = [file for file in repo_contents if any(file['name'].endswith(ext) for ext in file_extensions)]
        explanations = []

        for file in code_files:
            ext = next(ext for ext in file_extensions if file['name'].endswith(ext))
            language = file_extensions[ext]
            code_content = requests.get(file['download_url']).text
            explanation_prompt = f"Explain the following {language} code in detail:\n\n{code_content}"
            response = model.generate_content(explanation_prompt)
            explanations.append((file['name'], response.text))

        return explanations
    except Exception as e:
        st.error(f"An error occurred while fetching the code files: {e}")
        return None

# Function to fetch and explain repository file structure
def fetch_and_explain_file_structure(repo_url):
    def categorize_files(contents, structure):
        for item in contents:
            if item['type'] == 'dir':
                # Recursively fetch contents of the directory
                dir_api_url = item['url']
                dir_response = requests.get(dir_api_url, headers=headers)
                dir_response.raise_for_status()
                dir_contents = dir_response.json()
                categorize_files(dir_contents, structure)  # Recursively categorize files within the directory
            else:
                if item['name'].endswith(('.js', '.html', '.css', '.jsx', '.ts', '.tsx')):
                    structure["frontend"].append(item['name'])
                elif item['name'].endswith(('.py', '.java', '.go', '.rb', '.php', '.cpp', '.cs', '.swift')):
                    structure["backend"].append(item['name'])
                elif item['name'] in ('requirements.txt', 'package.json', 'Pipfile', 'Gemfile'):
                    structure["dependencies"].append(item['name'])
                else:
                    structure["others"].append(item['name'])

    try:
        repo_api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/contents"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(repo_api_url, headers=headers)
        response.raise_for_status()
        repo_contents = response.json()

        structure = {
            "frontend": [],
            "backend": [],
            "dependencies": [],
            "others": []
        }

        categorize_files(repo_contents, structure)  # Start the categorization process

        explanation_prompt = f"Explain the structure of the following repository with categorized files:\n\n{structure}"
        response = model.generate_content(explanation_prompt)

        return response.text
    except Exception as e:
        st.error(f"An error occurred while fetching the repository structure: {e}")
        return None


# Streamlit App
st.set_page_config(page_title="GitSummarize", page_icon="📄", layout="centered")
st.markdown(
    """
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
            color: #333333;
        }
        .stApp {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .stApp:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        h1 {
            color: #2a9d8f;
            transition: color 0.3s;
        }
        h1:hover {
            color: #21867a;
        }
        .stButton button {
            background-color: #2a9d8f;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            transition: background-color 0.3s, box-shadow 0.3s;
        }
        .stButton button:hover {
            background-color: #21867a;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("GitSummarize")

# Sidebar for options
option = st.sidebar.radio(
    "Choose an option:",
    ("Summarize File", "Summarize GitHub README", "Explain GitHub Code", "Explain File Structure", "Prompt Text")
)

if option == "Summarize File":
    st.header("Summarize a File")
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "md", "docx", "pdf"])

    if uploaded_file is not None:
        st.write("File content read. Summarizing...")

        word_count = st.number_input("Enter the number of words for the summary:", min_value=10, max_value=1000, value=100)
        if st.button("Confirm Summarization"):
            # Determine file type and read content
            file_extension = os.path.splitext(uploaded_file.name)[1]
            
            if file_extension == ".txt" or file_extension == ".md":
                file_content = uploaded_file.read().decode("utf-8")
            elif file_extension == ".docx":
                file_content = read_docx(uploaded_file)
            elif file_extension == ".pdf":
                file_content = read_pdf(uploaded_file)

            summary_prompt = f"Summarize the following content in {word_count} words:\n\n{file_content}"
            response = model.generate_content(summary_prompt)
            summary_text = response.text

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

    if st.button("Confirm Fetch and Summarize"):
        if repo_url:
            readme_content = fetch_readme_from_github(repo_url)
            if readme_content:
                st.write("README content fetched. Summarizing...")
                summary_prompt = (
                    f"Summarize the following README content in detail, "
                    f"with a length between 250 to 500 lines, and include "
                    f"the skills required to build the project:\n\n{readme_content}"
                )
                response = model.generate_content(summary_prompt)
                summary_text = response.text

                st.subheader("Detailed Summary")
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

elif option == "Explain GitHub Code":
    st.header("Fetch and Explain GitHub Code")
    repo_url = st.text_input("Enter the GitHub repository URL")

    if st.button("Confirm Fetch and Explain"):
        if repo_url:
            explanations = fetch_and_explain_code_from_github(repo_url)
            if explanations:
                st.write("Code files fetched and explained:")
                for filename, explanation in explanations:
                    st.subheader(f"File: {filename}")
                    st.write(explanation)
            else:
                st.error("Failed to fetch or explain code content.")
        else:
            st.error("Please enter a valid GitHub repository URL.")

elif option == "Explain File Structure":
    st.header("Explain GitHub Repository Structure")
    repo_url = st.text_input("Enter the GitHub repository URL")

    if st.button("Confirm Fetch and Explain Structure"):
        if repo_url:
            structure_explanation = fetch_and_explain_file_structure(repo_url)
            if structure_explanation:
                st.subheader("Repository Structure Explanation")
                st.write(structure_explanation)
            else:
                st.error("Failed to fetch or explain the repository structure.")
        else:
            st.error("Please enter a valid GitHub repository URL.")

elif option == "Prompt Text":
    st.header("Generate Content from Prompt")
    prompt_text = st.text_area("Enter your prompt:")

    if st.button("Generate Content"):
        if prompt_text:
            response = model.generate_content(prompt_text)
            st.subheader("Generated Content")
            st.write(response.text)
        else:
            st.error("Please enter a prompt.")
