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
    """Create test client with temporary database."""
    engine = create_engine(
        f"sqlite:///{temp_db}",
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Create a db session for tests to use directly
    db = TestingSessionLocal()
    
    # Save the original override before setting our own
    original_override = app.dependency_overrides.get(get_db)
    
    def override_get_db():
        request_db = TestingSessionLocal()
        try:
            yield request_db
        finally:
            request_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client, db
    finally:
        if original_override is not None:
            app.dependency_overrides[get_db] = original_override
        else:
            app.dependency_overrides.pop(get_db, None)
        db.close()
        engine.dispose()


def test_agent_can_assign_escalated_ticket(client_with_temp_db):
    """Test that an agent can assign an escalated ticket to themselves."""
    from app.api.auth import create_access_token
    
    client, db = client_with_temp_db
    
    # Create an agent user
    agent = User(
        email="agent@test.com",
        hashed_password="hashed_password",
        role="agent"
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    # Create an escalated ticket
    ticket = Ticket(
        message="Escalated ticket",
        status="escalated",
        user_id=None
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    # Create token for agent
    token = create_access_token(data={"sub": str(agent.id), "role": "agent"})
    
    # Assign ticket
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/tickets/{ticket.id}/assign", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_agent_id"] == agent.id
    assert data["id"] == ticket.id


def test_regular_user_gets_403_when_assigning_ticket(client_with_temp_db):
    """Test that a regular user gets 403 when trying to assign a ticket."""
    from app.api.auth import create_access_token
    
    client, db = client_with_temp_db
    
    # Create a regular user
    user = User(
        email="user@test.com",
        hashed_password="hashed_password",
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create an escalated ticket
    ticket = Ticket(
        message="Escalated ticket",
        status="escalated",
        user_id=None
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    # Create token for regular user
    token = create_access_token(data={"sub": str(user.id), "role": "user"})
    
    # Try to assign ticket
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/tickets/{ticket.id}/assign", headers=headers)
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["error"]["message"]


def test_assign_auto_resolved_ticket_returns_400(client_with_temp_db):
    """Test that trying to assign an auto_resolved ticket returns 400."""
    from app.api.auth import create_access_token
    
    client, db = client_with_temp_db
    
    # Create an agent user
    agent = User(
        email="agent@test.com",
        hashed_password="hashed_password",
        role="agent"
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    # Create an auto_resolved ticket (not escalated)
    ticket = Ticket(
        message="Auto resolved ticket",
        status="auto_resolved",
        user_id=None,
        response="Auto response",
        intent="test_intent",
        confidence=0.9
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    # Create token for agent
    token = create_access_token(data={"sub": str(agent.id), "role": "agent"})
    
    # Try to assign ticket
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/tickets/{ticket.id}/assign", headers=headers)
    
    assert response.status_code == 400
    assert "Only escalated tickets can be assigned" in response.json()["error"]["message"]


def test_agent_can_close_escalated_ticket(client_with_temp_db):
    """Test that an agent can close an escalated ticket."""
    from app.api.auth import create_access_token
    
    client, db = client_with_temp_db
    
    # Create an agent user
    agent = User(
        email="agent@test.com",
        hashed_password="hashed_password",
        role="agent"
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    # Create an escalated ticket
    ticket = Ticket(
        message="Escalated ticket to close",
        status="escalated",
        user_id=None
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    # Create token for agent
    token = create_access_token(data={"sub": str(agent.id), "role": "agent"})
    
    # Close ticket
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/tickets/{ticket.id}/close", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed"
    assert data["id"] == ticket.id


def test_close_ticket_has_status_closed_in_response(client_with_temp_db):
    """Test that the closed ticket has status 'closed' in the response."""
    from app.api.auth import create_access_token
    
    client, db = client_with_temp_db
    
    # Create an admin user
    admin = User(
        email="admin@test.com",
        hashed_password="hashed_password",
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # Create an escalated ticket
    ticket = Ticket(
        message="Ticket to close",
        status="escalated",
        user_id=None
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    # Create token for admin
    token = create_access_token(data={"sub": str(admin.id), "role": "admin"})
    
    # Close ticket
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/tickets/{ticket.id}/close", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "closed"
    
    # Verify in database
    db.refresh(ticket)
    assert ticket.status == "closed"
