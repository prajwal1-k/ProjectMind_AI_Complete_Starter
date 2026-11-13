# 🧠 ProjectMind AI — Colab-Connected Starter

**An AI-powered codebase analysis and understanding platform built with RAG, LangChain, Ollama, ChromaDB, and FastAPI.**

ProjectMind AI is a local-first codebase RAG prototype that enables developers to upload, analyze, explore, and interact with source code repositories using natural language.

It combines a responsive HTML/CSS/JavaScript frontend with a Python FastAPI backend, LangChain orchestration, Ollama-powered language models, and ChromaDB vector storage.

The project also includes a Google Colab notebook that sets up the backend, installs Ollama, downloads the required models, and exposes the API through ngrok.

---

## ✨ Features

- **AI-Powered Codebase Analysis:** Analyze source code repositories using AI.
- **ZIP Repository Upload:** Upload project repositories as ZIP files.
- **GitHub Repository Integration:** Analyze public GitHub repositories using their URLs.
- **RAG-Based Code Understanding:** Retrieve relevant code context before generating answers.
- **AI Code Assistant:** Ask natural language questions about your project.
- **Codebase File Explorer:** View the indexed project files.
- **Project Statistics:** Display project information and analysis statistics.
- **Responsive Dashboard:** Modern frontend built using HTML, CSS, and JavaScript.
- **Ollama Integration:** Run local language models for AI-powered analysis.
- **Vector Search:** Store and retrieve code embeddings using ChromaDB.
- **Google Colab Support:** Run the backend using a cloud notebook.
- **ngrok API Tunneling:** Connect the frontend to the Colab-hosted backend.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API framework |
| LangChain | RAG pipeline and LLM orchestration |
| Ollama | Language model execution |
| Qwen 2.5 Coder | Code understanding and generation |
| Nomic Embed Text | Text embedding generation |
| ChromaDB | Vector database |
| HTML5 | Frontend structure |
| CSS3 | Responsive dashboard styling |
| JavaScript | Frontend functionality |
| Google Colab | Cloud execution environment |
| ngrok | Public API tunneling |

---

## 📂 Project Structure

```text
ProjectMind_AI_Complete_Starter/
│
├── frontend/
│   └── index.html
│
├── backend/
│   └── app.py
│
├── colab/
│   └── ProjectMind_AI_Colab.ipynb
│
├── README.md
│
└── .gitignore
```

---

## 🚀 Quick Start Guide

ProjectMind AI is designed to run its backend through Google Colab while the frontend runs locally in your browser.

### Step 1: Download the Project

Download or clone the repository:

```bash
git clone https://github.com/prajwal1-k/ProjectMind_AI_Complete_Starter.git

cd ProjectMind_AI_Complete_Starter
```

Alternatively, download the ZIP file and extract it.

### Step 2: Open Google Colab

Open:

**`colab/ProjectMind_AI_Colab.ipynb`**

Upload the notebook to Google Colab or open it directly from your downloaded project.

### Step 3: Run the Notebook

Execute the notebook cells in order.

The notebook will:

1. Install the required Python dependencies.
2. Install and configure Ollama.
3. Download the required AI models.
4. Set up the FastAPI backend.
5. Configure ChromaDB and LangChain.
6. Start the FastAPI server.
7. Expose the API using ngrok.

Enter your ngrok authentication token when prompted.

### Step 4: Upload Backend File

When the notebook requests the backend source file, upload:

```text
backend/app.py
```

### Step 5: Connect the Frontend

After successful execution, the notebook will display:

- API URL
- API Key

Copy both values.

Open:

```text
frontend/index.html
```

Use Google Chrome or another modern browser.

Navigate to the **Connection Settings** section and enter:

- API URL
- API Key

Click **Connect** to establish the frontend-backend connection.

### Step 6: Analyze Your Codebase

Once connected:

1. Upload a ZIP repository or provide a public GitHub repository URL.
2. Click **Analyze**.
3. Wait for the codebase indexing process to complete.
4. Explore the indexed files and project statistics.
5. Open the RAG chat interface.
6. Ask questions about your source code.

---

## 🧠 RAG Architecture

