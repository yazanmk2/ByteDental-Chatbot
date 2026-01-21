"""
ByteDent RAG Chatbot Engine
===========================
CTO Best Practice: Clean separation of concerns with the RAG pipeline
implemented as a singleton service for efficient resource management.

Performance Optimizations Applied:
- CPU threading optimization
- Greedy decoding for faster inference
- Response caching with LRU
- Inference mode for reduced overhead
"""

import json
import time
import uuid
import os
import hashlib
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import lru_cache

import numpy as np
import faiss
import tiktoken
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

from app.config import settings
from app.logger import get_logger
from app.knowledge_base import get_knowledge_base

# ===========================================
# CPU PERFORMANCE OPTIMIZATIONS
# ===========================================
CPU_THREADS = os.cpu_count() or 4
os.environ["OMP_NUM_THREADS"] = str(CPU_THREADS)
os.environ["TOKENIZERS_PARALLELISM"] = "true"

# Path to GGUF model for fast CPU inference
GGUF_MODEL_PATH = "/opt/senior-dental-ai-chatbot/models/qwen2.5-3b-instruct-q4_k_m.gguf"


# ===========================================
# RESPONSE CACHE (LRU with TTL)
# ===========================================
class ResponseCache:
    """Simple in-memory cache for chat responses"""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.hits = 0
        self.misses = 0

    def _hash_query(self, query: str) -> str:
        """Create hash of normalized query"""
        normalized = query.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    def get(self, query: str) -> Optional[Any]:
        """Get cached response if exists and not expired"""
        key = self._hash_query(query)
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                return result
            else:
                del self.cache[key]  # Expired
        self.misses += 1
        return None

    def set(self, query: str, result: Any):
        """Cache a response"""
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache, key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

        key = self._hash_query(query)
        self.cache[key] = (result, time.time())

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2)
        }


# Global response cache instance
_response_cache = ResponseCache(max_size=100, ttl_seconds=3600)

logger = get_logger(__name__)


# ===========================================
# DATA CLASSES
# ===========================================

@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    text: str
    chunk_id: int
    source: str
    token_count: int


@dataclass
class RetrievalResult:
    """Result of retrieval operation"""
    chunks: List[Chunk]
    scores: List[float]
    max_score: float
    passed_threshold: bool
    retrieval_time_ms: float


@dataclass
class GateDecision:
    """Decision from answerability gate"""
    should_handoff: bool
    reason: str


@dataclass
class ChatResult:
    """Complete chat result"""
    type: str  # "answer" or "handoff"
    message: str
    citations: List[str]
    handoff_reason: Optional[str]
    retrieval_result: RetrievalResult
    gate_decision: GateDecision
    generation_time_ms: float
    total_time_ms: float
    request_id: str


# ===========================================
# CHUNKER
# ===========================================

class TokenAwareChunker:
    """Chunks text based on token count with overlap"""

    def __init__(self, chunk_size: int = 400, overlap: int = 80):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, text: str, source: str = "knowledge_base") -> List[Chunk]:
        """Split text into overlapping chunks based on tokens"""
        tokens = self.encoding.encode(text)
        chunks = []

        start = 0
        chunk_id = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)

            chunk_text = chunk_text.strip()
            if chunk_text:
                chunks.append(Chunk(
                    text=chunk_text,
                    chunk_id=chunk_id,
                    source=source,
                    token_count=len(chunk_tokens)
                ))
                chunk_id += 1

            start = end - self.overlap

        return chunks


# ===========================================
# VECTOR STORE
# ===========================================

class VectorStore:
    """FAISS-based vector store for semantic search"""

    def __init__(self, embedding_model_name: str):
        logger.info(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.index = None
        self.chunks: List[Chunk] = []
        logger.info(f"Embedding dimension: {self.dimension}")

    def build_index(self, chunks: List[Chunk]):
        """Build FAISS index from chunks"""
        logger.info(f"Building FAISS index for {len(chunks)} chunks")
        self.chunks = chunks

        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings.astype('float32'))

        logger.info(f"Index built with {self.index.ntotal} vectors")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """Search for relevant chunks"""
        if self.index is None:
            raise ValueError("Index not built. Call build_index first.")

        query_embedding = self.embedding_model.encode(
            [query],
            normalize_embeddings=True
        )

        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))

        return results


