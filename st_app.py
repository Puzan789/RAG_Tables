import streamlit as st
import requests
import json
from typing import Optional
import time

# Configuration
FASTAPI_BASE_URL = "http://127.0.0.1:8000"

# Page configuration
st.set_page_config(
    page_title="PDF Chat Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        color: #721c24;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        color: #333 !important;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
        border-left: 4px solid #2196f3;
        color: #1565c0 !important;
    }
    .assistant-message {
        background-color: #f8f9fa;
        margin-right: 2rem;
        border-left: 4px solid #28a745;
        color: #333 !important;
    }
    .assistant-message strong {
        color: #28a745 !important;
    }
    .user-message strong {
        color: #1565c0 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "chunks_uploaded" not in st.session_state:
    st.session_state.chunks_uploaded = False


# Helper functions
def make_request(endpoint: str, method: str = "GET", **kwargs) -> Optional[dict]:
    """Make HTTP request to FastAPI backend"""
    url = f"{FASTAPI_BASE_URL}/{endpoint.lstrip('/')}"

    try:
        if method.upper() == "POST":
            response = requests.post(url, **kwargs)
        else:
            response = requests.get(url, **kwargs)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error(
            "❌ Cannot connect to FastAPI server. Make sure it's running on http://127.0.0.1:8000"
        )
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def process_pdf_file(uploaded_file) -> Optional[dict]:
    """Process PDF file through FastAPI"""
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    return make_request("chunkpdf/", method="POST", files=files)


def upload_chunks_to_qdrant(summaries: list, metadata: dict) -> Optional[dict]:
    """Upload chunks to Qdrant database"""
    payload = {"summaries": summaries, "metadata": metadata}
    return make_request("uploadchunk/", method="POST", json=payload)


def send_chat_query(query: str) -> Optional[dict]:
    """Send chat query to FastAPI"""
    return make_request("chat", method="POST", params={"query": query})


# Main app layout
st.markdown(
    '<h1 class="main-header">📚 PDF Chat Assistant</h1>', unsafe_allow_html=True
)

# Sidebar for PDF processing
with st.sidebar:
    st.header("📄 PDF Processing")
    st.info(
        "💡 This section is for uploading new PDFs. You can also chat with existing documents without uploading."
    )

    uploaded_file = st.file_uploader(
        "Upload a PDF file (Optional)",
        type=["pdf"],
        help="Select a PDF file to process and add to your database",
    )

    if uploaded_file is not None:
        st.info(f"Selected file: {uploaded_file.name}")

        if st.button("🔄 Process PDF", type="primary"):
            with st.spinner("Processing PDF..."):
                result = process_pdf_file(uploaded_file)

                if result and result.get("success"):
                    st.session_state.pdf_processed = True
                    st.session_state.markdown_chunks = result.get("markdown_chunks", [])
                    st.session_state.summaries = result.get("summaries", [])
                    st.success("✅ PDF processed successfully!")
                else:
                    st.session_state.pdf_processed = False
                    st.error("❌ Failed to process PDF")

    # Upload chunks section
    if st.session_state.pdf_processed and not st.session_state.chunks_uploaded:
        st.subheader("📤 Upload to Database")

        # Metadata input
        with st.expander("Metadata (Optional)"):
            doc_title = st.text_input(
                "Document Title", value=uploaded_file.name if uploaded_file else ""
            )
            doc_author = st.text_input("Author", value="")
            doc_category = st.text_input("Category", value="")

        metadata = {
            "title": doc_title,
            "author": doc_author,
            "category": doc_category,
            "filename": uploaded_file.name if uploaded_file else "",
        }

        if st.button("📤 Upload Chunks to Database", type="primary"):
            with st.spinner("Uploading chunks..."):
                result = upload_chunks_to_qdrant(st.session_state.summaries, metadata)

                if result and result.get("success"):
                    st.session_state.chunks_uploaded = True
                    st.success("✅ Chunks uploaded successfully!")
                else:
                    st.error("❌ Failed to upload chunks")

    # Status indicators
    st.subheader("📊 Status")
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.pdf_processed:
            st.success("✅ PDF Processed")
        else:
            st.error("❌ PDF Not Processed")

    with col2:
        if st.session_state.chunks_uploaded:
            st.success("✅ Uploaded")
        else:
            st.error("❌ Not Uploaded")

# Main chat interface
st.header("💬 Chat with your Documents")

# Chat mode selection
st.subheader("📋 Chat Mode")
chat_mode = st.radio(
    "Choose how you want to chat:",
    options=["Chat with existing documents", "Upload new PDF and chat"],
    index=0,
    help="You can chat with documents already in the database or upload a new PDF",
)

# Display processing results only if PDF was processed
if st.session_state.pdf_processed and chat_mode == "Upload new PDF and chat":
    with st.expander("📋 Processing Results", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📝 Markdown Chunks")
            if hasattr(st.session_state, "markdown_chunks"):
                st.write(f"Total chunks: {len(st.session_state.markdown_chunks)}")
                for i, chunk in enumerate(
                    st.session_state.markdown_chunks[:3]
                ):  # Show first 3
                    with st.expander(f"Chunk {i + 1}"):
                        st.text_area("Content", chunk, height=100, key=f"chunk_{i}")

        with col2:
            st.subheader("📄 Summaries")
            if hasattr(st.session_state, "summaries"):
                st.write(f"Total summaries: {len(st.session_state.summaries)}")
                for i, summary in enumerate(
                    st.session_state.summaries[:3]
                ):  # Show first 3
                    with st.expander(f"Summary {i + 1}"):
                        st.text_area("Summary", summary, height=100, key=f"summary_{i}")

# Chat interface - available in both modes
chat_available = chat_mode == "Chat with existing documents" or (
    chat_mode == "Upload new PDF and chat" and st.session_state.chunks_uploaded
)

if chat_available:
    # Chat input
    user_query = st.text_input(
        "Ask a question about your documents:",
        placeholder="e.g., What topics are covered in the documents? Can you summarize the main points?",
        key="chat_input",
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        send_button = st.button("📤 Send", type="primary")
    with col2:
        clear_button = st.button("🗑️ Clear Chat")

    # Handle clear chat
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()

    # Handle send message
    if send_button and user_query.strip():
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        # Send query to FastAPI
        with st.spinner("Thinking..."):
            result = send_chat_query(user_query)

            if result and result.get("success"):
                assistant_response = result.get("response", "No response received")
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": assistant_response}
                )
            else:
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": "❌ Sorry, I couldn't process your question. Please try again.",
                    }
                )

        # Clear input and rerun
        st.rerun()

    # Display chat history
    if st.session_state.chat_history:
        st.subheader("💭 Chat History")

        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(
                    f"""
                <div class="chat-message user-message">
                    <strong>🧑 You:</strong><br>
                    {message["content"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant:</strong><br>
                    {message["content"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )

else:
    if chat_mode == "Upload new PDF and chat":
        st.info("📝 Please upload and process a PDF file first to start chatting!")
    else:
        st.warning(
            "⚠️ Make sure you have documents in your Qdrant database to chat with existing documents."
        )
        st.info(
            "💡 If you don't have any documents yet, switch to 'Upload new PDF and chat' mode to add some."
        )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>📚 PDF Chat Assistant - Chat with existing documents or upload new PDFs</p>
        <p>Make sure your FastAPI server is running on http://127.0.0.1:8000</p>
    </div>
    """,
    unsafe_allow_html=True,
)
