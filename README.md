# PX4 RAG Chatbot

An open-source Retrieval-Augmented Generation chatbot for the PX4 Autopilot documentation. Built as a portfolio project to demonstrate RAG pipeline design and full-stack chatbot development, and as a contribution to the PX4 open-source community.

Ask natural-language questions about PX4 flight modes, configuration, parameters, and development — get answers grounded in the actual PX4 user guide, with streaming responses over WebSocket.

---

## Status

**v1.0 — complete and working end to end.** Backend retrieves and streams grounded answers; frontend is a working ground-control-style chat console connected over WebSocket.

This is a completed MVP, not a finished product. See [Future contributions](#future-contributions) for the next round of improvements already identified — QGroundControl docs being the first.

---

## Architecture

```
PX4-user_guide (cloned repo, docs/en/**/*.md)
        |
        v
  repo_loader.py  --> output.json (raw_text + relative_path per file)
        |
        v
  chunker.py      --> chunks.json (heading-based chunks, clean_text)
        |
        v
  embedder.py (HF Inference API, all-MiniLM-L6-v2)
        |
        v
  milvus_store.py --> Milvus Lite (milvus_px4.db, dim=384, auto_id)
        |
   [query time]
        v
  retriever.py     --> top-5 chunks via vector search
        |
        v
  prompt_builder.py --> formatted prompt (context + history + question)
        |
        v
  llm.py (Llama-3.3-70B-Instruct via HF Inference Providers, streaming)
        |
        v
  main.py (FastAPI WebSocket /chat) --> streams tokens to client
        |
        v
  Angular frontend (ground-control console UI, signals + WebSocket service)
```

---

## Tech stack

| Layer      | Choice                                                                                 | Why                                                                                                                                                    |
| ---------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Doc source | PX4-user_guide GitHub repo (cloned locally)                                            | Live scraping was abandoned — too much content, repo is the source of truth anyway                                                                    |
| Chunking   | Heading-based (manual`#` parsing, not a markdown library)                            | Data has Vitepress/Vue syntax a generic parser would mishandle; line-walking gave full control                                                         |
| Vector DB  | Milvus Lite                                                                            | Free, embedded, no Docker — matches "open source, zero infra" goal                                                                                    |
| Embeddings | HuggingFace Inference API,`sentence-transformers/all-MiniLM-L6-v2`                   | Free tier, 384-dim, no local GPU needed                                                                                                                |
| LLM        | `meta-llama/Llama-3.3-70B-Instruct` via HF Inference Providers (`provider="auto"`) | Mistral-7B-Instruct-v0.3 is NOT available on free`hf-inference` tier (CPU-only, small models) — this was a real debugging detour, see Decisions Log |
| Backend    | FastAPI + WebSocket                                                                    | Bidirectional, natural fit for streaming conversation                                                                                                  |
| Frontend   | Angular                                                                                | Chosen for type safety and structure                                                                                                                   |
| History    | Client-side, sent with every message                                                   | Stateless server — privacy by design, scales for free                                                                                                 |

---

## Repo structure

```
PX4-chatbot/
├── ingestion/
│   ├── repo_loader.py      # walks docs/en/**/*.md, reads raw text
│   ├── chunker.py          # clean() + heading-based chunk()
│   ├── output.json         # gitignored — regenerate locally
│   └── chunks.json         # gitignored — regenerate locally
├── vectordb/
│   ├── embedder.py         # embed(text) -> 384-float vector via HF
│   ├── milvus_store.py     # create_collection(), insert_into_collection()
│   └── milvus_px4.db/      # gitignored — regenerate locally
├── api/
│   ├── retriever.py        # search_embedding(query) -> top-5 chunks
│   ├── prompt_builder.py   # build_prompt(chunks, history, question)
│   ├── llm.py               # inference(prompt) -> streaming chat completion
│   └── main.py              # FastAPI app, /chat WebSocket endpoint
├── frontend/
│   └── px4-chatbot/
│       └── src/app/
│           ├── message.model.ts     # Message interface
│           ├── chat.service.ts      # WebSocket connection, signals-based state
│           ├── app.component.ts/html
│           └── chat/
│               ├── chat.component.ts
│               ├── chat.component.html
│               └── chat.component.css   # ground-control console styling
├── test_ws.py               # standalone WebSocket smoke-test script
├── .env                     # gitignored — your local secrets
├── .env.example             # template for contributors
├── .gitignore
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.13, a virtual environment
- Node.js v22+ (use `nvm install --lts` — Angular CLI requires this)
- A free HuggingFace account + API token (`huggingface.co/settings/tokens`)
- Linux or WSL — **Milvus Lite has a known file-rename bug on native Windows**, see Decisions Log

### Environment variables (`.env`)

```
hf_token=hf_xxxxxxxxxxxxxxxxxxxx
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=meta-llama/Llama-3.3-70B-Instruct
db_name=milvus_px4.db
collection_name=px4_doc_collection
```

### Steps to rebuild the pipeline from scratch

```bash
# 1. Clone PX4 docs source (outside this repo, path referenced in repo_loader.py)
git clone https://github.com/PX4/PX4-Autopilot.git

# 2. Generate output.json
python ingestion/repo_loader.py

# 3. Generate chunks.json
python ingestion/chunker.py

# 4. Embed + insert into Milvus (one API call per chunk — slow, note runtime)
python vectordb/ingest.py

# 5. Start the backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 6. Smoke test in a second terminal
python test_ws.py
```

---

## Phases

- [X] Phase 0 — environment and repo setup
- [X] Phase 1 — ingestion pipeline (`repo_loader.py`, `chunker.py`)
- [X] Phase 2 — embeddings + Milvus Lite vector store
- [X] Phase 3 — FastAPI WebSocket RAG backend (retrieval, prompt building, streaming LLM)
- [X] Phase 4 — Angular frontend (ground-control console UI, streaming, signals-based state)
- [ ] Phase 3.5 — JWT auth layer on top of the WebSocket (deliberately deferred so auth bugs don't mask RAG bugs)
- [ ] Phase 5 — open source launch polish: `CONTRIBUTING.md`, `docker-compose.yml` for one-command setup, demo GIF, first GitHub release

v1.0 is functionally complete: ask a real PX4 question, get a grounded, streamed answer in a working chat UI. Everything below this line is intentional future work, not unfinished work.

---

## Future contributions

This project is marked complete but not perfect — these are known, scoped next steps, not vague TODOs.

- **QGroundControl documentation.** Currently the knowledge base only covers PX4-user_guide. QGC is the other half of a real PX4 workflow and the chatbot is incomplete without it. Decision already made: extend the *same* Milvus collection rather than creating a second one — see Decisions Log below for the reasoning (vector search degrades gracefully with mixed sources; a second collection + re-ranking would add real complexity for no measurable benefit at this scale). Plan: clone the QGC docs repo, confirm its markdown structure is compatible with the existing `chunker.py`, tag each chunk `source: "QGroundControl-user_guide"`, run through the existing pipeline unchanged.
- **Metadata filtering at query time.** Once QGC docs are in, watch for cross-source noise in retrieval results. If it shows up, add a Milvus `filter` expression (e.g. `source == "QGroundControl-user_guide"`) scoped by detected intent — don't pre-build this speculatively.
- **JWT authentication** (Phase 3.5) — was deliberately deferred during MVP build so auth bugs wouldn't mask RAG bugs. Add `POST /token` + WebSocket handshake validation now that the core pipeline is proven.
- **WebSocket reconnect logic** on the Angular side — currently a dropped connection just shows "offline" with no auto-retry.
- **Batched embedding during ingest** — `ingest.py` currently makes one HF API call per chunk, which is slow on re-runs. Worth batching if the doc set grows (e.g. once QGC is added).
- **Distance-threshold filtering in retrieval** — currently all top-5 chunks are used regardless of relevance score; low-similarity chunks (high COSINE distance) could be dropped before prompt building.

---

## Decisions log

Keep adding to this as you go — it's the most valuable part of this README for anyone (including future you) trying to understand *why*, not just *what*.

- **Live scraping abandoned, repo-only ingestion.** `docs.px4.io` scraping was too much surface area to maintain reliably; the GitHub repo is the canonical source the site is built from anyway.
- **Heading-based chunking via manual line-walking, not a markdown library.** The raw `.md` files contain Vitepress directives (`<script setup>`, `:::warning`, `<div v-if>`) that a generic markdown parser would mishandle. A `clean()` regex pass strips these before chunking.
- **Mistral-7B-Instruct-v0.3 does not work on the free `hf-inference` provider** — as of mid-2025 that provider serves CPU inference only (embeddings, classification, small/legacy LLMs). Switched to `provider="auto"` with `meta-llama/Llama-3.3-70B-Instruct`, routed through HF's Inference Providers (e.g. SambaNova).
- **Milvus Lite breaks on native Windows** (`os.rename` `WinError 183` during flush — a Linux-assumption bug in Milvus Lite's manifest-saving code). Moved development to WSL/native Linux.
- **Conversation history is sent by the client, not stored server-side.** Keeps the backend stateless, avoids storing potentially sensitive conversations, and scales without a session store.
- **WebSocket over SSE.** Conversations are inherently bidirectional; one persistent connection per session is a more natural fit than a new HTTP request per turn.
- **`asyncio.to_thread()` wraps the synchronous `inference()` call** inside the async WebSocket handler so one slow LLM call doesn't block other connected clients.
- **Frontend visual direction: ground-control console, not chat bubbles.** PX4 pilots' actual working environment is a telemetry HUD — that's the authentic reference point, not a generic Messenger-style UI. No copyrighted PX4/QGC logos used; the drone glyph in the header is an original SVG (lines + circles).
- **Single Milvus collection for multiple doc sources (PX4 + future QGroundControl), not separate collections with re-ranking.** Vector similarity search naturally surfaces relevant chunks regardless of how many unrelated chunks coexist in the same collection — splitting into parallel collections + Reciprocal Rank Fusion would add real complexity (two round trips, a fusion algorithm to tune) for no measurable benefit at this scale. Each chunk's existing `source` field is enough to distinguish origin; Milvus `filter` expressions are available later if cross-source noise turns out to be a real problem in practice.

---

## Known issues / things to watch

- HF Inference Providers occasionally segfaults on stream completion (library-level bug in `huggingface_hub` on Linux) — happens *after* the full answer has already streamed, so it's cosmetic but worth re-checking after upgrading `huggingface_hub`.
- `ingest.py` makes one HF API call per chunk — re-embedding the full doc set is slow. Consider batching, especially once QGC docs roughly double the dataset.
- No reconnect logic if the WebSocket drops — `chat.service.ts` shows "offline" but doesn't retry. Listed under Future contributions.

---

## License

PX4 documentation content is used under PX4's own CC BY 4.0 license. Code in this repository: [choose and add a license — MIT recommended for an open-source portfolio project].