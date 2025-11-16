"""
Tests for the Messages class.
"""
import pytest
from src.transport.transaction.message.messages import Messages
from src.transport.transaction.message.message_info import MessageInfo, message_info
from src.transport.transaction.message.message_info import MessageType


class TestMessages:
    """Test cases for the Messages class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.messages = Messages()
    
    # Test Message Classes
    @message_info(MessageType.COMMAND, "OrderService", "CreateOrder", 1, 0, 0)
    class CreateOrderCommand:
        def __init__(self):
            self.order_id: str = ""
            self.amount: float = 0.0
    
    @message_info(MessageType.EVENT, "OrderService", "OrderCreated", 2, 1, 3)
    class OrderCreatedEvent:
        def __init__(self):
            self.order_id: str = ""
            self.created_at: str = ""
    
    @message_info(MessageType.COMMAND, "PaymentService", "ProcessPayment", 1, 5, 2)
    class ProcessPaymentCommand:
        def __init__(self):
            self.payment_id: str = ""
            self.amount: float = 0.0
    
    class MessageWithoutAttribute:
        def __init__(self):
            self.data: str = ""
    
    def test_add_valid_message_type_returns_message_info(self):
        """Test adding a valid message type returns MessageInfo."""
        # Act
        result = self.messages.add(TestMessages.CreateOrderCommand)
        
        # Assert
        assert result is not None
        assert result.message_type == MessageType.COMMAND
        assert result.endpoint == "OrderService"
        assert result.name == "CreateOrder"
        assert result.major == 1
        assert result.minor == 0
        assert result.patch == 0
    
    def test_add_message_type_without_attribute_raises_value_error(self):
        """Test adding a message type without attribute raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            self.messages.add(TestMessages.MessageWithoutAttribute)
        
        assert "does not have a MessageInfo decorator" in str(excinfo.value)
        assert TestMessages.MessageWithoutAttribute.__name__ in str(excinfo.value)
    
    def test_get_message_info_existing_type_returns_correct_message_info(self):
        """Test getting message info for existing type returns correct info."""
        # Arrange
        self.messages.add(TestMessages.CreateOrderCommand)
        
        # Act
        result = self.messages.get_message_info(TestMessages.CreateOrderCommand)
        
        # Assert
        assert result is not None
        assert result.message_type == MessageType.COMMAND
        assert result.endpoint == "OrderService"
        assert result.name == "CreateOrder"
    
    def test_get_message_info_non_existent_type_returns_none(self):
        """Test getting message info for non-existent type returns None."""
        # Act
        result = self.messages.get_message_info(TestMessages.CreateOrderCommand)
        
        # Assert
        assert result is None
    
    def test_get_header_existing_type_returns_correct_header(self):
        """Test getting header for existing type returns correct header."""
        # Arrange
        self.messages.add(TestMessages.OrderCreatedEvent)
        
        # Act
        result = self.messages.get_header(TestMessages.OrderCreatedEvent)
        
        # Assert
        assert result == "endpoint=OrderService, type=event, name=OrderCreated, version=2.1.3"
    
    def test_get_header_non_existent_type_returns_none(self):
        """Test getting header for non-existent type returns None."""
        # Act
        result = self.messages.get_header(TestMessages.CreateOrderCommand)
        
        # Assert
        assert result is None
    
    def test_get_type_by_header_valid_header_returns_correct_type(self):
        """Test getting type by valid header returns correct type."""
        # Arrange
        self.messages.add(TestMessages.ProcessPaymentCommand)
        header = "endpoint=PaymentService, type=command, name=ProcessPayment, version=1.5.2"
        
        # Act
        result = self.messages.get_type_by_header(header)
        
        # Assert
        assert result == TestMessages.ProcessPaymentCommand
    
    def test_get_type_by_header_invalid_header_returns_none(self):
        """Test getting type by invalid header returns None."""
        # Arrange
        invalid_header = "invalid header format"
        
        # Act
        result = self.messages.get_type_by_header(invalid_header)
        
        # Assert
        assert result is None
    
    def test_get_type_by_header_non_existent_message_returns_none(self):
        """Test getting type by header for non-existent message returns None."""
        # Arrange
        header = "endpoint=UnknownService, type=command, name=UnknownCommand, version=1.0.0"
        
        # Act
        result = self.messages.get_type_by_header(header)
        
        # Assert
        assert result is None
    
    def test_get_type_by_header_caches_results(self):
        """Test that get_type_by_header caches results."""
        # Arrange
        self.messages.add(TestMessages.CreateOrderCommand)
        header = "endpoint=OrderService, type=command, name=CreateOrder, version=1.0.0"
        
        # Act
        result1 = self.messages.get_type_by_header(header)
        result2 = self.messages.get_type_by_header(header)
        
        # Assert
        assert result1 == TestMessages.CreateOrderCommand
        assert result2 == TestMessages.CreateOrderCommand
        assert result1 is result2
    
    def test_get_type_by_message_info_existing_message_info_returns_correct_type(self):
        """Test getting type by existing MessageInfo returns correct type."""
        # Arrange
        self.messages.add(TestMessages.OrderCreatedEvent)
        message_info = MessageInfo(MessageType.EVENT, "OrderService", "OrderCreated", 2, 1, 3)
        
        # Act
        result = self.messages.get_type_by_message_info(message_info)
        
        # Assert
        assert result == TestMessages.OrderCreatedEvent
    
    def test_get_type_by_message_info_non_existent_message_info_returns_none(self):
        """Test getting type by non-existent MessageInfo returns None."""
        # Arrange
        message_info = MessageInfo(MessageType.COMMAND, "UnknownService", "UnknownCommand", 1, 0, 0)
        
        # Act
        result = self.messages.get_type_by_message_info(message_info)
        
        # Assert
        assert result is None
    
    def test_get_type_by_message_info_different_minor_patch_versions_returns_type(self):
        """Test getting type by MessageInfo with different minor/patch versions returns type."""
        # Arrange
        self.messages.add(TestMessages.OrderCreatedEvent)  # Has version 2.1.3
        message_info_different_minor = MessageInfo(MessageType.EVENT, "OrderService", "OrderCreated", 2, 5, 3)
        message_info_different_patch = MessageInfo(MessageType.EVENT, "OrderService", "OrderCreated", 2, 1, 9)
        
        # Act
        result1 = self.messages.get_type_by_message_info(message_info_different_minor)
        result2 = self.messages.get_type_by_message_info(message_info_different_patch)
        
        # Assert
        assert result1 == TestMessages.OrderCreatedEvent
        assert result2 == TestMessages.OrderCreatedEvent
    
    def test_get_type_by_message_info_different_major_version_returns_none(self):
        """Test getting type by MessageInfo with different major version returns None."""
        # Arrange
        self.messages.add(TestMessages.OrderCreatedEvent)  # Has version 2.1.3
        message_info_different_major = MessageInfo(MessageType.EVENT, "OrderService", "OrderCreated", 3, 1, 3)
        
        # Act
        result = self.messages.get_type_by_message_info(message_info_different_major)
        
        # Assert
        assert result is None
    
    def test_multiple_messages_all_methods_work_correctly(self):
        """Test that all methods work correctly with multiple messages."""
        # Arrange
        self.messages.add(TestMessages.CreateOrderCommand)
        self.messages.add(TestMessages.OrderCreatedEvent)
        self.messages.add(TestMessages.ProcessPaymentCommand)
        
        # Act & Assert - get_message_info
        command_info = self.messages.get_message_info(TestMessages.CreateOrderCommand)
        event_info = self.messages.get_message_info(TestMessages.OrderCreatedEvent)
        payment_info = self.messages.get_message_info(TestMessages.ProcessPaymentCommand)
        
        assert command_info.message_type == MessageType.COMMAND
        assert event_info.message_type == MessageType.EVENT
        assert payment_info.endpoint == "PaymentService"
        
        # Act & Assert - get_header
        command_header = self.messages.get_header(TestMessages.CreateOrderCommand)
        event_header = self.messages.get_header(TestMessages.OrderCreatedEvent)
        
        assert "OrderService" in command_header
        assert "OrderCreated" in event_header
        
        # Act & Assert - get_type_by_header
        type_from_header = self.messages.get_type_by_header(command_header)
        assert type_from_header == TestMessages.CreateOrderCommand
    
    def test_add_same_type_twice_raises_key_error(self):
        """Test adding the same type twice raises KeyError."""
        # Arrange
        self.messages.add(TestMessages.CreateOrderCommand)
        
        # Act & Assert
        with pytest.raises(KeyError):
            self.messages.add(TestMessages.CreateOrderCommand)