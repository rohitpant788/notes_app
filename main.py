import streamlit as st
import requests

from dotenv import load_dotenv
import os

# GitHub Configuration
GITHUB_USERNAME = "rohitpant788"  # Replace with your GitHub username
NOTES_REPO = "notes_repo"  # Replace with your repository name
BRANCH = "main"  # Change if using a different branch

# Fetch token securely
load_dotenv()  # Load environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# API URLs
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{NOTES_REPO}/contents/"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{NOTES_REPO}/{BRANCH}/"


# Function to fetch directory structure from GitHub (with authentication)
def fetch_github_contents(path=""):
    url = GITHUB_API_URL + path
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}  # Use authentication

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Returns list of files/folders
    else:
        st.error(f"❌ Error {response.status_code}: {response.json().get('message', 'Unknown error')}")
        return []


# Fetch Root Contents
with st.spinner("🔄 Fetching topics from GitHub..."):
    root_contents = fetch_github_contents()

# Filter only folders (topics)
topics = {item['name']: item['path'] for item in root_contents if item['type'] == "dir"}

# Sidebar - Select a topic (folder)
if topics:
    selected_topic = st.sidebar.selectbox("📁 Select a Topic", ["Select a topic"] + list(topics.keys()))

    if selected_topic != "Select a topic":
        topic_path = topics[selected_topic]

        # Fetch Markdown files inside the selected topic
        with st.spinner(f"📄 Loading `{selected_topic}` notes..."):
            sub_contents = fetch_github_contents(topic_path)

        # Filter only Markdown files
        sub_pages = {item['name']: item['path'] for item in sub_contents if item['name'].endswith(".md")}

        # Sidebar - Select a sub-page
        if sub_pages:
            selected_page = st.sidebar.radio("📑 Select a Page", list(sub_pages.keys()))
        else:
            st.sidebar.warning("⚠️ No Markdown files found in this topic.")
            selected_page = None


        # Function to fetch and display Markdown content
        def fetch_markdown(file_path):
            url = GITHUB_RAW_URL + file_path
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}  # Use authentication
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                return f"❌ **Error {response.status_code}:** {response.json().get('message', 'Unknown error')}"


        # Display Selected Page
        if selected_page:
            st.title(f"📖 {selected_topic} - {selected_page}")
            markdown_content = fetch_markdown(sub_pages[selected_page])
            st.markdown(markdown_content, unsafe_allow_html=True)
        else:
            st.info("Select a page from the sidebar to view content.")
    else:
        st.info("Please select a topic from the sidebar.")
else:
    st.warning("⚠️ No topics found in the repository.")
