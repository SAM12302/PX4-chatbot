# Contributing to PX4 RAG Chatbot

Thank you for your interest in contributing! This document outlines the process and guidelines for contributing to this project.

## Getting Started

### Prerequisites

- Python 3.13+
- Node.js v22+ (use `nvm install --lts`)
- A free HuggingFace account + API token ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens))
- Linux or WSL (Milvus Lite has a known bug on native Windows — see README)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/PX4-chatbot.git
   cd PX4-chatbot
   ```

2. **Set up Python environment**
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # See existing imports in api/main.py and related files
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your HuggingFace API token
   export $(cat .env | grep -v '^#')
   ```

4. **Set up the vector database** (one-time, takes ~10-15 minutes)
   ```bash
   # Clone PX4 docs outside this repo
   cd ..
   git clone https://github.com/PX4/PX4-Autopilot.git
   cd PX4-chatbot
   
   # Run the ingestion pipeline
   python ingestion/repo_loader.py
   python ingestion/chunker.py
   python vectordb/ingest.py
   ```

5. **Start the backend**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **In a separate terminal, start the frontend**
   ```bash
   cd frontend
   npm install  # one-time
   ng serve --open
   ```

7. **Test the full stack**
   ```bash
   # Backend should be running on http://localhost:8000
   # Frontend should open on http://localhost:4200
   # Ask a question about PX4 to test the end-to-end flow
   ```

## Development Guidelines

### Code Style

- **Python:** Follow [PEP 8](https://pep8.org/). No comments for obvious code; add a comment only when the *why* is non-obvious.
- **TypeScript/Angular:** Use strong typing; no `any` types. Follow Angular style guide conventions.
- **Commit messages:** Be specific about *why* a change was made, not just *what*. Reference relevant issues.

### Testing

- **Backend:** Add tests in `api/test/` for critical paths (retrieval, prompt building, LLM inference).
- **Frontend:** Test in the browser first; Angular's CLI runs tests but UI correctness must be verified by hand.
- **WebSocket:** Use `test_ws.py` to smoke-test the backend alone (requires backend running on port 8000).

### Adding Features

This is an MVP, deliberately scoped. Before adding a new feature:

1. **Check Future Contributions** in README.md — does it align with the roadmap?
2. **File an issue** describing the feature and why it's needed.
3. **Keep scope tight.** Don't refactor surrounding code or add abstractions beyond what's immediately needed.
4. **Don't break existing functionality.** Test the full pipeline before opening a PR.

### Known Constraints

- **No session storage.** History is sent by the client on each request — by design for privacy and statelessness.
- **One Milvus collection.** Multiple doc sources (PX4, QGroundControl) coexist in the same collection; cross-source noise is managed by relevance score, not splitting.
- **Streaming over WebSocket.** Don't change this to HTTP polling without strong justification.
- **JWT auth is optional during development.** Set `JWT_ENABLED=true` in `.env` to enforce it; default is permissive.

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and test locally**
   - Run the full pipeline end-to-end
   - Verify no regressions in existing functionality
   - Add tests if applicable

3. **Commit with clear messages**
   ```bash
   git commit -m "Add JWT auth layer to WebSocket endpoint

   Adds POST /token for issuing JWTs, WebSocket token validation optional via JWT_ENABLED env var. Backward compatible — connections work with or without auth during development."
   ```

4. **Push and open a PR**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **PR description should include**
   - What problem does this solve?
   - What's the design approach?
   - How was it tested?
   - Any known limitations or follow-ups?

## Contribution Areas

### High-Priority (Roadmap)

- **QGroundControl documentation integration:** Extend the pipeline to ingest QGC docs alongside PX4. See README for design notes.
- **Metadata filtering:** Add Milvus `filter` expressions once cross-source noise appears.
- **WebSocket reconnect logic:** Auto-retry with exponential backoff on the frontend (started in `chat.service.ts`).

### Lower-Priority but Welcome

- Better error messages in the UI
- Unit tests for the ingestion pipeline
- Performance: batch embeddings, implement caching
- Accessibility: ARIA labels, keyboard navigation in the chat UI

## Reporting Bugs

1. **Check existing issues** — your bug may already be known.
2. **Create an issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs. actual behavior
   - Environment (OS, Node version, Python version, browser)
3. **If it's a security issue**, email the maintainer privately rather than posting publicly.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project. PX4 documentation is used under CC BY 4.0; code is MIT-licensed (or as specified in LICENSE).

## Questions?

Open an issue with the `question` label or start a discussion. The maintainer(s) will get back to you as soon as possible.

Thank you for contributing! 🚀