# ===========================================
# CHATBOT ENGINE (SINGLETON)
# ===========================================

class ByteDentChatbot:
    """
    Main chatbot engine implementing RAG pipeline.

    CTO Note: Implemented as a singleton to ensure model is loaded only once
    and shared across all requests for efficient resource utilization.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if ByteDentChatbot._initialized:
            return

        logger.info("Initializing ByteDent Chatbot Engine")
        self._start_time = time.time()

        # Initialize components
        self._init_chunker()
        self._init_vector_store()
        self._init_llm()
        self._build_knowledge_base()

        ByteDentChatbot._initialized = True
        logger.info("ByteDent Chatbot Engine initialized successfully")

    def _init_chunker(self):
        """Initialize the text chunker"""
        self.chunker = TokenAwareChunker(
            chunk_size=settings.chunk_size_tokens,
            overlap=settings.chunk_overlap_tokens
        )

    def _init_vector_store(self):
        """Initialize the vector store"""
        self.vector_store = VectorStore(settings.embedding_model)

    def _init_llm(self):
        """Initialize the LLM model using llama.cpp for fast CPU inference"""
        logger.info(f"Loading GGUF model: {GGUF_MODEL_PATH}")

        # Load model with llama.cpp - optimized for CPU
        self.model = Llama(
            model_path=GGUF_MODEL_PATH,
            n_ctx=4096,           # Context window (increased for RAG)
            n_threads=CPU_THREADS,  # Use all CPU cores
            n_batch=512,          # Batch size for prompt processing
            verbose=False         # Suppress llama.cpp logs
        )

        logger.info(f"GGUF model loaded with {CPU_THREADS} threads")
        logger.info("Model: Qwen2.5-3B-Instruct Q4_K_M (optimized for CPU)")

    def _build_knowledge_base(self):
        """Build the knowledge base index"""
        logger.info("Building knowledge base index")
        kb_content = get_knowledge_base()
        chunks = self.chunker.chunk_text(kb_content, source="dental_kb")
        self.vector_store.build_index(chunks)
        logger.info(f"Knowledge base built with {len(chunks)} chunks")

    # ===========================================
    # SYSTEM PROMPT
    # ===========================================

    SYSTEM_PROMPT = """You are a helpful support assistant for ByteDent, an AI-powered dental imaging analysis platform.

CRITICAL RULES:
1. Answer ONLY using the provided CONTEXT below
2. If CONTEXT is insufficient or missing, you MUST respond with type="handoff"
3. NEVER provide medical diagnoses, treatment recommendations, or personalized medical advice
4. NEVER guess, hallucinate, or infer information not in CONTEXT
5. ALWAYS cite specific parts of CONTEXT in your citations array
6. Keep responses professional, accurate, and educational
7. For pricing, specific patient cases, or medical advice, ALWAYS handoff
8. Remind users that ByteDent findings should be verified by a licensed dental professional

RESPONSE FORMAT (JSON only):
{{
  "type": "answer" or "handoff",
  "message": "your response to the user",
  "citations": ["relevant quote from context 1", "relevant quote from context 2"],
  "handoff_reason": "only if type=handoff, explain why"
}}

CONTEXT:
{context}

USER QUESTION:
{question}

