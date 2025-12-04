"""Integration tests for Event Management API endpoints"""
import os
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
import boto3
from main import app


@pytest.fixture(scope="function")
def dynamodb_table():
    """Create a mock DynamoDB table for testing"""
    with mock_aws():
        # Set environment variable for table name
        os.environ['DYNAMODB_TABLE_NAME'] = 'test-events'
        
        # Create DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-events',
            KeySchema=[
                {'AttributeName': 'eventId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'eventId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield table
        
        # Cleanup
        table.delete()


@pytest.fixture
def client(dynamodb_table):
    """Create a test client with mocked DynamoDB"""
    return TestClient(app)


class TestCreateEvent:
    """Tests for POST /events endpoint"""
    
    def test_create_event_success(self, client):
        """Test successful event creation returns 201 with eventId"""
        event_data = {
            "title": "Tech Conference 2024",
            "description": "Annual technology conference",
            "date": "2024-12-15",
            "location": "San Francisco",
            "capacity": 500,
            "organizer": "Tech Corp",
            "status": "scheduled"
        }
        
        response = client.post("/events", json=event_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "eventId" in data
        assert data["title"] == event_data["title"]
        assert data["description"] == event_data["description"]
        assert data["date"] == event_data["date"]
        assert data["location"] == event_data["location"]
        assert data["capacity"] == event_data["capacity"]
        assert data["organizer"] == event_data["organizer"]
        assert data["status"] == event_data["status"]
    
    def test_create_event_with_provided_id(self, client):
        """Test creating event with client-provided eventId"""
        event_data = {
            "eventId": "custom-event-123",
            "title": "Workshop",
            "description": "Python workshop",
            "date": "2024-11-20",
            "location": "Online",
            "capacity": 50,
            "organizer": "Python Community",
            "status": "active"
        }
        
        response = client.post("/events", json=event_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["eventId"] == "custom-event-123"
    
    def test_create_event_missing_required_field(self, client):
        """Test creating event with missing required field returns 422"""
        event_data = {
            "title": "Incomplete Event",
            "date": "2024-12-01",
            # Missing description, location, capacity, organizer, status
        }
        
        response = client.post("/events", json=event_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_event_invalid_data_type(self, client):
        """Test creating event with invalid data type returns 422"""
        event_data = {
            "title": "Invalid Event",
            "description": "Test",
            "date": "2024-12-01",
            "location": "Test Location",
            "capacity": "not-a-number",  # Should be integer
            "organizer": "Test Org",
            "status": "active"
        }
        
        response = client.post("/events", json=event_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_event_negative_capacity(self, client):
        """Test creating event with negative capacity returns 422"""
        event_data = {
            "title": "Invalid Capacity Event",
            "description": "Test event",
            "date": "2024-12-01",
            "location": "Test Location",
            "capacity": -10,
            "organizer": "Test Org",
            "status": "active"
        }
        
        response = client.post("/events", json=event_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestListEvents:
    """Tests for GET /events endpoint"""
    
    def test_list_events_empty(self, client):
        """Test listing events when table is empty returns empty list"""
        response = client.get("/events")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_events_with_data(self, client):
        """Test listing all events returns all created events"""
        # Create multiple events
        events = [
            {
                "title": "Event 1",
                "description": "First event",
                "date": "2024-12-01",
                "location": "Location 1",
                "capacity": 100,
                "organizer": "Org 1",
                "status": "scheduled"
            },
            {
                "title": "Event 2",
                "description": "Second event",
                "date": "2024-12-02",
                "location": "Location 2",
                "capacity": 200,
                "organizer": "Org 2",
                "status": "active"
            }
        ]
        
        for event in events:
            client.post("/events", json=event)
        
        response = client.get("/events")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_list_events_with_status_filter(self, client):
        """Test listing events with status filter returns only matching events"""
        # Create events with different statuses
        events = [
            {
                "title": "Scheduled Event",
                "description": "Event 1",
                "date": "2024-12-01",
                "location": "Location 1",
                "capacity": 100,
                "organizer": "Org 1",
                "status": "scheduled"
            },
            {
                "title": "Active Event",
                "description": "Event 2",
                "date": "2024-12-02",
                "location": "Location 2",
                "capacity": 200,
                "organizer": "Org 2",
                "status": "active"
            },
            {
                "title": "Another Scheduled",
                "description": "Event 3",
                "date": "2024-12-03",
                "location": "Location 3",
                "capacity": 150,
                "organizer": "Org 3",
                "status": "scheduled"
            }
        ]
        
        for event in events:
            client.post("/events", json=event)
        
        response = client.get("/events?status=scheduled")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for event in data:
            assert event["status"] == "scheduled"


class TestGetEvent:
    """Tests for GET /events/{eventId} endpoint"""
    
    def test_get_event_success(self, client):
        """Test retrieving existing event returns 200 with event data"""
        # Create an event
        event_data = {
            "eventId": "test-event-123",
            "title": "Test Event",
            "description": "Test description",
            "date": "2024-12-01",
            "location": "Test Location",
            "capacity": 100,
            "organizer": "Test Org",
            "status": "active"
        }
        
        client.post("/events", json=event_data)
        
        response = client.get("/events/test-event-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["eventId"] == "test-event-123"
        assert data["title"] == event_data["title"]
    
    def test_get_event_not_found(self, client):
        """Test retrieving non-existent event returns 404"""
        response = client.get("/events/non-existent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestUpdateEvent:
    """Tests for PUT /events/{eventId} endpoint"""
    
    def test_update_event_success(self, client):
        """Test updating existing event returns 200 with updated data"""
        # Create an event
        event_data = {
            "eventId": "update-test-123",
            "title": "Original Title",
            "description": "Original description",
            "date": "2024-12-01",
            "location": "Original Location",
            "capacity": 100,
            "organizer": "Original Org",
            "status": "scheduled"
        }
        
        client.post("/events", json=event_data)
        
        # Update the event
        update_data = {
            "title": "Updated Title",
            "capacity": 150
        }
        
        response = client.put("/events/update-test-123", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["capacity"] == 150
        assert data["description"] == "Original description"  # Unchanged
    
    def test_update_event_partial(self, client):
        """Test partial update preserves unchanged fields"""
        # Create an event
        event_data = {
            "eventId": "partial-update-123",
            "title": "Original Title",
            "description": "Original description",
            "date": "2024-12-01",
            "location": "Original Location",
            "capacity": 100,
            "organizer": "Original Org",
            "status": "scheduled"
        }
        
        client.post("/events", json=event_data)
        
        # Update only status
        update_data = {"status": "cancelled"}
        
        response = client.put("/events/partial-update-123", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert data["title"] == "Original Title"
        assert data["capacity"] == 100
    
    def test_update_event_not_found(self, client):
        """Test updating non-existent event returns 404"""
        update_data = {"title": "New Title"}
        
        response = client.put("/events/non-existent-id", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_update_event_invalid_data(self, client):
        """Test updating with invalid data returns 422"""
        # Create an event
        event_data = {
            "eventId": "invalid-update-123",
            "title": "Test Event",
            "description": "Test",
            "date": "2024-12-01",
            "location": "Test Location",
            "capacity": 100,
            "organizer": "Test Org",
            "status": "active"
        }
        
        client.post("/events", json=event_data)
        
        # Try to update with invalid capacity
        update_data = {"capacity": -50}
        
        response = client.put("/events/invalid-update-123", json=update_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestDeleteEvent:
    """Tests for DELETE /events/{eventId} endpoint"""
    
    def test_delete_event_success(self, client):
        """Test deleting existing event returns 200"""
        # Create an event
        event_data = {
            "eventId": "delete-test-123",
            "title": "To Be Deleted",
            "description": "Test event",
            "date": "2024-12-01",
            "location": "Test Location",
            "capacity": 100,
            "organizer": "Test Org",
            "status": "active"
        }
        
        client.post("/events", json=event_data)
        
        response = client.delete("/events/delete-test-123")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_delete_event_not_found(self, client):
        """Test deleting non-existent event returns 404"""
        response = client.delete("/events/non-existent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_delete_event_removes_from_database(self, client):
        """Test deleted event cannot be retrieved"""
        # Create an event
        event_data = {
            "eventId": "delete-verify-123",
            "title": "To Be Deleted",
            "description": "Test event",
            "date": "2024-12-01",
            "location": "Test Location",
            "capacity": 100,
            "organizer": "Test Org",
            "status": "active"
        }
        
        client.post("/events", json=event_data)
        
        # Delete the event
        delete_response = client.delete("/events/delete-verify-123")
        assert delete_response.status_code == 200
        
        # Try to retrieve the deleted event
        get_response = client.get("/events/delete-verify-123")
        assert get_response.status_code == 404


class TestErrorResponseFormat:
    """Tests for error response format"""
    
    def test_validation_error_has_detail(self, client):
        """Test validation errors include detail field"""
        event_data = {
            "title": "Invalid Event"
            # Missing required fields
        }
        
        response = client.post("/events", json=event_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
    
    def test_not_found_error_has_detail(self, client):
        """Test not found errors include detail field"""
        response = client.get("/events/non-existent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
