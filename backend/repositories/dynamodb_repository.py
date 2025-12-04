"""DynamoDB repository for event data persistence"""
import os
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from models.event import Event


class DynamoDBRepository:
    """Repository class for DynamoDB operations on events"""
    
    def __init__(self, table_name: Optional[str] = None):
        """
        Initialize DynamoDB repository
        
        Args:
            table_name: Name of the DynamoDB table (defaults to DYNAMODB_TABLE_NAME env var)
        """
        self.table_name = table_name or os.environ.get('DYNAMODB_TABLE_NAME', 'events')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)
    
    def put_item(self, event: Event) -> Event:
        """
        Store an event in DynamoDB
        
        Args:
            event: Event object to store
            
        Returns:
            The stored event
            
        Raises:
            Exception: If DynamoDB operation fails
        """
        try:
            item = event.model_dump()
            self.table.put_item(Item=item)
            return event
        except ClientError as e:
            raise Exception(f"Failed to put item in DynamoDB: {e.response['Error']['Message']}")
    
    def get_item(self, event_id: str) -> Optional[Event]:
        """
        Retrieve an event by eventId
        
        Args:
            event_id: The unique event identifier
            
        Returns:
            Event object if found, None otherwise
            
        Raises:
            Exception: If DynamoDB operation fails
        """
        try:
            response = self.table.get_item(Key={'eventId': event_id})
            
            if 'Item' not in response:
                return None
            
            return Event(**response['Item'])
        except ClientError as e:
            raise Exception(f"Failed to get item from DynamoDB: {e.response['Error']['Message']}")
    
    def scan_items(self, filter_expression: Optional[Dict[str, Any]] = None) -> List[Event]:
        """
        Scan all events with optional filtering
        
        Args:
            filter_expression: Optional dictionary with filter parameters
                              Example: {'status': 'active'}
            
        Returns:
            List of Event objects matching the filter
            
        Raises:
            Exception: If DynamoDB operation fails
        """
        try:
            scan_kwargs = {}
            
            if filter_expression:
                # Build filter expression for DynamoDB
                filter_parts = []
                expression_attribute_values = {}
                expression_attribute_names = {}
                
                for key, value in filter_expression.items():
                    filter_parts.append(f"#{key} = :{key}")
                    expression_attribute_values[f":{key}"] = value
                    expression_attribute_names[f"#{key}"] = key
                
                scan_kwargs['FilterExpression'] = ' AND '.join(filter_parts)
                scan_kwargs['ExpressionAttributeValues'] = expression_attribute_values
                scan_kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
            response = self.table.scan(**scan_kwargs)
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = self.table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))
            
            return [Event(**item) for item in items]
        except ClientError as e:
            raise Exception(f"Failed to scan items from DynamoDB: {e.response['Error']['Message']}")
    
    def delete_item(self, event_id: str) -> bool:
        """
        Delete an event by eventId
        
        Args:
            event_id: The unique event identifier
            
        Returns:
            True if item was deleted, False if item didn't exist
            
        Raises:
            Exception: If DynamoDB operation fails
        """
        try:
            response = self.table.delete_item(
                Key={'eventId': event_id},
                ReturnValues='ALL_OLD'
            )
            
            # If 'Attributes' is in response, the item existed and was deleted
            return 'Attributes' in response
        except ClientError as e:
            raise Exception(f"Failed to delete item from DynamoDB: {e.response['Error']['Message']}")
