# BookLeaf Publishing AI Agent 📚✨

A multi-platform AI assistant designed to automate author workflows, resolve identities across channels, and provide intelligent publishing support via RAG (Retrieval-Augmented Generation).

## 📊 Workflow Diagram
![Workflow of Assignment](https://raw.githubusercontent.com/kunalmaurya-17-24/BookLeafPub-Assignment/main/BookLeaf%20Assignment%20Workflow.png)


## 🚀 Key Features

### 1. Multi-Channel Identity Unification
- **Resolution:** Seamlessly links WhatsApp numbers, Instagram handles, and email addresses to a single author profile.
- **Fuzzy Matching:** Uses advanced string similarity (`rapidfuzz`) to handle typos and variations in usernames.
- **LLM Disambiguation:** Leverages Gemini 1.5 Pro to resolve complex identity conflicts.

### 2. Intelligent Knowledge Retrieval (RAG)
- **FAQ Support:** Directly answers complex questions about publishing rules, 21-day challenge deadlines, and royalties.
- **Contextual Search:** Uses Supabase `pgvector` for high-performance semantic search through BookLeaf's official policy documentation.
- **Author Status:** Real-time lookup of book production status, ISBNs, and payment history.

### 3. Agentic Workflow (LangGraph)
- **Stateful Logic:** Orchestrates a complex flow of intent analysis, tool selection, and response synthesis.
- **Confidence Guardrails:** Automatically flags unusual or low-confidence queries for human handover.
- **Audit Logging:** Logs every interaction (query, response, confidence score) to a centralized database for quality assurance.

## 🛠️ Tech Stack
- **AI Framework:** LangChain / LangGraph
- **LLM:** Google Gemini 1.5 Pro
- **Database:** Supabase (PostgreSQL + pgvector)
- **UIs:** Streamlit (Web) & Rich CLI (Terminal)
- **Language:** Python 3.11+

## 📥 Installation

1. Clone the repo:
   ```bash
   git clone <repo-url>
   cd BOOKLEAF
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```env
   GOOGLE_API_KEY=...
   SUPABASE_URL=...
   SUPABASE_SERVICE_KEY=...
   ```

## 🏃 Running the Demo

### **Option 1: Interactive CLI** (Best for quick testing)
```bash
python chat.py
```


### **Option 2: FastAPI Backend** (API documentation)
```bash
python main.py
```

## 🧪 Verification
Execute the automated test suite to verify all tasks:
```bash
python test_agent.py
```
Check database health:
```bash
python verify_db.py
```
