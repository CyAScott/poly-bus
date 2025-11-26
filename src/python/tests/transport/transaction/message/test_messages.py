"""
Tests for the Messages class.
"""
import pytest
from src.transport.transaction.message.messages import Messages
from src.transport.transaction.message.message_info import MessageInfo, message_info
from src.transport.transaction.message.message_info import MessageType
from src.transport.transaction.message.poly_bus_message_not_found_error import PolyBusMessageNotFoundError


class TestMessages:
    """Test cases for the Messages class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.messages = Messages()
    
    # Test Message Classes
    @message_info(MessageType.COMMAND, "polybus", "polybus-command", 1, 0, 0)
    class Command:
        def __init__(self):
            self.order_id: str = ""
            self.amount: float = 0.0
    
    @message_info(MessageType.EVENT, "polybus", "polybus-event", 2, 1, 3)
    class Event:
        def __init__(self):
            self.order_id: str = ""
            self.created_at: str = ""
    
    class MessageWithoutAttribute:
        def __init__(self):
            self.data: str = ""
    
    def test_add_valid_message_type_returns_message_info(self):
        """Test adding a valid message type returns MessageInfo."""
        # Act
        result = self.messages.add(TestMessages.Command)
        
        # Assert
        assert result is not None
        assert result.message_type == MessageType.COMMAND
        assert result.endpoint == "polybus"
        assert result.name == "polybus-command"
        assert result.major == 1
        assert result.minor == 0
        assert result.patch == 0
    
    def test_add_message_type_without_attribute_throws_error(self):
        """Test adding a message type without attribute throws error."""
        # Act & Assert
        with pytest.raises(PolyBusMessageNotFoundError):
            self.messages.add(TestMessages.MessageWithoutAttribute)
    
    def test_get_message_info_existing_type_returns_correct_message_info(self):
        """Test getting message info for existing type returns correct info."""
        # Arrange
        self.messages.add(TestMessages.Command)
        
        # Act
        result = self.messages.get_message_info(TestMessages.Command)
        
        # Assert
        assert result is not None
        assert result.message_type == MessageType.COMMAND
        assert result.endpoint == "polybus"
        assert result.name == "polybus-command"
    
    def test_get_message_info_non_existent_type_throws_error(self):
        """Test getting message info for non-existent type throws error."""
        # Act & Assert
        with pytest.raises(PolyBusMessageNotFoundError):
            self.messages.get_message_info(TestMessages.Command)
    
    def test_get_type_by_message_info_existing_message_info_returns_correct_type(self):
        """Test getting type by existing MessageInfo returns correct type."""
        # Arrange
        self.messages.add(TestMessages.Event)
        message_info_obj = MessageInfo(MessageType.EVENT, "polybus", "polybus-event", 2, 1, 3)
        
        # Act
        result = self.messages.get_type_by_message_info(message_info_obj)
        
        # Assert
        assert result == TestMessages.Event
    
    def test_get_type_by_message_info_non_existent_message_info_throws_error(self):
        """Test getting type by non-existent MessageInfo throws error."""
        # Arrange
        message_info_obj = MessageInfo(MessageType.COMMAND, "unknown", "unknown-command", 1, 0, 0)
        
        # Act & Assert
        with pytest.raises(PolyBusMessageNotFoundError):
            self.messages.get_type_by_message_info(message_info_obj)
    
    def test_get_type_by_message_info_different_minor_patch_versions_returns_type(self):
        """Test getting type by MessageInfo with different minor/patch versions returns type."""
        # Arrange
        self.messages.add(TestMessages.Event)  # Has version 2.1.3
        message_info_different_minor = MessageInfo(MessageType.EVENT, "polybus", "polybus-event", 2, 5, 3)
        message_info_different_patch = MessageInfo(MessageType.EVENT, "polybus", "polybus-event", 2, 1, 9)
        
        # Act
        result1 = self.messages.get_type_by_message_info(message_info_different_minor)
        result2 = self.messages.get_type_by_message_info(message_info_different_patch)
        
        # Assert
        assert result1 == TestMessages.Event
        assert result2 == TestMessages.Event
    
    def test_get_type_by_message_info_different_major_version_throws_error(self):
        """Test getting type by MessageInfo with different major version throws error."""
        # Arrange
        self.messages.add(TestMessages.Event)  # Has version 2.1.3
        message_info_different_major = MessageInfo(MessageType.EVENT, "polybus", "polybus-event", 3, 1, 3)
        
        # Act & Assert
        with pytest.raises(PolyBusMessageNotFoundError):
            self.messages.get_type_by_message_info(message_info_different_major)
    
    def test_add_same_type_twice_throws_error(self):
        """Test adding the same type twice throws error."""
        # Arrange
        self.messages.add(TestMessages.Command)
        
        # Act & Assert
        with pytest.raises(PolyBusMessageNotFoundError):
            self.messages.add(TestMessages.Command)
    
    def test_get_header_by_message_info_existing_message_info_returns_correct_header(self):
        """Test getting header by existing MessageInfo returns correct header."""
        # Arrange
        self.messages.add(TestMessages.Command)
        message_info_obj = MessageInfo(MessageType.COMMAND, "polybus", "polybus-command", 1, 0, 0)
        
        # Act
        result = self.messages.get_header_by_message_info(message_info_obj)
        
        # Assert
        assert result is not None
        assert result != ""
        assert result == message_info_obj.to_string(True)
    
    def test_get_header_by_message_info_non_existent_message_info_throws_error(self):
        """Test getting header by non-existent MessageInfo throws error."""
        # Arrange
        message_info_obj = MessageInfo(MessageType.COMMAND, "unknown", "unknown-command", 1, 0, 0)
        
        # Act & Assert
        with pytest.raises(PolyBusMessageNotFoundError):
            self.messages.get_header_by_message_info(message_info_obj)
    
    def test_get_header_by_message_info_different_major_version_throws_error(self):
        """Test getting header by MessageInfo with different major version throws error."""
        # Arrange
        self.messages.add(TestMessages.Event)  # Has version 2.1.3
        message_info_different_major = MessageInfo(MessageType.EVENT, "polybus", "polybus-event", 3, 1, 3)
        
        # Act & Assert
        with pytest.raises(PolyBusMessageNotFoundError):
            self.messages.get_header_by_message_info(message_info_different_major)
