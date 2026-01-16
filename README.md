# Senior Dental AI Chatbot

A production-ready dental FAQ chatbot using RAG (Retrieval-Augmented Generation) with Qwen 2.5-3B-Instruct and FAISS.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                        │
│                    (localhost:8001)                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   API Layer  │───▶│  RAG Engine  │───▶│  Response │ │
│  │   /api/v1/*  │    │  (Chatbot)   │    │  Builder  │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│         │                   │                           │
│         │                   ▼                           │
│         │          ┌──────────────────┐                │
│         │          │   FAISS Index    │                │
│         │          │  (Vector Store)  │                │
│         │          └────────┬─────────┘                │
│         │                   │                           │
│         │                   ▼                           │
│         │          ┌──────────────────┐                │
│         │          │  Knowledge Base  │                │
│         │          │  (Dental FAQs)   │                │
│         │          └──────────────────┘                │
│         │                                               │
│         ▼                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │                Qwen 2.5-3B-Instruct              │  │
│  │                  (LLM Generation)                 │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Features

- **RAG Pipeline**: Semantic search with FAISS + LLM generation
- **Handoff Detection**: Automatically routes complex queries to human support
- **Structured Logging**: JSON logging with request tracing
- **Health Checks**: Kubernetes-ready health endpoints
- **Rate Limiting**: Built-in request throttling
- **94.3% Accuracy**: Evaluated on 53 test cases

## Requirements

- Python 3.11+
- 8GB+ RAM (for model loading)
- CUDA (optional, for GPU acceleration)

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-org/senior-dental-ai-chatbot.git
cd senior-dental-ai-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run development server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Production Deployment (systemd)

```bash
# Run deployment script
sudo ./scripts/deploy.sh
```

## API Endpoints

### Chat

```
POST /api/v1/chat
Content-Type: application/json

{
  "message": "What is ByteDent?",
  "conversation_id": "optional-uuid"
}
```

**Response:**
```json
{
  "type": "answer",
  "message": "ByteDent is a dental AI platform...",
  "citations": ["ByteDent provides AI-powered dental analysis..."],
  "handoff_reason": null,
  "retrieval": {
    "top_similarity_score": 0.85,
    "chunks_retrieved": 5,
    "retrieval_time_ms": 15.2
  },
  "request_id": "req_abc123",
  "processing_time_ms": 1250.5,
  "timestamp": "2026-01-16T10:30:00Z"
}
```

### Health Checks

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/health` | Full component health check |
| `GET /api/v1/health/live` | Kubernetes liveness probe |
| `GET /api/v1/health/ready` | Kubernetes readiness probe |
| `GET /api/v1/metrics` | API metrics and statistics |

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Server bind address |
| `API_PORT` | `8001` | Server port |
| `ENVIRONMENT` | `production` | Environment name |
| `LOG_LEVEL` | `INFO` | Logging level |
| `BYTEDENT_LLM_MODEL` | `Qwen/Qwen2.5-3B-Instruct` | LLM model |
| `BYTEDENT_EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Embedding model |
| `RETRIEVAL_TOP_K` | `5` | Number of chunks to retrieve |
| `HANDOFF_SIMILARITY_THRESHOLD` | `0.30` | Handoff trigger threshold |

## Project Structure

```
senior-dental-ai-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings management
│   ├── chatbot.py           # RAG engine
│   ├── knowledge_base.py    # Dental knowledge
│   ├── models.py            # Pydantic models
│   └── logger.py            # Structured logging
├── tests/
│   ├── __init__.py
│   ├── test_chatbot.py
│   └── test_api.py
├── scripts/
│   └── deploy.sh            # Deployment script
├── .github/
│   └── workflows/
│       ├── ci.yml           # CI pipeline
│       └── cd.yml           # CD pipeline
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Handoff Logic

The chatbot triggers handoff to human support in these cases:

1. **Low Similarity Score**: Query doesn't match knowledge base (score < 0.30)
2. **Pricing Questions**: Cost, subscription, quote requests
3. **Patient-Specific**: "My scan", "my diagnosis", personal health queries
4. **Out of Scope**: Legal, insurance, medication questions
5. **Missing Citations**: Model can't cite specific knowledge base content
6. **Uncertainty Detected**: Model expresses uncertainty in response

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Lint with ruff
ruff check app/
```

## Deployment

### systemd Service

The application runs as a systemd service for production:

```bash
# Check service status
sudo systemctl status chatbot

# View logs
sudo journalctl -u chatbot -f

# Restart service
sudo systemctl restart chatbot
```

### CI/CD

- **CI**: Runs on pull requests (lint, test)
- **CD**: Deploys on merge to main (pull, install, restart)

## Integration with Laravel Backend

This service is called by the Laravel backend's `ChatService`:

```php
$response = Http::timeout(60)
    ->post('http://localhost:8001/api/v1/chat', [
        'message' => $message,
        'conversation_id' => $conversationId,
    ]);
```

The chatbot binds to `localhost:8001` only and is not exposed to the internet.

## License

Proprietary - Senior Dental Project

## Support

For issues, contact the development team.
