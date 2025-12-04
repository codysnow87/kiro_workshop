"""
Property-based tests for event service layer
"""
import pytest
from hypothesis import given, settings, strategies as st
from moto import mock_aws
import boto3
from contextlib import contextmanager
from models.event import CreateEventRequest, UpdateEventRequest
from services.event_service import EventService, EventNotFoundError
from repositories.dynamodb_repository import DynamoDBRepository


# Test helpers
@contextmanager
def create_event_service():
    """Context manager to create an event service with mocked DynamoDB"""
    with mock_aws():
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
        repository = DynamoDBRepository(table_name='events')
        service = EventService(repository)
        yield service


# Strategies for generating test data
valid_non_empty_string = st.text(min_size=1, max_size=100)
valid_date_string = st.dates().map(lambda d: d.strftime('%Y-%m-%d'))
valid_capacity = st.integers(min_value=0, max_value=10000)
valid_status = st.sampled_from(['active', 'cancelled', 'completed', 'scheduled'])


@st.composite
def valid_event_data(draw):
    """Strategy for generating valid event data"""
    return CreateEventRequest(
        title=draw(valid_non_empty_string),
        description=draw(st.text(max_size=500)),
        date=draw(valid_date_string),
        location=draw(valid_non_empty_string),
        capacity=draw(valid_capacity),
        organizer=draw(valid_non_empty_string),
        status=draw(valid_status)
    )


# Feature: event-management-api, Property 1: Create-Retrieve Round Trip
@settings(max_examples=100)
@given(event_data=valid_event_data())
def test_property_create_retrieve_round_trip(event_data):
    """
    Property 1: Create-Retrieve Round Trip
    For any valid event data, creating an event and then retrieving it by eventId 
    should return an event with the same field values.
    Validates: Requirements 1.1, 1.4, 2.1
    """
    with create_event_service() as event_service:
        # Create the event
        created_event = event_service.create_event(event_data)
        
        # Retrieve the event
        retrieved_event = event_service.get_event(created_event.eventId)
        
        # Verify all fields match
        assert retrieved_event.eventId == created_event.eventId
        assert retrieved_event.title == event_data.title
        assert retrieved_event.description == event_data.description
        assert retrieved_event.date == event_data.date
        assert retrieved_event.location == event_data.location
        assert retrieved_event.capacity == event_data.capacity
        assert retrieved_event.organizer == event_data.organizer
        assert retrieved_event.status == event_data.status


# Feature: event-management-api, Property 13: Client-Provided EventId
@settings(max_examples=100)
@given(
    event_data=valid_event_data(),
    client_event_id=st.text(min_size=1, max_size=100)
)
def test_property_client_provided_event_id(event_data, client_event_id):
    """
    Property 13: Client-Provided EventId
    For any POST request that includes an eventId in the request body, 
    the created event should use that exact eventId rather than generating a new one.
    Validates: Requirements 9.7
    """
    with create_event_service() as event_service:
        # Set the client-provided eventId
        event_data.eventId = client_event_id
        
        # Create the event
        created_event = event_service.create_event(event_data)
        
        # Verify the eventId matches the client-provided one
        assert created_event.eventId == client_event_id
        
        # Verify we can retrieve it with that ID
        retrieved_event = event_service.get_event(client_event_id)
        assert retrieved_event.eventId == client_event_id


# Feature: event-management-api, Property 6: List Completeness
@settings(max_examples=100)
@given(events_list=st.lists(valid_event_data(), min_size=0, max_size=10))
def test_property_list_completeness(events_list):
    """
    Property 6: List Completeness
    For any set of created events, listing all events should return 
    a collection containing exactly those events.
    Validates: Requirements 2.3
    """
    with create_event_service() as event_service:
        # Create all events
        created_event_ids = set()
        for event_data in events_list:
            created_event = event_service.create_event(event_data)
            created_event_ids.add(created_event.eventId)
        
        # List all events
        all_events = event_service.list_events()
        retrieved_event_ids = {event.eventId for event in all_events}
        
        # Verify the sets match
        assert created_event_ids == retrieved_event_ids
        assert len(all_events) == len(events_list)


# Feature: event-management-api, Property 7: Status Filter Correctness
@settings(max_examples=100)
@given(
    events_list=st.lists(valid_event_data(), min_size=1, max_size=10),
    filter_status=valid_status
)
def test_property_status_filter_correctness(events_list, filter_status):
    """
    Property 7: Status Filter Correctness
    For any status value and any set of events, filtering by that status 
    should return only events where the status field matches the filter value.
    Validates: Requirements 2.5
    """
    with create_event_service() as event_service:
        # Create all events
        created_events = []
        for event_data in events_list:
            created_event = event_service.create_event(event_data)
            created_events.append(created_event)
        
        # Filter by status
        filtered_events = event_service.list_events(status=filter_status)
        
        # Verify all returned events have the filter status
        for event in filtered_events:
            assert event.status == filter_status
        
        # Verify we got all events with that status
        expected_count = sum(1 for e in created_events if e.status == filter_status)
        assert len(filtered_events) == expected_count