ProjectMind AI uses Retrieval-Augmented Generation to provide answers based on the actual source code of a project.

```text
              USER
                |
                v
       HTML / CSS / JS
          FRONTEND
                |
                v
          NGROK TUNNEL
                |
                v
           FASTAPI
           BACKEND
                |
                v
          REPOSITORY
          INGESTION
                |
         +------+------+
         |             |
         v             v
      ZIP FILE     GITHUB URL
         |             |
         +------+------+
                |
                v
         CODE EXTRACTION
                |
                v
          TEXT CHUNKING
                |
                v
         NOM​IC EMBEDDINGS
                |
                v
            CHROMADB
                |
                v
           RETRIEVAL
                |
                v
        RELEVANT CODE CONTEXT
                |
                v
        QWEN 2.5 CODER
           VIA OLLAMA
                |
                v
          AI-GENERATED
             ANSWER
                |
                v
            FRONTEND
```

---

## 🤖 AI Models

ProjectMind AI uses the following default models:

| Model | Purpose |
|---|---|
| `qwen2.5-coder:1.5b` | Code analysis and AI chat |
| `nomic-embed-text` | Generate text embeddings |

### Pull Models Using Ollama

```bash
ollama pull qwen2.5-coder:1.5b

ollama pull nomic-embed-text
```

The chat model generates responses, while the embedding model converts code and text into vector representations for semantic retrieval.

---

## ☁️ Google Colab Configuration

Google Colab provides the cloud execution environment for the backend.

### Requirements

- Google account
- Google Colab
- ngrok account
- ngrok authentication token
- Stable internet connection

### Runtime Recommendations

- Select a runtime with sufficient RAM.
- GPU acceleration is helpful but not mandatory.
- Allow sufficient time for model downloads.
- Keep the Colab session active while using the frontend.

### Persistent Storage

When Google Drive is mounted, the notebook stores project data under:

```text
/content/drive/MyDrive/ProjectMindAI
```

This helps retain project data across temporary Colab sessions, subject to the notebook's persistence implementation.

**Important:** Colab runtimes are temporary. The backend and ngrok connection will stop when the runtime disconnects.

---

## 🔐 Security and Limitations

ProjectMind AI is an experimental prototype, not a production-ready hosting platform.

### Security Considerations

- The API key is a prototype access gate, not a complete authentication system.
- The frontend stores the API URL and API key in browser `sessionStorage`.
- Never expose shared API credentials on a publicly deployed website.
- Do not upload sensitive credentials, `.env` files, API keys, or customer information.
- Only analyze repositories you are authorized to access.
- Protect private repository tokens and never commit them to GitHub.

### Current Limitations

| Limitation | Details |
|---|---|
| ZIP Upload | Maximum upload size: 100 MB |
| File Size | Files larger than 1 MB are skipped |
| Directory Filtering | Common build and dependency folders are skipped |
| GitHub Access | Public repository URLs supported in frontend |
| Private Repositories | Token support exists in the API but is not exposed in frontend |
| Indexing | Project collection is rebuilt on each analysis |
| Runtime | Google Colab sessions are temporary |
| Deployment | Colab and ngrok are not intended for production hosting |

---

## 🔮 Future Enhancements

The following improvements are planned for future versions:

- Incremental and change-aware code indexing.
- Multi-language code understanding.
- AI-powered bug detection.
- Automated code documentation.
- Code quality and complexity analysis.
- GitHub OAuth integration.
- Private repository support through secure authentication.
- Multi-project workspace management.
- Advanced dependency and architecture visualization.
- Persistent production database.
- User authentication and role-based access control.
- Production deployment with scalable infrastructure.

---

## 🎯 Use Cases

ProjectMind AI can help:

- Developers understand unfamiliar codebases.
- Students learn how software projects work.
- Development teams explore large repositories.
- Programmers locate functions and modules.
- Developers understand project architecture.
- Software engineers accelerate codebase onboarding.
- Teams ask questions about existing source code.

---

## ⭐ Support the Project

If you find ProjectMind AI useful or interesting:

- Star the GitHub repository.
- Explore the source code.
- Report bugs and suggest improvements.
- Contribute to future development.
