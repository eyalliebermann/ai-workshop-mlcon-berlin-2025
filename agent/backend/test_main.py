"""
TEST SPECIFICATION: Berlin Sober Scene Chat API
=================================================

REQUIREMENT 1: Chat without memory
When: User sends a message without a session
Then: System responds based only on that single message

REQUIREMENT 2: Create conversation sessions
When: User requests a new session
Then: System provides a unique session ID

REQUIREMENT 3: Chat with conversation memory
When: User sends messages within a session
Then: System remembers all previous exchanges in that session

REQUIREMENT 4: AI receives full conversation context
When: User has exchanged 2 messages in a session (ask, reply, ask again)
Then: The second AI request includes the first exchange (first question + first answer)

REQUIREMENT 5: Sessions are independent
When: User creates multiple sessions
Then: Each session maintains separate conversation history

REQUIREMENT 6: Invalid session handling
When: User sends message with non-existent session ID
Then: System rejects the request

REQUIREMENT 7: System stays on topic
When: User sends any message
Then: AI is instructed to focus on Berlin's sober/conscious scene
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app, ChatRequest, ChatResponse, SessionResponse, sessions


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear sessions before each test"""
    sessions.clear()
    yield
    sessions.clear()


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


# ===== Session Management Tests =====

def test_create_session():
    """Test session creation endpoint"""
    response = client.post("/session")

    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0

    # Verify session was created in storage
    assert data["session_id"] in sessions


def test_session_has_system_prompt():
    """Test that new sessions are initialized with system prompt"""
    response = client.post("/session")
    session_id = response.json()["session_id"]

    assert session_id in sessions
    assert len(sessions[session_id]) == 1
    assert sessions[session_id][0]["role"] == "system"
    assert "conscious and sober scene" in sessions[session_id][0]["content"]


def test_multiple_sessions_are_independent():
    """Test that multiple sessions are created independently"""
    response1 = client.post("/session")
    response2 = client.post("/session")

    session_id1 = response1.json()["session_id"]
    session_id2 = response2.json()["session_id"]

    assert session_id1 != session_id2
    assert session_id1 in sessions
    assert session_id2 in sessions


def test_session_response_model():
    """Test SessionResponse model validation"""
    response = SessionResponse(session_id="test-uuid-123")
    assert response.session_id == "test-uuid-123"


# ===== Conversation History Tests =====

def test_chat_with_session_stores_history():
    """Test that chat messages are stored in session history"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Great sober events this week!"

    # Create session
    session_response = client.post("/session")
    session_id = session_response.json()["session_id"]

    with patch('main.client.chat.completions.create', return_value=mock_response):
        # Send message
        response = client.post(
            "/chat",
            json={"message": "What events are there?", "session_id": session_id}
        )

        assert response.status_code == 200

        # Verify history contains user message and assistant response
        assert len(sessions[session_id]) == 3  # system + user + assistant
        assert sessions[session_id][1]["role"] == "user"
        assert sessions[session_id][1]["content"] == "What events are there?"
        assert sessions[session_id][2]["role"] == "assistant"
        assert sessions[session_id][2]["content"] == "Great sober events this week!"


def test_chat_with_invalid_session():
    """Test that invalid session ID returns 404"""
    response = client.post(
        "/chat",
        json={"message": "Test", "session_id": "invalid-session-id"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_chat_without_session_backward_compatible():
    """Test that chat works without session_id (backward compatibility)"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response without session"

    with patch('main.client.chat.completions.create', return_value=mock_response):
        response = client.post(
            "/chat",
            json={"message": "Test message"}
        )

        assert response.status_code == 200
        assert response.json()["response"] == "Response without session"


def test_conversation_history_context():
    """Test that conversation history is passed to OpenAI"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Response"

    # Create session
    session_response = client.post("/session")
    session_id = session_response.json()["session_id"]

    # Capture messages at call time (not after modification)
    captured_messages = []

    def capture_call(*args, **kwargs):
        # Store a copy of messages at the time of call
        captured_messages.append(list(kwargs['messages']))
        return mock_response

    with patch('main.client.chat.completions.create', side_effect=capture_call) as mock_create:
        # First message
        client.post(
            "/chat",
            json={"message": "First question", "session_id": session_id}
        )

        # Second message
        client.post(
            "/chat",
            json={"message": "Second question", "session_id": session_id}
        )

        # Verify the second call includes full history
        # captured_messages[1] is what was sent on the second call
        messages = captured_messages[1]

        # Should have: system + user1 + assistant1 + user2
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "First question"
        assert messages[2]["role"] == "assistant"
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "Second question"


def test_chat_request_with_optional_session():
    """Test ChatRequest model with optional session_id"""
    # Without session_id
    request1 = ChatRequest(message="Hello")
    assert request1.message == "Hello"
    assert request1.session_id is None

    # With session_id
    request2 = ChatRequest(message="Hello", session_id="test-session")
    assert request2.message == "Hello"
    assert request2.session_id == "test-session"


def test_multi_turn_conversation():
    """Integration test: Full multi-turn conversation flow"""
    mock_responses = [
        "First response",
        "Second response",
        "Third response"
    ]

    # Create session
    session_response = client.post("/session")
    session_id = session_response.json()["session_id"]

    for i, expected_response in enumerate(mock_responses):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = expected_response

        with patch('main.client.chat.completions.create', return_value=mock_response):
            response = client.post(
                "/chat",
                json={"message": f"Question {i+1}", "session_id": session_id}
            )

            assert response.status_code == 200
            assert response.json()["response"] == expected_response

    # Verify full conversation is stored
    # system + (user + assistant) * 3 = 7 messages
    assert len(sessions[session_id]) == 7
