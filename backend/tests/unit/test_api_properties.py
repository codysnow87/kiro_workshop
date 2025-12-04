"""
Property-based tests for FastAPI routes
"""
import pytest
from hypothesis import given, settings, strategies as st
from fastapi.testclient import TestClient
from moto import mock_aws
import boto3
from contextlib import contextmanager
from main import app


# Test helpers
@contextmanager
def setup_test_environment():
    """Context manager to set up test environment with mocked DynamoDB"""
    import os
    with mock_aws():
        # Set environment variable for table name
        os.environ['DYNAMODB_TABLE_NAME'] = 'events'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='events',
            KeySchema=[
                {'AttributeName': 'eventId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'eventId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        client = TestClient(app)
        yield client


# Strategies for generating test data
valid_non_empty_string = st.text(min_size=1, max_size=100)
valid_date_string = st.dates().map(lambda d: d.strftime('%Y-%m-%d'))
valid_capacity = st.integers(min_value=0, max_value=10000)
valid_status = st.sampled_from(['active', 'cancelled', 'completed', 'scheduled'])


@st.composite
def valid_event_request(draw):
    """Strategy for generating valid event creation requests"""
    return {
        "title": draw(valid_non_empty_string),
        "description": draw(st.text(max_size=500)),
        "date": draw(valid_date_string),
        "location": draw(valid_non_empty_string),
        "capacity": draw(valid_capacity),
        "organizer": draw(valid_non_empty_string),
        "status": draw(valid_status)
    }


# Feature: event-management-api, Property 15: Create Success Status
@settings(max_examples=100)
@given(event_data=valid_event_request())
def test_property_create_success_status(event_data):
    """
    Property 15: Create Success Status
    For any successful create operation, the API should return HTTP status code 201 
    and include the complete event data with eventId in the response.
    Validates: Requirements 7.1, 9.3
    """
    with setup_test_environment() as client:
        # Create an event via POST
        response = client.post("/events", json=event_data)
        
        # Verify status code is 201
        assert response.status_code == 201
        
        # Verify response contains complete event data
        response_data = response.json()
        assert "eventId" in response_data
        assert response_data["eventId"] is not None
        assert len(response_data["eventId"]) > 0
        
        # Verify all input fields are in the response
        assert response_data["title"] == event_data["title"]
        assert response_data["description"] == event_data["description"]
        assert response_data["date"] == event_data["date"]
        assert response_data["location"] == event_data["location"]
        assert response_data["capacity"] == event_data["capacity"]
        assert response_data["organizer"] == event_data["organizer"]
        assert response_data["status"] == event_data["status"]


# Feature: event-management-api, Property 11: Delete Success Status
@settings(max_examples=100)
@given(event_data=valid_event_request())
def test_property_delete_success_status(event_data):
    """
    Property 11: Delete Success Status
    For any successful delete operation, the API should return HTTP status code 200 or 204.
    Validates: Requirements 4.3
    """
    with setup_test_environment() as client:
        # Create an event first
        create_response = client.post("/events", json=event_data)
        assert create_response.status_code == 201
        event_id = create_response.json()["eventId"]
        
        # Delete the event
        delete_response = client.delete(f"/events/{event_id}")
        
        # Verify status code is 200 or 204
        assert delete_response.status_code in [200, 204]


# Strategy for URL-safe non-existent IDs
url_safe_id = st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'), min_size=1, max_size=100)


# Feature: event-management-api, Property 14: Error Response Format
@settings(max_examples=100)
@given(non_existent_id=url_safe_id)
def test_property_error_response_format(non_existent_id):
    """
    Property 14: Error Response Format
    For any error condition, the API response should include a JSON body 
    with a "detail" field containing a descriptive error message.
    Validates: Requirements 6.4
    """
    with setup_test_environment() as client:
        # Test GET with non-existent ID (404 error)
        response = client.get(f"/events/{non_existent_id}")
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], str)
        assert len(response_data["detail"]) > 0
        
        # Test PUT with non-existent ID (404 error)
        update_data = {"title": "Updated Title"}
        response = client.put(f"/events/{non_existent_id}", json=update_data)
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], str)
        assert len(response_data["detail"]) > 0
        
        # Test DELETE with non-existent ID (404 error)
        response = client.delete(f"/events/{non_existent_id}")
        assert response.status_code == 404
        response_data = response.json()
        assert "detail" in response_data
        assert isinstance(response_data["detail"], str)
        assert len(response_data["detail"]) > 0
        
        # Test POST with invalid data (422 validation error)
        invalid_data = {"title": ""}  # Empty title should fail validation
        response = client.post("/events", json=invalid_data)
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data
