import os
import time
import streamlit as st
from dotenv import load_dotenv

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import OpenAI

load_dotenv()

st.set_page_config(page_title="Webpage Q&A", layout="wide")
st.title("🌐 Webpage Q&A with Sources")
st.sidebar.title("Webpage URLs")

main_placeholder = st.empty()
faiss_folder = "faiss_index"  # folder to save FAISS index

# --- Sidebar URL inputs ---
urls = []
for i in range(1, 4):
    url = st.sidebar.text_input(f"URL {i}", key=f"url_{i}")
    if url.strip():
        urls.append(url.strip())

process_url_clicked = st.sidebar.button("Process URLs")


# --- Fallback loader using BeautifulSoup ---
def fallback_bs4_loader(urls):
    import requests
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    docs = []
    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                st.warning(f"⚠️ Failed to fetch {url} (status {res.status_code})")
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            text = " ".join([p.text for p in soup.find_all("p")])
            if text.strip():
                docs.append(Document(page_content=text, metadata={"source": url}))
                st.success(f"✅ Loaded {url} (BeautifulSoup)")
            else:
                st.warning(f"⚠️ No readable text found at {url}")
        except Exception as e:
            st.error(f"Error fetching {url}: {e}")
    return docs


# --- Main logic ---
if process_url_clicked:
    if not urls:
        st.error("Please enter at least one valid URL.")
    else:
        main_placeholder.info("🔄 Loading data from URLs...")
        data = []

        # --- Step 1: Try UnstructuredURLLoader (fast) ---
        try:
            from langchain_community.document_loaders import UnstructuredURLLoader

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            loader = UnstructuredURLLoader(urls=urls, headers=headers)
            data = loader.load()
        except Exception as e:
            st.warning(f"⚠️ Unstructured loader failed: {e}")

        # --- Step 2: Fallback to BeautifulSoup ---
        if not data or len(data) == 0:
            st.info("Using BeautifulSoup fallback...")
            data = fallback_bs4_loader(urls)

        st.write("Loaded docs:", len(data))

        if len(data) == 0:
            st.error("❌ No content could be loaded. Check your URLs or site accessibility.")
        else:
            # --- Split text into chunks ---
            text_splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", ".", ","],
                chunk_size=1000,
                chunk_overlap=100,
            )
            docs = text_splitter.split_documents(data)
            st.write("Number of split docs:", len(docs))

            # --- Generate embeddings ---
            main_placeholder.info("⚙️ Generating embeddings and building FAISS index...")
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_documents(docs, embeddings)

            # --- Save FAISS index safely ---
            vectorstore.save_local(faiss_folder)
            main_placeholder.success(f"✅ FAISS index saved locally at '{faiss_folder}'!")


llm = OpenAI(temperature=0.9, max_tokens=500)

query = st.text_input("Ask a question:")
if query:
    if not os.path.exists(faiss_folder):
        st.error("FAISS index not found. Please process URLs first.")
    else:
        st.info("🔍 Searching for answers...")

        # Load FAISS index safely
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local(
            faiss_folder,
            embeddings,
            allow_dangerous_deserialization=True
        )

        chain = RetrievalQAWithSourcesChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever()
        )

        result = chain({"question": query})
        st.write("**Answer:**", result['answer'])
        st.write("**Sources:**", result['sources'])