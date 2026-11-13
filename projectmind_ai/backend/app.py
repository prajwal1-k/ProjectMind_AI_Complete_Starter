import os, uuid, shutil, zipfile, tempfile, hashlib, subprocess
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

DATA_DIR = Path(os.getenv("PROJECTMIND_DATA", "/content/projectmind_data"))
REPOS_DIR = DATA_DIR / "repositories"
CHROMA_DIR = DATA_DIR / "chroma"
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5-coder:1.5b")
API_KEY = os.getenv("PROJECTMIND_API_KEY", "")
MAX_FILE_BYTES = int(os.getenv("MAX_FILE_BYTES", str(1_000_000)))
MAX_REPO_FILES = int(os.getenv("MAX_REPO_FILES", "5000"))

DATA_DIR.mkdir(parents=True, exist_ok=True)
REPOS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ProjectMind AI", version="1.0.0")
# Development default. Set FRONTEND_ORIGINS to a comma-separated allowlist for deployment.
origins = os.getenv("FRONTEND_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware, allow_origins=[x.strip() for x in origins],
    allow_credentials=False, allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"]
)

def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

def get_embeddings():
    return OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_URL)

def get_vectorstore(project_id: str):
    return Chroma(
        collection_name=f"project_{project_id.replace('-', '_')}",
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR)
    )

def safe_project_path(project_id: str) -> Path:
    p = (REPOS_DIR / project_id).resolve()
    if REPOS_DIR.resolve() not in p.parents:
        raise HTTPException(400, "Invalid project path")
    if not p.exists():
        raise HTTPException(404, "Project not found")
    return p

def list_source_files(root: Path):
    ignored = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist",
               "build", ".next", ".idea", ".vscode", "coverage", "chroma"}
    allowed = {".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss",
               ".rs", ".go", ".java", ".cpp", ".c", ".h", ".hpp", ".sql",
               ".json", ".yaml", ".yml", ".toml", ".md", ".sh"}
    count = 0
    for path in root.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        if path.suffix.lower() not in allowed and path.name not in {"Dockerfile", "Makefile"}:
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            count += 1
            if count > MAX_REPO_FILES:
                break
            yield path
        except OSError:
            continue

def split_text(text: str, size=1100, overlap=160):
    text = text.replace("\r\n", "\n")
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + size)
        if end < len(text):
            boundary = text.rfind("\n", start, end)
            if boundary > start + size // 2:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks

def source_documents(root: Path):
    docs = []
    for path in list_source_files(root):
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = str(path.relative_to(root))
        digest = hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()
        for idx, chunk in enumerate(split_text(content)):
            docs.append(Document(
                page_content=chunk,
                metadata={"path": rel, "chunk": idx, "sha256": digest,
                          "language": path.suffix.lower() or "text"}
            ))
    return docs

def index_project(project_id: str):
    root = safe_project_path(project_id)
    docs = source_documents(root)
    if not docs:
        raise HTTPException(400, "No supported source files found")
    store = get_vectorstore(project_id)
    # Rebuild collection to avoid stale chunks after a full re-index.
    try:
        store.delete_collection()
    except Exception:
        pass
    store = get_vectorstore(project_id)
    batch_size = 64
    for i in range(0, len(docs), batch_size):
        store.add_documents(docs[i:i+batch_size])
    return {"indexed_chunks": len(docs), "indexed_files": len({d.metadata["path"] for d in docs})}

class GitHubRequest(BaseModel):
    url: str
    branch: Optional[str] = None
    access_token: Optional[str] = None
    name: Optional[str] = None

class ChatRequest(BaseModel):
    question: str
    project_id: str
    k: int = 6

@app.get("/health")
def health():
    return {"status": "ok", "service": "ProjectMind AI", "chat_model": CHAT_MODEL,
            "embedding_model": EMBED_MODEL}

@app.get("/projects", dependencies=[Depends(require_api_key)])
def projects():
    items = []
    for p in REPOS_DIR.iterdir():
        if p.is_dir():
            items.append({"id": p.name, "name": p.name, "path": str(p)})
    return {"projects": items}

