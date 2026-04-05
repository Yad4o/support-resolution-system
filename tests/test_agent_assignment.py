"""
Tests for agent assignment and ticket close endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db, Base
from app.models.ticket import Ticket
from app.models.user import User


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database file."""
    import tempfile
    import os
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture(scope="function")
def client_with_temp_db(temp_db):
    """Create test client with temporary database using shared session."""
    engine = create_engine(
        f"sqlite:///{temp_db}",
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Single shared session for both test and requests
    shared_db = TestingSessionLocal()
    original_override = app.dependency_overrides.get(get_db)
    
    def override_get_db():
        try:
            yield shared_db
        finally:
            pass  # Don't close here - test manages lifecycle
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client, shared_db
    finally:
        if original_override is not None:
            app.dependency_overrides[get_db] = original_override
        else:
            app.dependency_overrides.pop(get_db, None)
        shared_db.close()
        engine.dispose()


def user_factory(db, email, role="agent", password="hashed_password"):
    """Create and return a User."""
    user = User(email=email, hashed_password=password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def ticket_factory(db, message, status, user_id=None, **kwargs):
    """Create and return a Ticket."""
    ticket = Ticket(message=message, status=status, user_id=user_id, **kwargs)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def auth_headers_for(user):
    """Create and return Authorization header for a user."""
    from app.api.auth import create_access_token
    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def test_agent_can_assign_escalated_ticket(client_with_temp_db):
    """Test that an agent can assign an escalated ticket to themselves."""
    client, db = client_with_temp_db
    
    agent = user_factory(db, "agent@test.com", role="agent")
    ticket = ticket_factory(db, "Escalated ticket", "escalated")
    
    headers = auth_headers_for(agent)
    response = client.post(f"/tickets/{ticket.id}/assign", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_agent_id"] == agent.id
    assert data["id"] == ticket.id


def test_regular_user_gets_403_when_assigning_ticket(client_with_temp_db):
    """Test that a regular user gets 403 when trying to assign a ticket."""
    client, db = client_with_temp_db
    
    user = user_factory(db, "user@test.com", role="user")
    ticket = ticket_factory(db, "Escalated ticket", "escalated")
    
    headers = auth_headers_for(user)
    response = client.post(f"/tickets/{ticket.id}/assign", headers=headers)
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["error"]["message"]


def test_assign_auto_resolved_ticket_returns_409(client_with_temp_db):
    """Test that trying to assign an auto_resolved ticket returns 409 (conflict)."""
    client, db = client_with_temp_db
    
    agent = user_factory(db, "agent@test.com", role="agent")
    ticket = ticket_factory(
        db, "Auto resolved ticket", "auto_resolved",
        response="Auto response", intent="test_intent", confidence=0.9
    )
    
    headers = auth_headers_for(agent)
    response = client.post(f"/tickets/{ticket.id}/assign", headers=headers)
    
    assert response.status_code == 409
    assert "cannot assign" in response.json()["error"]["message"]


def test_agent_can_close_escalated_ticket(client_with_temp_db):
    """Test that an agent can close an escalated ticket."""
    client, db = client_with_temp_db
    
    agent = user_factory(db, "agent@test.com", role="agent")
    ticket = ticket_factory(db, "Escalated ticket to close", "escalated")
    
    headers = auth_headers_for(agent)
    response = client.post(f"/tickets/{ticket.id}/close", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed"
    assert data["id"] == ticket.id


def test_close_ticket_has_status_closed_in_response(client_with_temp_db):
    """Test that the closed ticket has status 'closed' in the response."""
    client, db = client_with_temp_db
    
    admin = user_factory(db, "admin@test.com", role="admin")
    ticket = ticket_factory(db, "Ticket to close", "escalated")
    
    headers = auth_headers_for(admin)
    response = client.post(f"/tickets/{ticket.id}/close", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed"
    
    db.refresh(ticket)
    assert ticket.status == "closed"
