"""Event service layer for business logic"""
import uuid
from typing import Optional, List
from models.event import Event, CreateEventRequest, UpdateEventRequest
from repositories.dynamodb_repository import DynamoDBRepository


class EventNotFoundError(Exception):
    """Exception raised when an event is not found"""
    pass


class EventService:
    """Service class for event business logic"""
    
    def __init__(self, repository: DynamoDBRepository):
        """
        Initialize event service
        
        Args:
            repository: DynamoDB repository instance
        """
        self.repository = repository
    
    def create_event(self, event_data: CreateEventRequest) -> Event:
        """
        Create a new event
        
        Args:
            event_data: Event creation request data
            
        Returns:
            Created event with eventId
            
        Raises:
            Exception: If repository operation fails
        """
        # Generate eventId if not provided
        event_id = event_data.eventId if event_data.eventId else str(uuid.uuid4())
        
        # Create Event object with all fields
        event = Event(
            eventId=event_id,
            title=event_data.title,
            description=event_data.description,
            date=event_data.date,
            location=event_data.location,
            capacity=event_data.capacity,
            organizer=event_data.organizer,
            status=event_data.status
        )
        
        # Store in repository
        return self.repository.put_item(event)
    
    def get_event(self, event_id: str) -> Event:
        """
        Retrieve an event by ID
        
        Args:
            event_id: The unique event identifier
            
        Returns:
            Event object
            
        Raises:
            EventNotFoundError: If event doesn't exist
            Exception: If repository operation fails
        """
        event = self.repository.get_item(event_id)
        
        if event is None:
            raise EventNotFoundError(f"Event with id '{event_id}' not found")
        
        return event
    
    def list_events(self, status: Optional[str] = None) -> List[Event]:
        """
        List all events with optional status filter
        
        Args:
            status: Optional status value to filter by
            
        Returns:
            List of events matching the filter
            
        Raises:
            Exception: If repository operation fails
        """
        if status:
            filter_expression = {'status': status}
            return self.repository.scan_items(filter_expression)
        else:
            return self.repository.scan_items()
    
    def update_event(self, event_id: str, update_data: UpdateEventRequest) -> Event:
        """
        Update an existing event (partial updates supported)
        
        Args:
            event_id: The unique event identifier
            update_data: Fields to update (only provided fields are updated)
            
        Returns:
            Updated event object
            
        Raises:
            EventNotFoundError: If event doesn't exist
            Exception: If repository operation fails
        """
        # Retrieve existing event
        existing_event = self.get_event(event_id)
        
        # Merge update data with existing event
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Create updated event by merging
        updated_data = existing_event.model_dump()
        updated_data.update(update_dict)
        
        updated_event = Event(**updated_data)
        
        # Store updated event
        return self.repository.put_item(updated_event)
    
    def delete_event(self, event_id: str) -> None:
        """
        Delete an event
        
        Args:
            event_id: The unique event identifier
            
        Raises:
            EventNotFoundError: If event doesn't exist
            Exception: If repository operation fails
        """
        # Check if event exists first
        self.get_event(event_id)
        
        # Delete the event
        self.repository.delete_item(event_id)