@app.post("/projects/upload", dependencies=[Depends(require_api_key)])
async def upload_project(file: UploadFile = File(...), name: Optional[str] = None):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Upload a .zip archive")
    project_id = uuid.uuid4().hex[:12]
    destination = REPOS_DIR / project_id
    destination.mkdir(parents=True)
    raw = await file.read()
    if len(raw) > 100 * 1024 * 1024:
        shutil.rmtree(destination, ignore_errors=True)
        raise HTTPException(413, "ZIP exceeds 100 MB limit")
    with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
        tmp.write(raw); tmp.flush()
        try:
            with zipfile.ZipFile(tmp.name) as z:
                for member in z.infolist():
                    target = (destination / member.filename).resolve()
                    if destination.resolve() not in target.parents and target != destination.resolve():
                        raise HTTPException(400, "Unsafe ZIP path detected")
                z.extractall(destination)
        except zipfile.BadZipFile:
            shutil.rmtree(destination, ignore_errors=True)
            raise HTTPException(400, "Invalid ZIP archive")
    # Flatten the common GitHub ZIP wrapper directory.
    children = list(destination.iterdir())
    if len(children) == 1 and children[0].is_dir():
        wrapper = children[0]
        for child in wrapper.iterdir():
            shutil.move(str(child), str(destination / child.name))
        wrapper.rmdir()
    return {"id": project_id, "name": name or Path(file.filename).stem,
            "message": "Project uploaded. Run analysis to build memory."}

@app.post("/projects/github", dependencies=[Depends(require_api_key)])
def clone_github(req: GitHubRequest):
    if not req.url.startswith(("https://github.com/", "https://gitlab.com/")):
        raise HTTPException(400, "Only HTTPS GitHub/GitLab repository URLs are accepted")
    project_id = uuid.uuid4().hex[:12]
    destination = REPOS_DIR / project_id
    url = req.url.rstrip("/")
    if req.access_token:
        # Token is passed to git through an environment header, not embedded in saved URL.
        env = os.environ.copy()
        env["GIT_CONFIG_COUNT"] = "1"
        env["GIT_CONFIG_KEY_0"] = "http.extraheader"
        env["GIT_CONFIG_VALUE_0"] = "AUTHORIZATION: basic " + __import__("base64").b64encode(("x-access-token:" + req.access_token).encode()).decode()
    else:
        env = os.environ.copy()
    cmd = ["git", "clone", "--depth", "1"]
    if req.branch:
        cmd += ["--branch", req.branch]
    cmd += [url, str(destination)]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=300)
    if result.returncode:
        shutil.rmtree(destination, ignore_errors=True)
        raise HTTPException(400, "Repository clone failed: " + result.stderr[-1200:])
    return {"id": project_id, "name": req.name or url.split("/")[-1].removesuffix(".git"),
            "message": "Repository cloned. Run analysis to build memory."}

@app.post("/projects/{project_id}/analyze", dependencies=[Depends(require_api_key)])
def analyze(project_id: str):
    result = index_project(project_id)
    return {"project_id": project_id, **result, "status": "indexed"}

@app.post("/chat", dependencies=[Depends(require_api_key)])
def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty")
    store = get_vectorstore(req.project_id)
    try:
        matches = store.similarity_search(req.question, k=max(1, min(req.k, 12)))
    except Exception as e:
        raise HTTPException(400, "Project memory not found. Analyze the project first.")
    if not matches:
        raise HTTPException(404, "No relevant code found. Analyze the project first.")
    context = "\n\n".join(
        f"FILE: {d.metadata.get('path')} | CHUNK: {d.metadata.get('chunk')}\n{d.page_content}"
        for d in matches
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are ProjectMind AI, a careful software engineering assistant. Answer using the supplied repository context. If context is insufficient, say so. Never invent file paths or implementation details. Cite relevant file paths in your answer."),
        ("human", "Repository context:\n{context}\n\nQuestion: {question}")
    ])
    llm = ChatOllama(model=CHAT_MODEL, base_url=OLLAMA_URL, temperature=0.1)
    response = (prompt | llm).invoke({"context": context, "question": req.question})
    sources = [{"path": d.metadata.get("path"), "chunk": d.metadata.get("chunk")} for d in matches]
    return {"answer": response.content, "sources": sources}

@app.get("/projects/{project_id}/files", dependencies=[Depends(require_api_key)])
def project_files(project_id: str):
    root = safe_project_path(project_id)
    files = [str(p.relative_to(root)) for p in list_source_files(root)]
    return {"files": files, "count": len(files)}

@app.get("/projects/{project_id}/stats", dependencies=[Depends(require_api_key)])
def project_stats(project_id: str):
    root = safe_project_path(project_id)
    files = list(list_source_files(root))
    store = get_vectorstore(project_id)
    try:
        count = store._collection.count()
    except Exception:
        count = 0
    return {"project_id": project_id, "files": len(files), "chunks": count}

@app.delete("/projects/{project_id}", dependencies=[Depends(require_api_key)])
def delete_project(project_id: str):
    root = safe_project_path(project_id)
    shutil.rmtree(root)
    try:
        get_vectorstore(project_id).delete_collection()
    except Exception:
        pass
    return {"deleted": project_id}
