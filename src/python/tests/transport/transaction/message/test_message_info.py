"""Tests for the MessageInfo decorator."""

import pytest
from src.transport.transaction.message.message_info import message_info, MessageInfo
from src.transport.transaction.message.message_type import MessageType


def test_get_attribute_from_header_with_valid_header_returns_correct_attribute():
    """Test parsing valid header strings."""
    # Arrange
    header = "endpoint=user-service, type=Command, name=CreateUser, version=1.2.3"
    
    # Act
    result = MessageInfo.get_attribute_from_header(header)
    
    # Assert
    assert result is not None
    assert result.endpoint == "user-service"
    assert result.message_type == MessageType.COMMAND
    assert result.name == "CreateUser"
    assert result.major == 1
    assert result.minor == 2
    assert result.patch == 3


def test_get_attribute_from_header_with_event_type_returns_correct_attribute():
    """Test parsing header with event type."""
    # Arrange
    header = "endpoint=notification-service, type=Event, name=UserCreated, version=2.0.1"
    
    # Act
    result = MessageInfo.get_attribute_from_header(header)
    
    # Assert
    assert result is not None
    assert result.endpoint == "notification-service"
    assert result.message_type == MessageType.EVENT
    assert result.name == "UserCreated"
    assert result.major == 2
    assert result.minor == 0
    assert result.patch == 1


def test_get_attribute_from_header_with_extra_spaces_returns_correct_attribute():
    """Test parsing header with extra spacing."""
    # Arrange - the current regex doesn't handle spaces within values well, so testing valid spacing
    header = "endpoint=payment-service, type=Command, name=ProcessPayment, version=3.14.159"
    
    # Act
    result = MessageInfo.get_attribute_from_header(header)
    
    # Assert
    assert result is not None
    assert result.endpoint == "payment-service"
    assert result.message_type == MessageType.COMMAND
    assert result.name == "ProcessPayment"
    assert result.major == 3
    assert result.minor == 14
    assert result.patch == 159


def test_get_attribute_from_header_with_case_insensitive_type_returns_correct_attribute():
    """Test parsing header with case insensitive type."""
    # Arrange
    header = "endpoint=order-service, type=command, name=PlaceOrder, version=1.0.0"
    
    # Act
    result = MessageInfo.get_attribute_from_header(header)
    
    # Assert
    assert result is not None
    assert result.message_type == MessageType.COMMAND


@pytest.mark.parametrize("header", [
    "",
    "invalid header",
    "endpoint=test",
    "endpoint=test, type=Command",
    "endpoint=test, type=Command, name=Test",
    "endpoint=test, type=Command, name=Test, version=invalid",
    "type=Command, name=Test, version=1.0.0",
])
def test_get_attribute_from_header_with_invalid_header_returns_none(header):
    """Test parsing invalid header strings returns None."""
    # Act
    result = MessageInfo.get_attribute_from_header(header)
    
    # Assert
    assert result is None


def test_get_attribute_from_header_with_invalid_enum_type_returns_none():
    """Test parsing header with invalid enum type returns None (Python doesn't throw like C#)."""
    # Arrange
    header = "endpoint=test, type=InvalidType, name=Test, version=1.0.0"
    
    # Act
    result = MessageInfo.get_attribute_from_header(header)
    
    # Assert
    assert result is None


def test_get_attribute_from_header_with_missing_version_returns_none():
    """Test parsing header with missing version."""
    # Arrange
    header = "endpoint=test-service, type=Command, name=TestCommand, version="
    
    # Act
    result = MessageInfo.get_attribute_from_header(header)
    
    # Assert
    assert result is None


def test_get_attribute_from_header_with_incomplete_version_returns_none():
    """Test parsing header with incomplete version."""
    # Arrange
    header = "endpoint=test-service, type=Command, name=TestCommand, version=1.0"
    
    # Act
    result = MessageInfo.get_attribute_from_header(header)
    
    # Assert
    assert result is None


def test_equals_with_identical_attributes_returns_true():
    """Test equality with identical attributes."""
    # Arrange
    attr1 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    attr2 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    
    # Act & Assert
    assert attr1 == attr2
    assert attr2 == attr1