Respond with JSON only, no other text:"""

    # ===========================================
    # CORE METHODS
    # ===========================================

    def retrieve_context(self, query: str) -> RetrievalResult:
        """Retrieve relevant context for a query"""
        start_time = time.time()

        results = self.vector_store.search(query, top_k=settings.retrieval_top_k)

        if not results:
            return RetrievalResult(
                chunks=[],
                scores=[],
                max_score=0.0,
                passed_threshold=False,
                retrieval_time_ms=(time.time() - start_time) * 1000
            )

        # Filter by threshold
        filtered_results = [
            (chunk, score) for chunk, score in results
            if score >= settings.min_similarity_threshold
        ]

        chunks = [chunk for chunk, _ in filtered_results]
        scores = [score for _, score in filtered_results]
        max_score = max(scores) if scores else 0.0

        return RetrievalResult(
            chunks=chunks,
            scores=scores,
            max_score=max_score,
            passed_threshold=len(chunks) > 0,
            retrieval_time_ms=(time.time() - start_time) * 1000
        )

    def answerability_gate(self, query: str, retrieval_result: RetrievalResult) -> GateDecision:
        """Determine if question is answerable or needs handoff"""
        query_lower = query.lower()

        # Check 1: No retrieved documents
        if not retrieval_result.chunks:
            return GateDecision(
                should_handoff=True,
                reason="No relevant information found in knowledge base"
            )

        # Check 2: Similarity score below handoff threshold
        if retrieval_result.max_score < settings.handoff_similarity_threshold:
            return GateDecision(
                should_handoff=True,
                reason=f"Low similarity score ({retrieval_result.max_score:.3f})"
            )

        # Check 3: Query contains handoff-required topics
        for topic in settings.handoff_required_topics:
            if topic in query_lower:
                return GateDecision(
                    should_handoff=True,
                    reason=f"Query requires live support: contains '{topic}'"
                )

        # Check 4: Patient-specific queries
        patient_patterns = [
            "my scan", "my x-ray", "my cbct", "my panoramic",
            "my diagnosis", "my treatment", "my tooth", "my teeth",
            "diagnose me", "analyze my", "look at my",
            "what should i do", "should i get", "do i need"
        ]

        for pattern in patient_patterns:
            if pattern in query_lower:
                return GateDecision(
                    should_handoff=True,
                    reason="Query appears to be patient-specific"
                )

        return GateDecision(
            should_handoff=False,
            reason="Query is answerable from knowledge base"
        )

    def _format_context(self, chunks: List[Chunk]) -> str:
        """Format retrieved chunks into context string"""
        if not chunks:
            return "[No relevant context found]"

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Context {i}]\n{chunk.text}")

        return "\n\n".join(context_parts)

    def _generate_response(self, prompt: str) -> str:
        """Generate text from LLM using llama.cpp for fast CPU inference"""
        # Use chat completion API for proper formatting
        messages = [{"role": "user", "content": prompt}]

        response = self.model.create_chat_completion(
            messages=messages,
            max_tokens=256,       # Cap for speed
            temperature=0.1,      # Low temperature for consistent answers
            top_p=0.9,
            stop=["```", "\n\n\n"],  # Stop tokens
        )

        return response["choices"][0]["message"]["content"].strip()

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Extract and parse JSON from model output"""
        # Handle markdown code blocks
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                text = text[json_start:json_end]

        # Find JSON object
        json_start = text.find("{")
        json_end = text.rfind("}") + 1

        if json_start == -1 or json_end <= json_start:
            raise ValueError("No JSON object found in response")

        json_str = text[json_start:json_end]
        return json.loads(json_str)

    def _check_uncertainty(self, response_text: str) -> bool:
        """Check if response contains uncertainty language"""
        text_lower = response_text.lower()
        return any(keyword in text_lower for keyword in settings.uncertainty_keywords)

    def chat(self, question: str, request_id: Optional[str] = None) -> ChatResult:
        """
        Main chat method - processes a question through the full RAG pipeline.

        Args:
            question: User's question
            request_id: Optional request ID for tracking

        Returns:
            ChatResult with response details
        """
        total_start = time.time()
        request_id = request_id or str(uuid.uuid4())

        logger.info(f"Processing chat request", extra={"request_id": request_id})

        # Check cache first for instant response
        cached = _response_cache.get(question)
        if cached is not None:
            logger.info(f"Cache hit for query", extra={"request_id": request_id})
            # Return cached result with updated request_id and timing
            cached.request_id = request_id
            cached.total_time_ms = (time.time() - total_start) * 1000
            return cached

        # Step 1: Retrieve context
        retrieval_result = self.retrieve_context(question)

        # Step 2: Answerability gate
        gate_decision = self.answerability_gate(question, retrieval_result)

        # Step 3: If gate says handoff, do it immediately
        if gate_decision.should_handoff:
            total_time = (time.time() - total_start) * 1000
            logger.info(
                f"Handoff triggered: {gate_decision.reason}",
                extra={"request_id": request_id, "duration_ms": total_time}
            )
            return ChatResult(
                type="handoff",
                message="I need to connect you with a support specialist who can better assist you with this request.",
                citations=[],
                handoff_reason=gate_decision.reason,
                retrieval_result=retrieval_result,
                gate_decision=gate_decision,
                generation_time_ms=0,
                total_time_ms=total_time,
                request_id=request_id
            )

        # Step 4: Generate response
        gen_start = time.time()
        context = self._format_context(retrieval_result.chunks)
        prompt = self.SYSTEM_PROMPT.format(context=context, question=question)
        raw_output = self._generate_response(prompt)
        generation_time = (time.time() - gen_start) * 1000

        # Step 5: Parse JSON response
        try:
            parsed = self._parse_json_response(raw_output)
        except (json.JSONDecodeError, ValueError) as e:
            total_time = (time.time() - total_start) * 1000
            logger.warning(
                f"Failed to parse model response: {e}",
                extra={"request_id": request_id}
            )
            return ChatResult(
                type="handoff",
                message="I'm having trouble processing your request. Let me connect you with support.",
                citations=[],
                handoff_reason=f"Failed to parse model response",
                retrieval_result=retrieval_result,
                gate_decision=gate_decision,
                generation_time_ms=generation_time,
                total_time_ms=total_time,
                request_id=request_id
            )

        # Step 6: Validate response
        response_type = parsed.get("type", "handoff")
        message = parsed.get("message", "")
        citations = parsed.get("citations", [])

        # Check for uncertainty
        if response_type == "answer" and self._check_uncertainty(message):
            total_time = (time.time() - total_start) * 1000
            return ChatResult(
                type="handoff",
                message="I'm not completely certain about this answer. Let me connect you with support.",
                citations=[],
                handoff_reason="Model expressed uncertainty",
                retrieval_result=retrieval_result,
                gate_decision=gate_decision,
                generation_time_ms=generation_time,
                total_time_ms=total_time,
                request_id=request_id
            )

        # Check for missing citations
        if response_type == "answer" and not citations:
            total_time = (time.time() - total_start) * 1000
            return ChatResult(
                type="handoff",
                message="I need to verify this information. Let me connect you with support.",
                citations=[],
                handoff_reason="Answer provided without citations",
                retrieval_result=retrieval_result,
                gate_decision=gate_decision,
                generation_time_ms=generation_time,
                total_time_ms=total_time,
                request_id=request_id
            )

        # Step 7: Return successful response
        total_time = (time.time() - total_start) * 1000
        logger.info(
            f"Chat completed successfully",
            extra={"request_id": request_id, "duration_ms": total_time}
        )

        result = ChatResult(
            type=response_type,
            message=message,
            citations=citations,
            handoff_reason=parsed.get("handoff_reason"),
            retrieval_result=retrieval_result,
            gate_decision=gate_decision,
            generation_time_ms=generation_time,
            total_time_ms=total_time,
            request_id=request_id
        )

        # Cache successful answers for faster repeat queries
        if response_type == "answer":
            _response_cache.set(question, result)

        return result

    def get_uptime(self) -> float:
        """Get service uptime in seconds"""
        return time.time() - self._start_time

    def is_healthy(self) -> bool:
        """Check if the chatbot is healthy"""
        try:
            # Quick health check - verify model and index are loaded
            return (
                self.model is not None and
                self.vector_store.index is not None and
                self.vector_store.index.ntotal > 0
            )
        except Exception:
            return False

    def get_model_info(self) -> str:
        """Return model info for health endpoint"""
        return "Qwen2.5-0.5B-Instruct-GGUF-Q4_K_M"


# ===========================================
# SINGLETON ACCESSOR
# ===========================================

def get_chatbot() -> ByteDentChatbot:
    """Get the chatbot singleton instance"""
    return ByteDentChatbot()
