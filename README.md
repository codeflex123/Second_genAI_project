# INDmoney Mutual Fund RAG Assistant 📈🤖

An intelligent, Retrieval-Augmented Generation (RAG) based chatbot designed to provide strictly factual, up-to-date mutual fund information extracted directly from INDmoney. 

This project demonstrates a complete end-to-end AI pipeline: automated data scraping, vector database ingestion, strict AI guardrails, and a modern Streamlit user interface.

## ✨ Key Features

*   **Strict Specificity Guardrails**: The bot is programmed to *only* answer questions regarding 7 specific supported mutual funds. It explicitly refuses to hallucinate data for unsupported funds (like Parag Parikh, SBI, etc.) or provide subjective investment advice.
*   **Daily Automated Sync**: A GitHub Action runs daily at 10:00 AM IST to scrape the latest NAVs and fund data using Playwright, ensuring the chatbot's knowledge base is never stale.
*   **Local Vector Database**: Utilizes ChromaDB for efficient, local semantic search and retrieval (Zero external API costs for retrieval).
*   **Intelligent Metadata Filtering**: Eliminates cross-fund hallucinations by dynamically filtering vector search results based on the specific fund mentioned in the user's query.
*   **Premium Streamlit UI**: Features a modern, glassmorphism-inspired design with suggested questions and source citations.
*   **Dynamic Data Previews**: The automated sync also updates a [`data_preview.md`](data_preview.md) file so you can always see the exact data the bot is currently using.

## 🗂️ Supported Funds

Currently, the assistant tracks and answers questions exclusively for:
1.  ICICI Prudential Large Cap Fund
2.  HDFC Flexi Cap Fund
3.  Kotak Large Cap Fund
4.  Bank of India Flexi Cap Fund
5.  HDFC Small Cap Fund
6.  Mahindra Manulife Mid Cap Fund
7.  Motilal Oswal Large and Midcap Fund

## 🏗️ Architecture (Phase-wise)

1.  **Phase 1 - Data Ingestion (`phase1/scraper.py`)**: Asynchronous Playwright scraper that fetches live NAV, AUM, expense ratios, and FAQs from INDmoney.
2.  **Phase 2 - Vector Store (`phase2/ingest.py`)**: Processes scraped JSON data and embeds it into a persistent ChromaDB collection.
3.  **Phase 3 - LLM & RAG Backend (`phase3/bot.py`)**: Integrates Google's Gemini Flash model with strict prompt engineering and fallback mechanisms for accurate, citation-backed answers.
4.  **Phase 4 - Frontend (`app.py`)**: The user-facing Streamlit application.
5.  **Phase 5 - Orchestration (`phase5/` & `.github/workflows/data_sync.yml`)**: Automates the pipeline to keep data fresh without manual intervention.

## 🚀 How to Run Locally

### Prerequisites
*   Python 3.10+
*   Google Gemini API Key

### Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/codeflex123/Second_genAI_project.git
    cd Second_genAI_project
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

3.  **Environment Variables:**
    Create a `.env` file in the `phase3/` directory and add your Gemini API key:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

4.  **Run the Streamlit App:**
    ```bash
    streamlit run app.py
    ```
    *Note: The app will automatically initialize the database and scrape data on its first run if the vector database is empty.*

## 🧪 Try it out!

Check out [`sample_questions.md`](sample_questions.md) for a list of queries to test the bot's factual retrieval and strict guardrails.