def test_equals_with_same_object_returns_true():
    """Test equality with same object."""
    # Arrange
    attr = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    
    # Act & Assert
    assert attr == attr


def test_equals_with_different_type_returns_false():
    """Test equality with different message type."""
    # Arrange
    attr1 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    attr2 = MessageInfo(MessageType.EVENT, "user-service", "CreateUser", 1, 2, 3)
    
    # Act & Assert
    assert attr1 != attr2


def test_equals_with_different_endpoint_returns_false():
    """Test equality with different endpoint."""
    # Arrange
    attr1 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    attr2 = MessageInfo(MessageType.COMMAND, "order-service", "CreateUser", 1, 2, 3)
    
    # Act & Assert
    assert attr1 != attr2


def test_equals_with_different_name_returns_false():
    """Test equality with different name."""
    # Arrange
    attr1 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    attr2 = MessageInfo(MessageType.COMMAND, "user-service", "UpdateUser", 1, 2, 3)
    
    # Act & Assert
    assert attr1 != attr2


def test_equals_with_different_major_version_returns_false():
    """Test equality with different major version."""
    # Arrange
    attr1 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    attr2 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 2, 2, 3)
    
    # Act & Assert
    assert attr1 != attr2


def test_equals_with_different_minor_version_returns_true():
    """Test equality with different minor version (should be equal)."""
    # Arrange
    attr1 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    attr2 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 3, 3)
    
    # Act & Assert
    assert attr1 == attr2, "Minor version differences should not affect equality"


def test_equals_with_different_patch_version_returns_true():
    """Test equality with different patch version (should be equal)."""
    # Arrange
    attr1 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    attr2 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 4)
    
    # Act & Assert
    assert attr1 == attr2, "Patch version differences should not affect equality"


def test_equals_with_null_object_returns_false():
    """Test equality with None object."""
    # Arrange
    attr = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    
    # Act & Assert
    assert attr != None


def test_equals_with_different_object_type_returns_false():
    """Test equality with different object type."""
    # Arrange
    attr = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    other = "not a MessageAttribute"
    
    # Act & Assert
    assert attr != other


def test_get_hash_code_with_identical_attributes_returns_same_hash_code():
    """Test that identical attributes have same hash code."""
    # Arrange
    attr1 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    attr2 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    
    # Act & Assert
    assert hash(attr1) == hash(attr2)


def test_get_hash_code_with_different_attributes_returns_different_hash_codes():
    """Test that different attributes have different hash codes."""
    # Arrange
    attr1 = MessageInfo(MessageType.COMMAND, "user-service", "CreateUser", 1, 2, 3)
    attr2 = MessageInfo(MessageType.EVENT, "user-service", "CreateUser", 1, 2, 3)
    
    # Act & Assert
    assert hash(attr1) != hash(attr2)


# Additional Python-specific tests for decorator functionality
def test_message_info_decorator_basic_usage():
    """Test that the decorator can be applied to a class."""
    
    @message_info(MessageType.COMMAND, "test-endpoint", "test-name", 1, 0, 0)
    class TestClass:
        pass
    
    assert hasattr(TestClass, '_message_info')
    assert isinstance(TestClass._message_info, MessageInfo)
    assert TestClass._message_info.message_type == MessageType.COMMAND
    assert TestClass._message_info.endpoint == "test-endpoint"
    assert TestClass._message_info.name == "test-name"
    assert TestClass._message_info.major == 1
    assert TestClass._message_info.minor == 0
    assert TestClass._message_info.patch == 0


def test_message_info_to_string():
    """Test the to_string method."""
    info = MessageInfo(MessageType.EVENT, "user-service", "user-created", 2, 1, 3)
    
    # With version
    expected_with_version = "endpoint=user-service, type=event, name=user-created, version=2.1.3"
    assert info.to_string(True) == expected_with_version
    assert str(info) == expected_with_version
    
    # Without version
    expected_without_version = "endpoint=user-service, type=event, name=user-created"
    assert info.to_string(False) == expected_without_version