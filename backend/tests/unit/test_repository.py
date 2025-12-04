"""Unit tests for DynamoDB repository"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from botocore.exceptions import ClientError
from repositories.dynamodb_repository import DynamoDBRepository
from models.event import Event


@pytest.fixture
def mock_dynamodb_table():
    """Create a mock DynamoDB table"""
    with patch('repositories.dynamodb_repository.boto3') as mock_boto3:
        mock_resource = Mock()
        mock_table = Mock()
        mock_boto3.resource.return_value = mock_resource
        mock_resource.Table.return_value = mock_table
        yield mock_table


@pytest.fixture
def repository(mock_dynamodb_table):
    """Create a repository instance with mocked DynamoDB"""
    return DynamoDBRepository(table_name='test-events')


@pytest.fixture
def sample_event():
    """Create a sample event for testing"""
    return Event(
        eventId='test-123',
        title='Test Event',
        description='A test event',
        date='2024-12-15',
        location='Test Location',
        capacity=100,
        organizer='Test Organizer',
        status='active'
    )


class TestPutItem:
    """Tests for put_item method"""
    
    def test_put_item_success(self, repository, mock_dynamodb_table, sample_event):
        """Test successful put_item operation"""
        mock_dynamodb_table.put_item.return_value = {}
        
        result = repository.put_item(sample_event)
        
        assert result == sample_event
        mock_dynamodb_table.put_item.assert_called_once()
        call_args = mock_dynamodb_table.put_item.call_args
        assert call_args[1]['Item']['eventId'] == 'test-123'
        assert call_args[1]['Item']['title'] == 'Test Event'
    
    def test_put_item_dynamodb_error(self, repository, mock_dynamodb_table, sample_event):
        """Test put_item with DynamoDB error"""
        mock_dynamodb_table.put_item.side_effect = ClientError(
            {'Error': {'Message': 'Table not found'}},
            'PutItem'
        )
        
        with pytest.raises(Exception) as exc_info:
            repository.put_item(sample_event)
        
        assert 'Failed to put item in DynamoDB' in str(exc_info.value)


class TestGetItem:
    """Tests for get_item method"""
    
    def test_get_item_existing(self, repository, mock_dynamodb_table):
        """Test get_item with existing event"""
        mock_dynamodb_table.get_item.return_value = {
            'Item': {
                'eventId': 'test-123',
                'title': 'Test Event',
                'description': 'A test event',
                'date': '2024-12-15',
                'location': 'Test Location',
                'capacity': 100,
                'organizer': 'Test Organizer',
                'status': 'active'
            }
        }
        
        result = repository.get_item('test-123')
        
        assert result is not None
        assert result.eventId == 'test-123'
        assert result.title == 'Test Event'
        mock_dynamodb_table.get_item.assert_called_once_with(Key={'eventId': 'test-123'})
    
    def test_get_item_non_existent(self, repository, mock_dynamodb_table):
        """Test get_item with non-existent event"""
        mock_dynamodb_table.get_item.return_value = {}
        
        result = repository.get_item('non-existent')
        
        assert result is None
        mock_dynamodb_table.get_item.assert_called_once_with(Key={'eventId': 'non-existent'})
    
    def test_get_item_dynamodb_error(self, repository, mock_dynamodb_table):
        """Test get_item with DynamoDB error"""
        mock_dynamodb_table.get_item.side_effect = ClientError(
            {'Error': {'Message': 'Access denied'}},
            'GetItem'
        )
        
        with pytest.raises(Exception) as exc_info:
            repository.get_item('test-123')
        
        assert 'Failed to get item from DynamoDB' in str(exc_info.value)


class TestScanItems:
    """Tests for scan_items method"""
    
    def test_scan_items_no_filter(self, repository, mock_dynamodb_table):
        """Test scan_items without filter"""
        mock_dynamodb_table.scan.return_value = {
            'Items': [
                {
                    'eventId': 'event-1',
                    'title': 'Event 1',
                    'description': 'First event',
                    'date': '2024-12-15',
                    'location': 'Location 1',
                    'capacity': 50,
                    'organizer': 'Organizer 1',
                    'status': 'active'
                },
                {
                    'eventId': 'event-2',
                    'title': 'Event 2',
                    'description': 'Second event',
                    'date': '2024-12-16',
                    'location': 'Location 2',
                    'capacity': 100,
                    'organizer': 'Organizer 2',
                    'status': 'cancelled'
                }
            ]
        }
        
        result = repository.scan_items()
        
        assert len(result) == 2
        assert result[0].eventId == 'event-1'
        assert result[1].eventId == 'event-2'
        mock_dynamodb_table.scan.assert_called_once_with()
    
    def test_scan_items_with_filter(self, repository, mock_dynamodb_table):
        """Test scan_items with status filter"""
        mock_dynamodb_table.scan.return_value = {
            'Items': [
                {
                    'eventId': 'event-1',
                    'title': 'Event 1',
                    'description': 'First event',
                    'date': '2024-12-15',
                    'location': 'Location 1',
                    'capacity': 50,
                    'organizer': 'Organizer 1',
                    'status': 'active'
                }
            ]
        }
        
        result = repository.scan_items(filter_expression={'status': 'active'})
        
        assert len(result) == 1
        assert result[0].status == 'active'
        
        # Verify filter expression was built correctly
        call_args = mock_dynamodb_table.scan.call_args
        assert 'FilterExpression' in call_args[1]
        assert 'ExpressionAttributeValues' in call_args[1]
        assert ':status' in call_args[1]['ExpressionAttributeValues']
        assert call_args[1]['ExpressionAttributeValues'][':status'] == 'active'
    
    def test_scan_items_empty_result(self, repository, mock_dynamodb_table):
        """Test scan_items with no results"""
        mock_dynamodb_table.scan.return_value = {'Items': []}
        
        result = repository.scan_items()
        
        assert len(result) == 0
        assert result == []
    
    def test_scan_items_with_pagination(self, repository, mock_dynamodb_table):
        """Test scan_items with paginated results"""
        # First call returns items with LastEvaluatedKey
        mock_dynamodb_table.scan.side_effect = [
            {
                'Items': [
                    {
                        'eventId': 'event-1',
                        'title': 'Event 1',
                        'description': 'First event',
                        'date': '2024-12-15',
                        'location': 'Location 1',
                        'capacity': 50,
                        'organizer': 'Organizer 1',
                        'status': 'active'
                    }
                ],
                'LastEvaluatedKey': {'eventId': 'event-1'}
            },
            {
                'Items': [
                    {
                        'eventId': 'event-2',
                        'title': 'Event 2',
                        'description': 'Second event',
                        'date': '2024-12-16',
                        'location': 'Location 2',
                        'capacity': 100,
                        'organizer': 'Organizer 2',
                        'status': 'active'
                    }
                ]
            }
        ]
        
        result = repository.scan_items()
        
        assert len(result) == 2
        assert result[0].eventId == 'event-1'
        assert result[1].eventId == 'event-2'
        assert mock_dynamodb_table.scan.call_count == 2
    
    def test_scan_items_dynamodb_error(self, repository, mock_dynamodb_table):
        """Test scan_items with DynamoDB error"""
        mock_dynamodb_table.scan.side_effect = ClientError(
            {'Error': {'Message': 'Throttling error'}},
            'Scan'
        )
        
        with pytest.raises(Exception) as exc_info:
            repository.scan_items()
        
        assert 'Failed to scan items from DynamoDB' in str(exc_info.value)


class TestDeleteItem:
    """Tests for delete_item method"""
    
    def test_delete_item_existing(self, repository, mock_dynamodb_table):
        """Test delete_item with existing event"""
        mock_dynamodb_table.delete_item.return_value = {
            'Attributes': {
                'eventId': 'test-123',
                'title': 'Test Event'
            }
        }
        
        result = repository.delete_item('test-123')
        
        assert result is True
        mock_dynamodb_table.delete_item.assert_called_once_with(
            Key={'eventId': 'test-123'},
            ReturnValues='ALL_OLD'
        )
    
    def test_delete_item_non_existent(self, repository, mock_dynamodb_table):
        """Test delete_item with non-existent event"""
        mock_dynamodb_table.delete_item.return_value = {}
        
        result = repository.delete_item('non-existent')
        
        assert result is False
        mock_dynamodb_table.delete_item.assert_called_once_with(
            Key={'eventId': 'non-existent'},
            ReturnValues='ALL_OLD'
        )
    
    def test_delete_item_dynamodb_error(self, repository, mock_dynamodb_table):
        """Test delete_item with DynamoDB error"""
        mock_dynamodb_table.delete_item.side_effect = ClientError(
            {'Error': {'Message': 'Item locked'}},
            'DeleteItem'
        )
        
        with pytest.raises(Exception) as exc_info:
            repository.delete_item('test-123')
        
        assert 'Failed to delete item from DynamoDB' in str(exc_info.value)
