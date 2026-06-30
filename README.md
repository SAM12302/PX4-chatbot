
# PX4 RAG Chatbot

An open-source Retrieval-Augmented Generation chatbot for the PX4 Autopilot documentation. Built as a portfolio project to demonstrate RAG pipeline design and full-stack chatbot development, and as a contribution to the PX4 open-source community.

Ask natural-language questions about PX4 flight modes, configuration, parameters, and development — get answers grounded in the actual PX4 user guide, with streaming responses over WebSocket.

---

## Status

**Backend: working end to end.** **Frontend: in progress (Angular scaffolded, not yet wired up).**

If you're picking this back up after a break, start at [Where I left off](#where-i-left-off).

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
  Angular frontend (chat UI) -- NOT YET CONNECTED
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
│   └── px4-chatbot/         # ng new scaffold — components not yet built
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

## Where I left off

You were about to build the Angular `ChatComponent`, `MessageComponent`, and `InputComponent`, and a WebSocket service to connect to `/chat`. Two open questions were on the table when you paused — answer these before writing code:

1. **Where does the WebSocket connection live?** A shared `Service`, not inside a component directly — so multiple components can use it without duplicating connection logic.
2. **What does the `Message` interface look like?**
   ```typescript
   interface Message {
       role: 'user' | 'assistant';
       content: string;
   }
   ```

**Next concrete step:** create `chat.service.ts`, decide between native `WebSocket` API or `rxjs/webSocket`, and implement a `connect()` + `sendMessage()` + an observable/callback for incoming tokens.

The message protocol your backend already speaks:

```json
// client sends
{"question": "...", "history": [{"role": "user", "content": "..."}, ...]}

// server sends, one per token
{"type": "token", "content": "..."}
// then once, at the end
{"type": "done"}
// or, on failure
{"type": "error", "content": "..."}
```

---

## Remaining phases

- [X] Phase 0 — environment and repo setup
- [X] Phase 1 — ingestion pipeline (`repo_loader.py`, `chunker.py`)
- [X] Phase 2 — embeddings + Milvus Lite vector store
- [X] Phase 3 — FastAPI WebSocket RAG backend (retrieval, prompt building, streaming LLM)
- [ ] Phase 3.5 — JWT auth layer on top of the WebSocket (deliberately deferred so auth bugs don't mask RAG bugs)
- [ ] Phase 4 — Angular frontend (in progress)
- [ ] Phase 5 — open source launch: polish README, add `CONTRIBUTING.md`, `docker-compose.yml` for one-command setup, demo GIF, first GitHub release

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

---

## Known issues / things to watch

- HF Inference Providers occasionally segfaults on stream completion (library-level bug in `huggingface_hub` on Linux) — happens *after* the full answer has already streamed, so it's cosmetic but worth re-checking after upgrading `huggingface_hub`.
- `ingest.py` makes one HF API call per chunk — re-embedding the full doc set is slow. Consider batching or caching if you re-run it often during development.
- No retry/reconnect logic yet on the Angular side (doesn't exist yet — build it in from the start when you write `chat.service.ts`).

---

## License

PX4 documentation content is used under PX4's own CC BY 4.0 license. Code in this repository: [choose and add a license — MIT recommended for an open-source portfolio project].

