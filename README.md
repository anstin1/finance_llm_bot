## Finance Chatbot – Webpage Q&A with Sources

A Streamlit-based application that lets you enter up to three webpage URLs, builds a local FAISS vector index from the page content, and answers natural-language questions grounded in those sources using an OpenAI LLM via LangChain.

### Highlights
- **URL ingestion with fallback**: Attempts `UnstructuredURLLoader`; falls back to BeautifulSoup scraping if needed.
- **Chunking and embeddings**: Splits content with `RecursiveCharacterTextSplitter`, embeds with `OpenAIEmbeddings`.
- **Local vector store**: Saves a FAISS index in `faiss_index/` for reuse across sessions.
- **Grounded answers**: Answers include cited source URLs via `RetrievalQAWithSourcesChain`.

---

## Prerequisites
- **Python**: 3.10 or newer is recommended
- **OpenAI API key**: An active key with access to text generation and embeddings
- **OS**: Windows, macOS, or Linux (Windows instructions shown below; commands are similar on other OSes)

> Note: Network access is required to fetch webpages and call the OpenAI API.

---

## Project Structure
```
finance_chatbot/
  faiss_index/
    index.faiss
    index.pkl
  main.py
  requirement.txt
  README.md
```
- `main.py`: Streamlit app entrypoint; handles URL loading, chunking, embedding, FAISS index creation, and Q&A.
- `faiss_index/`: Local FAISS index files created after processing URLs.
- `requirement.txt`: Python dependencies.

---

## Setup

### 1) Clone and enter the project directory
```bash
# Windows PowerShell
cd C:\code\genAI\finance_chatbot
```

### 2) Create and activate a virtual environment (recommended)
```bash
# Create venv (Windows)
python -m venv .venv

# Activate venv (Windows PowerShell)
. .\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirement.txt
```

### 4) Configure environment variables
Create a `.env` file in the project root with your OpenAI API key:
```bash
# .env
OPENAI_API_KEY=your_openai_api_key_here
```
The app loads environment variables via `python-dotenv`.

> If you prefer, you can set `OPENAI_API_KEY` directly in your shell environment instead of using `.env`.

---

## Running the App
Run Streamlit from the project root:
```bash
streamlit run main.py
```
This will open the app in your browser (default: `http://localhost:8501`).

---

## Usage
1. In the left sidebar, provide up to three webpage URLs.
2. Click "Process URLs" to fetch, parse, split into chunks, embed, and build the local FAISS index.
   - The app first tries `UnstructuredURLLoader` with a desktop-like user agent.
   - If that fails, it falls back to BeautifulSoup and extracts text from `<p>` tags.
3. After indexing completes, ask a question in the input box.
4. The app retrieves relevant chunks from FAISS and uses an OpenAI LLM to answer, displaying both the answer and the source URLs.

> The FAISS index is saved under `faiss_index/` and reused on subsequent runs until you rebuild it.

---

## Architecture
- **UI**: `streamlit` for the interface and interaction.
- **Loading**: `langchain_community.document_loaders.UnstructuredURLLoader` with a custom User-Agent; fallback to `requests` + `beautifulsoup4`.
- **Preprocessing**: `RecursiveCharacterTextSplitter` with `chunk_size=1000` and `chunk_overlap=100`.
- **Embeddings**: `OpenAIEmbeddings` from `langchain-openai`.
- **Vector DB**: `FAISS` (CPU) from `langchain_community.vectorstores`.
- **Reasoning**: `RetrievalQAWithSourcesChain` with `OpenAI` LLM.

Data Flow:
- Input URLs → Load HTML → Extract text → Split into chunks → Embed → Build FAISS index → Retrieve relevant chunks → Generate answer with sources.

---

## Configuration Notes
- **OpenAI model selection**: The app uses `OpenAI` from `langchain_openai` with `temperature=0.9` and `max_tokens=500`. To adjust models or parameters, edit the `llm = OpenAI(...)` line in `main.py`.
- **Deserialization**: FAISS is loaded with `allow_dangerous_deserialization=True`. Only load indices that your app previously saved to avoid security risks.
- **Index location**: FAISS files are written to and loaded from `faiss_index/`. Delete this folder to force a reindex.
- **User-Agent**: Both loaders use a desktop-like UA string to improve fetch reliability.

---

## Troubleshooting
- **OpenAI API errors**: Ensure `OPENAI_API_KEY` is set and valid; verify network connectivity.
- **No content loaded**: Some sites block scraping or render content client-side. Try different URLs or ensure the fallback loader is used. Consider increasing timeouts in the fallback loader if needed.
- **Index not found**: If you see "FAISS index not found", click "Process URLs" first to create `faiss_index/`.
- **Module not found**: Re-activate your virtual environment and re-run `pip install -r requirement.txt`.
- **Windows execution policy**: If activating the venv fails, run PowerShell as Administrator and execute:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

---

## Security & Privacy
- Your URLs and content are fetched locally; embeddings and LLM calls are sent to OpenAI. Review your data handling requirements before processing sensitive URLs or content.
- Only load FAISS indices that were created by this application.

---

## Development
- Code style: Keep functions small and readable; prefer clear naming.
- Dependencies are pinned in `requirement.txt`. Update responsibly and test before bumping versions.

---

## License
Specify your license here (e.g., MIT). If omitted, the project is proprietary by default.

---

## Acknowledgements
- Built with `Streamlit`, `LangChain`, `FAISS`, and `OpenAI`.
- Fallback parsing via `requests` and `beautifulsoup4`.
