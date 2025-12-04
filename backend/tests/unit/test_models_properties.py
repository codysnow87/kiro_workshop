"""
Property-based tests for event models validation
"""
import pytest
from hypothesis import given, settings, strategies as st
from pydantic import ValidationError
from models.event import CreateEventRequest, UpdateEventRequest, Event


# Strategies for generating test data
valid_non_empty_string = st.text(min_size=1)
valid_date_string = st.dates().map(lambda d: d.strftime('%Y-%m-%d'))
valid_capacity = st.integers(min_value=0, max_value=10000)


# Feature: event-management-api, Property 2: Input Validation Completeness
@settings(max_examples=100)
@given(
    missing_field=st.sampled_from(['title', 'description', 'date', 'location', 'capacity', 'organizer', 'status'])
)
def test_property_missing_required_fields_rejected(missing_field):
    """
    Property 2: Input Validation Completeness
    For any event data with missing required fields, the API should reject the request
    Validates: Requirements 1.2, 5.1, 5.2, 5.4, 5.6, 5.7, 6.3
    """
    # Create a valid event data dict
    valid_data = {
        'title': 'Test Event',
        'description': 'Test Description',
        'date': '2024-12-15',
        'location': 'Test Location',
        'capacity': 100,
        'organizer': 'Test Organizer',
        'status': 'active'
    }
    
    # Remove the field we're testing
    test_data = {k: v for k, v in valid_data.items() if k != missing_field}
    
    # Should raise ValidationError
    with pytest.raises(ValidationError) as exc_info:
        CreateEventRequest(**test_data)
    
    # Verify the error mentions the missing field
    error_dict = exc_info.value.errors()
    assert any(missing_field in str(error) for error in error_dict), \
        f"Expected validation error to mention missing field '{missing_field}'"


# Additional test for empty strings on non-empty fields
@settings(max_examples=100)
@given(
    empty_field=st.sampled_from(['title', 'location', 'organizer', 'status'])
)
def test_property_empty_strings_rejected(empty_field):
    """
    Property 2: Input Validation Completeness (empty string variant)
    For any event data with empty strings in non-empty fields, the API should reject the request
    Validates: Requirements 5.1, 5.4, 5.6, 5.7
    """
    valid_data = {
        'title': 'Test Event',
        'description': 'Test Description',
        'date': '2024-12-15',
        'location': 'Test Location',
        'capacity': 100,
        'organizer': 'Test Organizer',
        'status': 'active'
    }
    
    # Set the field to empty string
    test_data = valid_data.copy()
    test_data[empty_field] = ''
    
    # Should raise ValidationError
    with pytest.raises(ValidationError) as exc_info:
        CreateEventRequest(**test_data)
    
    # Verify the error is about string length
    error_dict = exc_info.value.errors()
    assert len(error_dict) > 0, "Expected validation error for empty string"


# Feature: event-management-api, Property 3: Type Validation
@settings(max_examples=100)
@given(
    field_name=st.sampled_from(['title', 'description', 'date', 'location', 'organizer', 'status']),
    invalid_value=st.one_of(st.integers(), st.floats(), st.lists(st.text()), st.dictionaries(st.text(), st.text()))
)
def test_property_type_validation_strings(field_name, invalid_value):
    """
    Property 3: Type Validation
    For any event data with invalid data types for string fields, the API should reject the request
    Validates: Requirements 1.3, 3.3, 5.2
    """
    valid_data = {
        'title': 'Test Event',
        'description': 'Test Description',
        'date': '2024-12-15',
        'location': 'Test Location',
        'capacity': 100,
        'organizer': 'Test Organizer',
        'status': 'active'
    }
    
    # Replace the field with an invalid type
    test_data = valid_data.copy()
    test_data[field_name] = invalid_value
    
    # Should raise ValidationError
    with pytest.raises(ValidationError) as exc_info:
        CreateEventRequest(**test_data)
    
    # Verify we got a validation error
    error_dict = exc_info.value.errors()
    assert len(error_dict) > 0, "Expected validation error for invalid type"


