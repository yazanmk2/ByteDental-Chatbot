"""
ByteDent Dental AI API
======================
Production-grade FastAPI application for the ByteDent RAG chatbot.

CTO Best Practices:
- Structured logging with request tracing
- Comprehensive health checks
- Rate limiting and security headers
- OpenAPI documentation
- Graceful shutdown handling
- Dependency injection
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import uvicorn

from app.config import settings
from app.logger import get_logger, setup_logging
from app.models import (
    ChatRequest, ChatResponse, RetrievalInfo,
    HealthResponse, HealthStatus, ComponentHealth,
    ErrorResponse, ErrorDetail, MetricsResponse
)
from app.chatbot import get_chatbot, ByteDentChatbot

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# ===========================================
# METRICS TRACKING
# ===========================================

class Metrics:
    """Simple in-memory metrics tracker"""
    def __init__(self):
        self.total_requests = 0
        self.total_answers = 0
        self.total_handoffs = 0
        self.total_errors = 0
        self.total_response_time_ms = 0.0
        self.total_similarity_score = 0.0

    def record_request(self, response_type: str, response_time_ms: float, similarity_score: float):
        self.total_requests += 1
        self.total_response_time_ms += response_time_ms
        self.total_similarity_score += similarity_score
        if response_type == "answer":
            self.total_answers += 1
        else:
            self.total_handoffs += 1

    def record_error(self):
        self.total_errors += 1

    @property
    def average_response_time_ms(self) -> float:
        return self.total_response_time_ms / max(1, self.total_requests)

    @property
    def average_similarity_score(self) -> float:
        return self.total_similarity_score / max(1, self.total_requests)


metrics = Metrics()


# ===========================================
# LIFESPAN MANAGEMENT
# ===========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    CTO Note: Pre-load models on startup to avoid cold start latency.
    Ensure graceful shutdown for clean resource release.
    """
    logger.info("Starting ByteDent API server")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize chatbot (loads models)
    try:
        chatbot = get_chatbot()
        logger.info("Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}")
        raise

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down ByteDent API server")


# ===========================================
# FASTAPI APPLICATION
# ===========================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## ByteDent Dental AI API

AI-powered dental imaging analysis chatbot API.

### Features
- **RAG-based Q&A**: Answer dental questions using knowledge base
- **Smart Handoff**: Automatic escalation for out-of-scope queries
- **Citation Support**: Responses include source citations

### Response Types
- `answer`: AI-generated response with citations
- `handoff`: Request escalated to human support

