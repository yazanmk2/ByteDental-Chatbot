"""
ByteDent API Models
===================
CTO Best Practice: Strict Pydantic models for request/response validation,
ensuring type safety, automatic documentation, and clear API contracts.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


# ===========================================
# ENUMS
# ===========================================

class ResponseType(str, Enum):
    """Response type enumeration"""
    ANSWER = "answer"
    HANDOFF = "handoff"


class HealthStatus(str, Enum):
    """Health check status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


# ===========================================
# REQUEST MODELS
# ===========================================

class ChatRequest(BaseModel):
    """
    Chat request model.

    Example:
        {
            "message": "What is a CBCT scan?",
            "conversation_id": "conv_123",
            "metadata": {"source": "web"}
        }
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question or message",
        examples=["What is a CBCT scan?"]
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID for tracking",
        examples=["conv_abc123"]
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata for the request"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is a periapical abscess?",
                "conversation_id": "conv_123",
                "metadata": {"source": "web", "user_type": "dentist"}
            }
        }


# ===========================================
# RESPONSE MODELS
# ===========================================

class RetrievalInfo(BaseModel):
    """Information about the retrieval process"""
    top_similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Highest similarity score from retrieval"
    )
    chunks_retrieved: int = Field(
        ...,
        ge=0,
        description="Number of chunks retrieved"
    )
    retrieval_time_ms: float = Field(
        ...,
        ge=0,
        description="Time taken for retrieval in milliseconds"
    )


class ChatResponse(BaseModel):
    """
    Chat response model.

    Example successful response:
        {
            "type": "answer",
            "message": "A CBCT scan is...",
            "citations": ["CBCT uses cone-shaped beam..."],
            "retrieval": {...},
            "request_id": "req_123"
        }
    """
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    type: ResponseType = Field(
        ...,
        description="Response type: 'answer' or 'handoff'"
    )
    message: str = Field(
        ...,
        description="Response message to the user"
    )
    citations: List[str] = Field(
        default=[],
        description="Citations from the knowledge base"
    )
    handoff_reason: Optional[str] = Field(
        default=None,
        description="Reason for handoff (only if type='handoff')"
    )
    retrieval: Optional[RetrievalInfo] = Field(
        default=None,
        description="Retrieval process information"
    )
    request_id: str = Field(
        ...,
        description="Unique request identifier for tracking"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation ID if provided in request"
    )
    processing_time_ms: float = Field(
        ...,
        ge=0,
        description="Total processing time in milliseconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp (UTC)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "answer",
                "message": "A CBCT (Cone Beam Computed Tomography) scan is a specialized 3D dental imaging technology...",
                "citations": [
                    "CBCT is a specialized three-dimensional dental imaging technology",
                    "CBCT uses a cone-shaped X-ray beam that rotates around the patient's head"
                ],
                "handoff_reason": None,
                "retrieval": {
                    "top_similarity_score": 0.87,
                    "chunks_retrieved": 5,
                    "retrieval_time_ms": 45.2
                },
                "request_id": "req_abc123",
                "conversation_id": "conv_123",
                "processing_time_ms": 1250.5,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class HandoffPayload(BaseModel):
    """Structured payload for support handoff"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    user_question: str
    handoff_reason: str
    retrieved_context_snippets: List[str] = Field(default=[])
    similarity_scores: List[float] = Field(default=[])
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    conversation_id: Optional[str] = None
    request_id: str
    metadata: Dict[str, Any] = Field(default={})


# ===========================================
# HEALTH CHECK MODELS
# ===========================================

class ComponentHealth(BaseModel):
    """Health status of a component"""
    status: HealthStatus
    message: Optional[str] = None
    latency_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """
    Health check response.

    Used by load balancers and monitoring systems.
    """
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    status: HealthStatus = Field(
        ...,
        description="Overall health status"
    )
    version: str = Field(
        ...,
        description="API version"
    )
    environment: str = Field(
        ...,
        description="Deployment environment"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    components: Dict[str, ComponentHealth] = Field(
        default={},
        description="Individual component health status"
    )
    uptime_seconds: float = Field(
        ...,
        ge=0,
        description="Service uptime in seconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "production",
                "timestamp": "2024-01-15T10:30:00Z",
                "components": {
                    "llm_model": {"status": "healthy", "message": "Model loaded"},
                    "vector_store": {"status": "healthy", "latency_ms": 5.2},
                    "embedding_model": {"status": "healthy"}
                },
                "uptime_seconds": 3600.5
            }
        }


# ===========================================
# ERROR MODELS
# ===========================================

class ErrorDetail(BaseModel):
    """Error detail model"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(default=None, description="Field that caused the error")


class ErrorResponse(BaseModel):
    """
    Standard error response.

    CTO Note: Consistent error format across all endpoints
    for easier client-side error handling.
    """
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    error: bool = Field(default=True)
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Human-readable error message")
    details: List[ErrorDetail] = Field(default=[], description="Detailed error information")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "status_code": 400,
                "message": "Invalid request",
                "details": [
                    {
                        "code": "VALIDATION_ERROR",
                        "message": "Message cannot be empty",
                        "field": "message"
                    }
                ],
                "request_id": "req_abc123",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# ===========================================
# METRICS MODELS
# ===========================================

class MetricsResponse(BaseModel):
    """API metrics response"""
    total_requests: int = Field(default=0)
    total_answers: int = Field(default=0)
    total_handoffs: int = Field(default=0)
    average_response_time_ms: float = Field(default=0.0)
    average_similarity_score: float = Field(default=0.0)
    uptime_seconds: float = Field(default=0.0)
    model_info: Dict[str, str] = Field(default={})
