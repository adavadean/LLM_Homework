# Smart Librarian – AI with RAG and Tool Calling

This project implements an AI-powered book recommendation chatbot using OpenAI GPT, Retrieval-Augmented Generation (RAG) with ChromaDB, and a custom function tool to return detailed book summaries.

## Implemented Requirements

- A `book_summaries` dataset with 10+ books
- Vector store based on ChromaDB using OpenAI embeddings (`text-embedding-3-small`)
- AI chatbot that uses GPT for natural language input and responds with book recommendations
- Tool `get_summary_by_title(title: str)` integrated via function calling (OpenAI)
- Profanity filter that blocks offensive prompts from being sent to the LLM
- Frontend UI using React + Vite
- Text-to-Speech (TTS) support via Web Speech API
- Speech-to-Text (voice input) using browser’s native voice recognition
- Clear backend–frontend integration via FastAPI and REST API

## Technologies Used

- Python 3.10
- FastAPI
- OpenAI API (chat completions + embeddings + function calling)
- ChromaDB (local persistent vector store)
- Pydantic v2 with pydantic_settings
- React + Vite
- Web Speech API for TTS and STT

## How to Run

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
Access the frontend at: http://localhost:5173

```markdown
Required .env file (backend):

```env
OPENAI_API_KEY=sk-your-api-key-here
CHAT_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_DIR=./chroma_db
COLLECTION_NAME=book_summaries
ENABLE_PROFANITY_FILTER=true
TOP_K=3
CORS_ALLOW_ORIGINS=["http://localhost:5173"]

Example Prompts

I want a book about freedom and social control.
What do you recommend if I love fantasy stories?
What is the book "1984" about?
Recommend me a story involving friendship and magic.