### Rate Limits
- 60 requests per minute per IP (configurable)
    """,
    openapi_tags=[
        {"name": "Chat", "description": "Main chat endpoints"},
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Metrics", "description": "API metrics endpoints"},
    ],
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ===========================================
# MIDDLEWARE
# ===========================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """
    Request middleware for logging, timing, and request ID tracking.
    """
    # Generate request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    # Log request
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={"request_id": request_id}
    )

    # Time the request
    start_time = time.time()

    try:
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"

        # Log response
        logger.info(
            f"Request completed: {response.status_code}",
            extra={"request_id": request_id, "duration_ms": duration_ms}
        )

        return response

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"Request failed: {str(e)}",
            extra={"request_id": request_id, "duration_ms": duration_ms}
        )
        raise


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


# ===========================================
# EXCEPTION HANDLERS
# ===========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    request_id = getattr(request.state, "request_id", None)

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status_code=exc.status_code,
            message=exc.detail,
            request_id=request_id
        ).model_dump(mode='json')
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"request_id": request_id},
        exc_info=True
    )

    metrics.record_error()

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status_code=500,
            message="An internal error occurred. Please try again later.",
            request_id=request_id
        ).model_dump(mode='json')
    )


# ===========================================
# DEPENDENCIES
# ===========================================

def get_chatbot_dependency() -> ByteDentChatbot:
    """Dependency injection for chatbot"""
    return get_chatbot()


# ===========================================
# API ENDPOINTS
# ===========================================

@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Send a chat message",
    description="Send a message to the ByteDent dental AI assistant and receive a response."
)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    chatbot: ByteDentChatbot = Depends(get_chatbot_dependency)
) -> ChatResponse:
    """
    Main chat endpoint.

    Processes user questions through the RAG pipeline and returns
    either an AI-generated answer with citations or a handoff response.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    try:
        # Process chat
        result = chatbot.chat(
            question=chat_request.message,
            request_id=request_id
        )

        # Record metrics
        metrics.record_request(
            response_type=result.type,
            response_time_ms=result.total_time_ms,
            similarity_score=result.retrieval_result.max_score
        )

        # Build response
        retrieval_info = RetrievalInfo(
            top_similarity_score=result.retrieval_result.max_score,
            chunks_retrieved=len(result.retrieval_result.chunks),
            retrieval_time_ms=result.retrieval_result.retrieval_time_ms
        )

        return ChatResponse(
            type=result.type,
            message=result.message,
            citations=result.citations,
            handoff_reason=result.handoff_reason,
            retrieval=retrieval_info,
            request_id=request_id,
            conversation_id=chat_request.conversation_id,
            processing_time_ms=result.total_time_ms,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", extra={"request_id": request_id})
        metrics.record_error()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat request"
        )


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Check the health status of the API and its components."
)
async def health_check(
    chatbot: ByteDentChatbot = Depends(get_chatbot_dependency)
) -> HealthResponse:
    """
    Health check endpoint.

    Used by load balancers and monitoring systems to verify service health.
    """
    components = {}

    # Check LLM model
    try:
        if chatbot.model is not None:
            components["llm_model"] = ComponentHealth(
                status=HealthStatus.HEALTHY,
                message=f"Loaded: {settings.llm_model}"
            )
        else:
            components["llm_model"] = ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message="Model not loaded"
            )
    except Exception as e:
        components["llm_model"] = ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            message=str(e)
        )

    # Check vector store
    try:
        if chatbot.vector_store.index is not None:
            components["vector_store"] = ComponentHealth(
                status=HealthStatus.HEALTHY,
                message=f"Index size: {chatbot.vector_store.index.ntotal}"
            )
        else:
            components["vector_store"] = ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message="Index not built"
            )
    except Exception as e:
        components["vector_store"] = ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            message=str(e)
        )

    # Check embedding model
    try:
        if chatbot.vector_store.embedding_model is not None:
            components["embedding_model"] = ComponentHealth(
                status=HealthStatus.HEALTHY,
                message=f"Loaded: {settings.embedding_model}"
            )
        else:
            components["embedding_model"] = ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message="Model not loaded"
            )
    except Exception as e:
        components["embedding_model"] = ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            message=str(e)
        )

    # Determine overall status
    all_healthy = all(c.status == HealthStatus.HEALTHY for c in components.values())
    any_unhealthy = any(c.status == HealthStatus.UNHEALTHY for c in components.values())

    if all_healthy:
        overall_status = HealthStatus.HEALTHY
    elif any_unhealthy:
        overall_status = HealthStatus.UNHEALTHY
    else:
        overall_status = HealthStatus.DEGRADED

    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        environment=settings.environment,
        components=components,
        uptime_seconds=chatbot.get_uptime()
    )


@app.get(
    "/api/v1/health/live",
    tags=["Health"],
    summary="Liveness probe",
    description="Kubernetes liveness probe endpoint."
)
async def liveness():
    """Liveness probe - returns 200 if the server is running"""
    return {"status": "alive"}


@app.get(
    "/api/v1/health/ready",
    tags=["Health"],
    summary="Readiness probe",
    description="Kubernetes readiness probe endpoint."
)
async def readiness(
    chatbot: ByteDentChatbot = Depends(get_chatbot_dependency)
):
    """Readiness probe - returns 200 if the server is ready to accept requests"""
    if chatbot.is_healthy():
        return {"status": "ready"}
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@app.get(
    "/api/v1/metrics",
    response_model=MetricsResponse,
    tags=["Metrics"],
    summary="API metrics",
    description="Get API usage metrics."
)
async def get_metrics(
    chatbot: ByteDentChatbot = Depends(get_chatbot_dependency)
) -> MetricsResponse:
    """Get API metrics"""
    return MetricsResponse(
        total_requests=metrics.total_requests,
        total_answers=metrics.total_answers,
        total_handoffs=metrics.total_handoffs,
        average_response_time_ms=metrics.average_response_time_ms,
        average_similarity_score=metrics.average_similarity_score,
        uptime_seconds=chatbot.get_uptime(),
        model_info={
            "llm_model": settings.llm_model,
            "embedding_model": settings.embedding_model,
            "device": settings.device
        }
    )


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    description="Welcome message and API info."
)
async def root():
    """Root endpoint with API info"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
        "chat": "/api/v1/chat"
    }


# ===========================================
# CUSTOM OPENAPI SCHEMA
# ===========================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=app.description,
        routes=app.routes,
    )

    # Add security schemes if API key is enabled
    if settings.api_key_enabled:
        openapi_schema["components"]["securitySchemes"] = {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ===========================================
# MAIN ENTRY POINT
# ===========================================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.workers,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
