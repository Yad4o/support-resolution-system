import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import get_db, Base
from app.main import app
from app.models.ticket import Ticket
from app.models.feedback import Feedback


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_feedback.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Create test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        # Clean up override after test
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def db_session():
    """Create test database session."""
    # Import models to ensure they're registered with Base
    from app.models.feedback import Feedback
    from app.models.ticket import Ticket
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


class TestFeedbackAPI:
    """Test cases for Feedback API endpoints."""

    def test_create_feedback_success(self, client, db_session):
        """Test successful feedback creation."""
        # Create a ticket first
        ticket = Ticket(
            message="Test ticket for feedback",
            intent="login_issue",
            confidence=0.9,
            status="auto_resolved",
            response="Test response"
        )
        db_session.add(ticket)
        db_session.commit()
        db_session.refresh(ticket)
        
        # Create feedback for the ticket
        feedback_data = {
            "ticket_id": ticket.id,
            "rating": 5,
            "resolved": True
        }
        
        response = client.post("/feedback/", json=feedback_data)
        
        assert response.status_code == 201
        feedback_response = response.json()
        
        assert feedback_response["ticket_id"] == ticket.id
        assert feedback_response["rating"] == 5
        assert feedback_response["resolved"] is True
        assert "id" in feedback_response
        assert "created_at" in feedback_response

    def test_create_feedback_ticket_not_found(self, client, db_session):
        """Test feedback creation with non-existent ticket."""
        feedback_data = {
            "ticket_id": 99999,
            "rating": 3,
            "resolved": False
        }
        
        response = client.post("/feedback/", json=feedback_data)
        
        assert response.status_code == 404
        error_detail = response.json()
        assert "not found" in error_detail["detail"].lower()

    def test_create_feedback_invalid_rating(self, client, db_session):
        """Test feedback creation with invalid rating."""
        # Create a ticket first
        ticket = Ticket(
            message="Test ticket",
            intent="general",
            confidence=0.8,
            status="escalated"
        )
        db_session.add(ticket)
        db_session.commit()
        db_session.refresh(ticket)
        
        # Test with invalid rating (too high)
        feedback_data = {
            "ticket_id": ticket.id,
            "rating": 6,  # Invalid: should be 1-5
            "resolved": True
        }
        
        response = client.post("/feedback/", json=feedback_data)
        
        assert response.status_code == 422  # Validation error

    def test_get_feedback_by_ticket_id_success(self, client, db_session):
        """Test successful feedback retrieval by ticket ID."""
        # Create ticket and feedback
        ticket = Ticket(
            message="Test ticket",
            intent="payment_issue",
            confidence=0.7,
            status="auto_resolved",
            response="Payment issue resolved"
        )
        db_session.add(ticket)
        db_session.commit()
        db_session.refresh(ticket)
        
        feedback = Feedback(
            ticket_id=ticket.id,
            rating=4,
            resolved=True
        )
        db_session.add(feedback)
        db_session.commit()
        db_session.refresh(feedback)
        
        # Get feedback by ticket ID
        response = client.get(f"/feedback/{ticket.id}")
        
        assert response.status_code == 200
        feedback_response = response.json()
        
        assert feedback_response["id"] == feedback.id
        assert feedback_response["ticket_id"] == ticket.id
        assert feedback_response["rating"] == 4
        assert feedback_response["resolved"] is True
        assert "created_at" in feedback_response

    def test_get_feedback_by_ticket_id_not_found(self, client, db_session):
        """Test feedback retrieval for non-existent ticket."""
        response = client.get("/feedback/99999")
        
        assert response.status_code == 404
        error_detail = response.json()
        assert "no feedback found" in error_detail["detail"].lower()

    def test_get_feedback_by_query_success(self, client, db_session):
        """Test successful feedback retrieval using query parameter."""
        # Create ticket and feedback
        ticket = Ticket(
            message="Test ticket for query",
            intent="account_issue",
            confidence=0.6,
            status="escalated"
        )
        db_session.add(ticket)
        db_session.commit()
        db_session.refresh(ticket)
        
        feedback = Feedback(
            ticket_id=ticket.id,
            rating=2,
            resolved=False
        )
        db_session.add(feedback)
        db_session.commit()
        db_session.refresh(feedback)
        
        # Get feedback using query parameter
        response = client.get(f"/feedback/?ticket_id={ticket.id}")
        
        assert response.status_code == 200
        feedback_response = response.json()
        
        assert feedback_response["id"] == feedback.id
        assert feedback_response["ticket_id"] == ticket.id
        assert feedback_response["rating"] == 2
        assert feedback_response["resolved"] is False

    def test_get_feedback_by_query_not_found(self, client, db_session):
        """Test feedback retrieval using query parameter for non-existent ticket."""
        response = client.get("/feedback/?ticket_id=99999")
        
        assert response.status_code == 200
        feedback_response = response.json()
        
        # Should return None when no feedback found
        assert feedback_response is None

    def test_feedback_schema_validation(self, client, db_session):
        """Test feedback schema validation."""
        # Test missing required fields
        invalid_data = {
            "rating": 3
            # Missing ticket_id and resolved
        }
        
        response = client.post("/feedback/", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
        
        # Test invalid rating range
        invalid_rating_data = {
            "ticket_id": 1,
            "rating": 0,  # Invalid: should be 1-5
            "resolved": True
        }
        
        response = client.post("/feedback/", json=invalid_rating_data)
        
        assert response.status_code == 422  # Validation error

    def test_feedback_end_to_end_workflow(self, client, db_session):
        """Test complete feedback workflow."""
        # 1. Create a ticket
        ticket_data = {"message": "I need help with my account"}
        ticket_response = client.post("/tickets/", json=ticket_data)
        assert ticket_response.status_code == 201
        ticket = ticket_response.json()
        
        # 2. Create feedback for the ticket
        feedback_data = {
            "ticket_id": ticket["id"],
            "rating": 4,
            "resolved": True
        }
        feedback_response = client.post("/feedback/", json=feedback_data)
        assert feedback_response.status_code == 201
        feedback = feedback_response.json()
        
        # 3. Retrieve the feedback
        get_response = client.get(f"/feedback/{ticket['id']}")
        assert get_response.status_code == 200
        retrieved_feedback = get_response.json()
        
        # 4. Verify all data is consistent
        assert retrieved_feedback["id"] == feedback["id"]
        assert retrieved_feedback["ticket_id"] == ticket["id"]
        assert retrieved_feedback["rating"] == 4
        assert retrieved_feedback["resolved"] is True
        assert retrieved_feedback["created_at"] == feedback["created_at"]
