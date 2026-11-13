# ProjectMind AI — Colab-connected starter

A local-first codebase RAG prototype with a static HTML/CSS/JS frontend, FastAPI, LangChain, Ollama and ChromaDB.

## Included
- `frontend/index.html`: responsive dashboard, connection settings, ZIP/Git repository ingestion, analysis, file list, project stats and RAG chat.
- `backend/app.py`: FastAPI endpoints and LangChain + Ollama + ChromaDB indexing/retrieval.
- `colab/ProjectMind_AI_Colab.ipynb`: Colab setup notebook that installs Ollama, pulls models, starts FastAPI and exposes it using ngrok.

## Quick start
1. Download and extract this ZIP.
2. Open `colab/ProjectMind_AI_Colab.ipynb` in Google Colab.
3. Run notebook cells in order. Enter your ngrok auth token when prompted.
4. Upload `backend/app.py` when the notebook asks for it.
5. Copy the printed API URL and API key.
6. Open `frontend/index.html` in Chrome, paste the URL and key into Connection settings, then connect.
7. Add a ZIP repository or public GitHub URL, click Analyze, then ask questions.

## Colab notes
- Select a runtime with enough RAM; GPU is helpful but not mandatory.
- Ollama model downloads can be large. The default chat model is `qwen2.5-coder:1.5b`; embedding model is `nomic-embed-text`.
- Colab runtimes are temporary and disconnect. The notebook stores data under `/content/drive/MyDrive/ProjectMindAI` when Drive is mounted.
- Do not use Colab/ngrok as production hosting.

## Security and limitations
- The API key is a prototype access gate, not a substitute for a production identity system.
- The frontend keeps the API URL/key in `sessionStorage`; do not deploy a shared API key in a public website.
- Use only repositories you are authorized to access. Avoid uploading secrets, `.env` files, credentials or customer data.
- GitHub private-repo token support is implemented in the API but intentionally not exposed in the frontend. Add it only for trusted, private deployments.
- ZIP upload limit is 100 MB; indexing skips common build/dependency folders and files over 1 MB.
- Current indexing rebuilds a project's collection on each analysis. Incremental change-aware indexing is a next iteration.
