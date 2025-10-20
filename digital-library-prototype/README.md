# Digital Library Prototype (Hadoop-like Search Demo)

This is a **minimal working demo** of a digital library with:
- A Flask API for storing/searching items (books, presentations, videos).
- Multiple search modes: **keyword**, **boolean**, **fuzzy**.
- Faceted filters: domain, type, author contains, ISBN, year range.
- A static frontend (single HTML file) that calls the API.

> Note: This prototype uses in-memory JSON and simple heuristics.
> In your full implementation, swap the storage for **HDFS/S3** and indexing for **Elasticsearch/Solr**.

## Quickstart

### 1) Start Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
# API will run at http://localhost:8000
```

### 2) Open Frontend
- Open `frontend/index.html` in your browser.
- Make sure the backend is running at `http://localhost:8000` (you can change the base URL in the HTML if needed).

## API Endpoints

- `GET /api/health` → `{status: "ok"}`
- `GET /api/items` → list items
- `POST /api/items` → add an item (JSON body)
- `POST /api/search` → search items
  - Body: `{"q": "...", "mode": "keyword|boolean|fuzzy", "filters": {"domain":"...", "type":"book|presentation|video", "author":"...", "isbn":"...", "year_min":2020, "year_max":2024}}`

### Boolean Search Examples
- `hdfs AND (mapreduce OR replication) NOT video`
- `"distributed systems" AND replication`
- `bert OR embeddings`

## Upgrade Path (Hadoop/Elasticsearch)
- Store files in **HDFS/S3**; persist metadata in **PostgreSQL** or **NoSQL**.
- Index metadata + extracted text with **Elasticsearch**. Replace `/api/search` with ES queries (BM25, fuzzy, analyzers).
- Use **Apache Tika** to extract metadata from PDFs/PPTs; **FFmpeg/MediaInfo** for audio/video.
- Add **semantic search** with text embeddings (BERT/Sentence-Transformers) into a vector index (FAISS or OpenSearch k-NN).
- Add auth, pagination, thumbnails, upload of actual files, previews, etc.
