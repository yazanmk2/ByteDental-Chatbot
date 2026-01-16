"""
API endpoint tests for Senior Dental AI Chatbot.

These tests verify the API endpoints work correctly without loading the full LLM model.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_chatbot():
    """Mock the chatbot singleton to avoid loading the LLM."""
    with patch('app.main.ByteDentChatbot') as mock:
        mock_instance = MagicMock()
        mock_instance.is_ready.return_value = True
        mock_instance.get_uptime.return_value = 100.0
        mock_instance.chat.return_value = {
            'type': 'answer',
            'message': 'ByteDent is a dental AI platform.',
            'citations': ['ByteDent provides AI-powered dental analysis.'],
            'handoff_reason': None,
            'retrieval': {
                'top_similarity_score': 0.85,
                'chunks_retrieved': 3,
                'retrieval_time_ms': 15.0
            }
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def client(mock_chatbot):
    """Create test client with mocked chatbot."""
    from app.main import app
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self, client):
        """Test the root welcome endpoint."""
        response = client.get('/')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'online'
        assert 'version' in data

    def test_health_live(self, client):
        """Test liveness probe endpoint."""
        response = client.get('/api/v1/health/live')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'alive'

    def test_health_ready(self, client, mock_chatbot):
        """Test readiness probe endpoint."""
        mock_chatbot.is_ready.return_value = True
        response = client.get('/api/v1/health/ready')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ready'

    def test_health_ready_not_ready(self, client, mock_chatbot):
        """Test readiness probe when not ready."""
        mock_chatbot.is_ready.return_value = False
        response = client.get('/api/v1/health/ready')
        assert response.status_code == 503
        data = response.json()
        assert data['status'] == 'not_ready'


class TestChatEndpoint:
    """Test chat endpoint."""

    def test_chat_success(self, client, mock_chatbot):
        """Test successful chat request."""
        response = client.post(
            '/api/v1/chat',
            json={'message': 'What is ByteDent?'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['type'] == 'answer'
        assert 'message' in data
        assert 'citations' in data
        assert 'request_id' in data

    def test_chat_with_conversation_id(self, client, mock_chatbot):
        """Test chat with conversation tracking."""
        response = client.post(
            '/api/v1/chat',
            json={
                'message': 'Tell me about dental imaging',
                'conversation_id': 'conv-123'
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data['conversation_id'] == 'conv-123'

    def test_chat_empty_message(self, client):
        """Test chat with empty message."""
        response = client.post(
            '/api/v1/chat',
            json={'message': ''}
        )
        assert response.status_code == 422

    def test_chat_missing_message(self, client):
        """Test chat without message field."""
        response = client.post(
            '/api/v1/chat',
            json={}
        )
        assert response.status_code == 422

    def test_chat_message_too_long(self, client):
        """Test chat with message exceeding max length."""
        response = client.post(
            '/api/v1/chat',
            json={'message': 'x' * 2001}
        )
        assert response.status_code == 422

    def test_chat_handoff_response(self, client, mock_chatbot):
        """Test chat returning handoff."""
        mock_chatbot.chat.return_value = {
            'type': 'handoff',
            'message': 'I need to connect you with a specialist.',
            'citations': [],
            'handoff_reason': 'pricing_question',
            'retrieval': {
                'top_similarity_score': 0.75,
                'chunks_retrieved': 2,
                'retrieval_time_ms': 10.0
            }
        }
        response = client.post(
            '/api/v1/chat',
            json={'message': 'How much does ByteDent cost?'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['type'] == 'handoff'
        assert data['handoff_reason'] == 'pricing_question'


class TestMetricsEndpoint:
    """Test metrics endpoint."""

    def test_metrics(self, client):
        """Test metrics endpoint returns statistics."""
        response = client.get('/api/v1/metrics')
        assert response.status_code == 200
        data = response.json()
        assert 'total_requests' in data
        assert 'total_answers' in data
        assert 'total_handoffs' in data


class TestRequestHeaders:
    """Test request/response headers."""

    def test_request_id_generated(self, client, mock_chatbot):
        """Test that request ID is generated if not provided."""
        response = client.post(
            '/api/v1/chat',
            json={'message': 'Hello'}
        )
        assert 'X-Request-ID' in response.headers

    def test_request_id_passed_through(self, client, mock_chatbot):
        """Test that provided request ID is used."""
        response = client.post(
            '/api/v1/chat',
            json={'message': 'Hello'},
            headers={'X-Request-ID': 'custom-123'}
        )
        # The request ID should be in the response
        data = response.json()
        assert 'request_id' in data


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            '/api/v1/chat',
            content='not json',
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 422

    def test_chatbot_error(self, client, mock_chatbot):
        """Test handling of chatbot errors."""
        mock_chatbot.chat.side_effect = Exception('Model error')
        response = client.post(
            '/api/v1/chat',
            json={'message': 'Hello'}
        )
        assert response.status_code == 500
        data = response.json()
        assert 'error' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
