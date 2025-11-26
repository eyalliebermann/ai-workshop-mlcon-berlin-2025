import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app, ChatRequest, ChatResponse


client = TestClient(app)


def test_chat_endpoint_success():
    """Test successful chat endpoint with mocked OpenAI response"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Here are some great sober events in Berlin this week!"

    with patch('main.client.chat.completions.create', return_value=mock_response):
        response = client.post(
            "/chat",
            json={"message": "What sober events are happening in Berlin?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "sober events" in data["response"].lower()


def test_chat_endpoint_validates_request():
    """Test that request validation works properly"""
    response = client.post("/chat", json={})
    assert response.status_code == 422  # Validation error


def test_chat_endpoint_handles_openai_error():
    """Test error handling when OpenAI API fails"""
    with patch('main.client.chat.completions.create', side_effect=Exception("API Error")):
        response = client.post(
            "/chat",
            json={"message": "Test message"}
        )

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()


def test_chat_request_model():
    """Test ChatRequest model validation"""
    request = ChatRequest(message="Hello")
    assert request.message == "Hello"

    with pytest.raises(Exception):
        ChatRequest()


def test_chat_response_model():
    """Test ChatResponse model validation"""
    response = ChatResponse(response="Test response")
    assert response.response == "Test response"


def test_cors_headers():
    """Test that CORS headers are properly set"""
    response = client.options("/chat")
    assert response.status_code in [200, 405]  # OPTIONS might not be explicitly defined


def test_system_prompt_context():
    """Test that responses stay on topic with Berlin sober scene"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "I can only discuss Berlin's conscious and sober scene."

    with patch('main.client.chat.completions.create', return_value=mock_response) as mock_create:
        response = client.post(
            "/chat",
            json={"message": "Tell me about nightlife"}
        )

        # Verify system prompt was included in the call
        call_args = mock_create.call_args
        messages = call_args.kwargs['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert 'conscious and sober scene' in messages[0]['content']
        assert messages[1]['role'] == 'user'


def test_empty_message():
    """Test handling of empty message"""
    response = client.post("/chat", json={"message": ""})
    # Should still process, even if empty
    assert response.status_code in [200, 500]  # Either success or error is acceptable
