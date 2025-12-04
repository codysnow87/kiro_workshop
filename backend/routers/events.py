"""Events router for CRUD operations"""
import os
from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import Optional, List
from models.event import Event, CreateEventRequest, UpdateEventRequest
from services.event_service import EventService, EventNotFoundError
from repositories.dynamodb_repository import DynamoDBRepository

router = APIRouter(prefix="/events", tags=["events"])

# Dependency to get repository instance
def get_repository() -> DynamoDBRepository:
    """Get DynamoDB repository instance with table name from environment"""
    table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'events')
    return DynamoDBRepository(table_name=table_name)


# Dependency to get service instance
def get_event_service(repository: DynamoDBRepository = Depends(get_repository)) -> EventService:
    """Get event service instance with repository"""
    return EventService(repository)


@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: CreateEventRequest,
    service: EventService = Depends(get_event_service)
) -> Event:
    """
    Create a new event
    
    Args:
        event_data: Event creation request data
        service: Event service instance (injected)
        
    Returns:
        Created event with eventId
        
    Raises:
        HTTPException: 422 if validation fails
    """
    try:
        return service.create_event(event_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=List[Event])
async def list_events(
    status_filter: Optional[str] = Query(None, alias="status"),
    service: EventService = Depends(get_event_service)
) -> List[Event]:
    """
    List all events with optional status filter
    
    Args:
        status_filter: Optional status value to filter by
        service: Event service instance (injected)
        
    Returns:
        List of events matching the filter
    """
    try:
        return service.list_events(status=status_filter)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{eventId}", response_model=Event)
async def get_event(
    eventId: str,
    service: EventService = Depends(get_event_service)
) -> Event:
    """
    Retrieve a specific event by ID
    
    Args:
        eventId: The unique event identifier
        service: Event service instance (injected)
        
    Returns:
        Event object
        
    Raises:
        HTTPException: 404 if event not found
    """
    try:
        return service.get_event(eventId)
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{eventId}", response_model=Event)
async def update_event(
    eventId: str,
    update_data: UpdateEventRequest,
    service: EventService = Depends(get_event_service)
) -> Event:
    """
    Update an existing event (partial updates supported)
    
    Args:
        eventId: The unique event identifier
        update_data: Fields to update (only provided fields are updated)
        service: Event service instance (injected)
        
    Returns:
        Updated event object
        
    Raises:
        HTTPException: 404 if event not found, 422 if validation fails
    """
    try:
        return service.update_event(eventId, update_data)
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{eventId}", status_code=status.HTTP_200_OK)
async def delete_event(
    eventId: str,
    service: EventService = Depends(get_event_service)
) -> dict:
    """
    Delete an event
    
    Args:
        eventId: The unique event identifier
        service: Event service instance (injected)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if event not found
    """
    try:
        service.delete_event(eventId)
        return {"message": f"Event {eventId} deleted successfully"}
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
