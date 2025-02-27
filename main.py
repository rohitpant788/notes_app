import streamlit as st
import requests
from streamlit_tree_select import tree_select

# GitHub Configuration
GITHUB_USERNAME = "rohitpant788"  # Replace with your GitHub username
NOTES_REPO = "notes_repo"  # Replace with your repository name
BRANCH = "main"  # Change if using a different branch
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{NOTES_REPO}/contents/"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{NOTES_REPO}/{BRANCH}/"


# Function to fetch directory structure from GitHub
def fetch_github_contents(path=""):
    url = GITHUB_API_URL + path
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Returns list of files/folders
    else:
        st.error(f"❌ Error: Unable to fetch `{path}` from GitHub")
        return []


# Dark Mode Styling
st.sidebar.title("⚙️ Settings")
theme = st.sidebar.toggle("🌙 Dark Mode", value=False)

if theme:
    dark_theme = """
        <style>
            body {
                background-color: #121212;
                color: white;
            }
            .stApp {
                background-color: #121212;
            }
            .stSidebar {
                background-color: #1e1e1e;
            }
            .stMarkdown {
                color: white;
            }
        </style>
    """
    st.markdown(dark_theme, unsafe_allow_html=True)

# Sidebar Title
st.sidebar.title("📂 Notes Navigation")

# Fetch Root Contents
with st.spinner("🔄 Fetching topics..."):
    root_contents = fetch_github_contents()


# Function to build the tree structure
def build_tree(contents, parent=""):
    tree = []
    for item in contents:
        node = {
            "label": item["name"],
            "value": item["path"],
            "children": []
        }
        if item["type"] == "dir":  # If it's a folder, fetch its contents recursively
            sub_contents = fetch_github_contents(item["path"])
            node["children"] = build_tree(sub_contents, parent=item["path"])
        tree.append(node)
    return tree


# Generate tree structure dynamically
tree_data = build_tree(root_contents)

# Display tree-based navigation in sidebar
selected_node = tree_select(tree_data, use_checkbox=False)


# Fetch and display Markdown content
def fetch_markdown(file_path):
    url = GITHUB_RAW_URL + file_path
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return f"❌ **Error:** Unable to fetch `{file_path}`"


# Display selected Markdown file
if selected_node:
    selected_path = selected_node["value"]

    # Only load if it's a Markdown file
    if selected_path.endswith(".md"):
        st.title(f"📖 {selected_node['label']}")
        markdown_content = fetch_markdown(selected_path)
        st.markdown(markdown_content, unsafe_allow_html=True)
    else:
        st.info("📂 Select a Markdown file to view content.")