# Feature: event-management-api, Property 8: Update Correctness
@settings(max_examples=100)
@given(
    initial_event=valid_event_data(),
    updated_title=valid_non_empty_string,
    updated_capacity=valid_capacity
)
def test_property_update_correctness(initial_event, updated_title, updated_capacity):
    """
    Property 8: Update Correctness
    For any existing event and any valid update data, updating the event 
    and then retrieving it should return the event with updated values 
    for the modified fields.
    Validates: Requirements 3.1, 3.4
    """
    with create_event_service() as event_service:
        # Create initial event
        created_event = event_service.create_event(initial_event)
        
        # Update the event
        update_data = UpdateEventRequest(
            title=updated_title,
            capacity=updated_capacity
        )
        updated_event = event_service.update_event(created_event.eventId, update_data)
        
        # Retrieve the event
        retrieved_event = event_service.get_event(created_event.eventId)
        
        # Verify updated fields match
        assert retrieved_event.title == updated_title
        assert retrieved_event.capacity == updated_capacity
        
        # Verify unchanged fields remain the same
        assert retrieved_event.description == initial_event.description
        assert retrieved_event.date == initial_event.date
        assert retrieved_event.location == initial_event.location
        assert retrieved_event.organizer == initial_event.organizer
        assert retrieved_event.status == initial_event.status


# Feature: event-management-api, Property 9: Partial Update Preservation
@settings(max_examples=100)
@given(
    initial_event=valid_event_data(),
    field_to_update=st.sampled_from(['title', 'description', 'date', 'location', 'capacity', 'organizer', 'status'])
)
def test_property_partial_update_preservation(initial_event, field_to_update):
    """
    Property 9: Partial Update Preservation
    For any existing event and any partial update containing a subset of fields, 
    updating the event should modify only the specified fields while preserving 
    all other field values unchanged.
    Validates: Requirements 9.5
    """
    with create_event_service() as event_service:
        # Create initial event
        created_event = event_service.create_event(initial_event)
        
        # Create a partial update with only one field
        update_dict = {}
        new_value = None
        
        if field_to_update == 'title':
            new_value = 'Updated Title'
            update_dict['title'] = new_value
        elif field_to_update == 'description':
            new_value = 'Updated Description'
            update_dict['description'] = new_value
        elif field_to_update == 'date':
            new_value = '2025-12-31'
            update_dict['date'] = new_value
        elif field_to_update == 'location':
            new_value = 'Updated Location'
            update_dict['location'] = new_value
        elif field_to_update == 'capacity':
            new_value = 999
            update_dict['capacity'] = new_value
        elif field_to_update == 'organizer':
            new_value = 'Updated Organizer'
            update_dict['organizer'] = new_value
        elif field_to_update == 'status':
            new_value = 'completed'
            update_dict['status'] = new_value
        
        update_data = UpdateEventRequest(**update_dict)
        
        # Update the event
        event_service.update_event(created_event.eventId, update_data)
        
        # Retrieve the event
        retrieved_event = event_service.get_event(created_event.eventId)
        
        # Verify the updated field changed
        assert getattr(retrieved_event, field_to_update) == new_value
        
        # Verify all other fields remain unchanged
        for field in ['title', 'description', 'date', 'location', 'capacity', 'organizer', 'status']:
            if field != field_to_update:
                assert getattr(retrieved_event, field) == getattr(initial_event, field)


# Feature: event-management-api, Property 10: Delete Removes Event
@settings(max_examples=100)
@given(event_data=valid_event_data())
def test_property_delete_removes_event(event_data):
    """
    Property 10: Delete Removes Event
    For any existing event, deleting it should result in subsequent GET requests 
    for that eventId raising EventNotFoundError.
    Validates: Requirements 4.1
    """
    with create_event_service() as event_service:
        # Create an event
        created_event = event_service.create_event(event_data)
        
        # Verify it exists
        retrieved_event = event_service.get_event(created_event.eventId)
        assert retrieved_event.eventId == created_event.eventId
        
        # Delete the event
        event_service.delete_event(created_event.eventId)
        
        # Verify it no longer exists
        with pytest.raises(EventNotFoundError):
            event_service.get_event(created_event.eventId)


# Feature: event-management-api, Property 12: Not Found Error Handling
@settings(max_examples=100)
@given(non_existent_id=st.text(min_size=1, max_size=100))
def test_property_not_found_error_handling(non_existent_id):
    """
    Property 12: Not Found Error Handling
    For any non-existent eventId, GET, PUT, and DELETE operations 
    should raise EventNotFoundError.
    Validates: Requirements 2.2, 3.2, 4.2
    """
    with create_event_service() as event_service:
        # Test GET with non-existent ID
        with pytest.raises(EventNotFoundError):
            event_service.get_event(non_existent_id)
        
        # Test UPDATE with non-existent ID
        update_data = UpdateEventRequest(title='Updated Title')
        with pytest.raises(EventNotFoundError):
            event_service.update_event(non_existent_id, update_data)
        
        # Test DELETE with non-existent ID
        with pytest.raises(EventNotFoundError):
            event_service.delete_event(non_existent_id)