@settings(max_examples=100)
@given(
    invalid_capacity=st.one_of(
        st.text(alphabet=st.characters(blacklist_categories=('Nd',)), min_size=1),  # Non-numeric strings
        st.lists(st.integers()), 
        st.dictionaries(st.text(), st.text())
    )
)
def test_property_type_validation_capacity(invalid_capacity):
    """
    Property 3: Type Validation (capacity field)
    For any event data with invalid data type for capacity field, the API should reject the request
    Note: Pydantic coerces compatible types (e.g., float to int, numeric strings), so we test truly incompatible types
    Validates: Requirements 1.3, 3.3, 5.2
    """
    valid_data = {
        'title': 'Test Event',
        'description': 'Test Description',
        'date': '2024-12-15',
        'location': 'Test Location',
        'capacity': 100,
        'organizer': 'Test Organizer',
        'status': 'active'
    }
    
    # Replace capacity with an invalid type
    test_data = valid_data.copy()
    test_data['capacity'] = invalid_capacity
    
    # Should raise ValidationError
    with pytest.raises(ValidationError) as exc_info:
        CreateEventRequest(**test_data)
    
    # Verify we got a validation error
    error_dict = exc_info.value.errors()
    assert len(error_dict) > 0, "Expected validation error for invalid capacity type"


# Feature: event-management-api, Property 4: Date Format Validation
@settings(max_examples=100)
@given(
    invalid_date=st.one_of(
        st.text(min_size=1, max_size=50).filter(lambda x: not _is_valid_date_format(x)),
        st.integers(),
        st.lists(st.text())
    )
)
def test_property_date_format_validation(invalid_date):
    """
    Property 4: Date Format Validation
    For any event data with an invalid date format, the API should reject the request
    Validates: Requirements 5.3
    """
    valid_data = {
        'title': 'Test Event',
        'description': 'Test Description',
        'date': '2024-12-15',
        'location': 'Test Location',
        'capacity': 100,
        'organizer': 'Test Organizer',
        'status': 'active'
    }
    
    # Replace date with invalid format
    test_data = valid_data.copy()
    test_data['date'] = invalid_date
    
    # Should raise ValidationError
    with pytest.raises(ValidationError) as exc_info:
        CreateEventRequest(**test_data)
    
    # Verify we got a validation error
    error_dict = exc_info.value.errors()
    assert len(error_dict) > 0, "Expected validation error for invalid date format"


def _is_valid_date_format(s: str) -> bool:
    """Helper to check if a string is in YYYY-MM-DD format"""
    if not isinstance(s, str):
        return False
    try:
        from datetime import datetime
        datetime.strptime(s, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


# Feature: event-management-api, Property 5: Capacity Validation
@settings(max_examples=100)
@given(
    negative_capacity=st.integers(max_value=-1)
)
def test_property_capacity_validation(negative_capacity):
    """
    Property 5: Capacity Validation
    For any event data with a negative capacity value, the API should reject the request
    Validates: Requirements 5.5
    """
    valid_data = {
        'title': 'Test Event',
        'description': 'Test Description',
        'date': '2024-12-15',
        'location': 'Test Location',
        'capacity': 100,
        'organizer': 'Test Organizer',
        'status': 'active'
    }
    
    # Replace capacity with negative value
    test_data = valid_data.copy()
    test_data['capacity'] = negative_capacity
    
    # Should raise ValidationError
    with pytest.raises(ValidationError) as exc_info:
        CreateEventRequest(**test_data)
    
    # Verify we got a validation error about capacity
    error_dict = exc_info.value.errors()
    assert len(error_dict) > 0, "Expected validation error for negative capacity"
    assert any('capacity' in str(error).lower() or 'greater' in str(error).lower() 
               for error in error_dict), "Expected error to mention capacity constraint"
