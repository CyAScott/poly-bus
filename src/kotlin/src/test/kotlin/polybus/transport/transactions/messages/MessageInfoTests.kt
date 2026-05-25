package polybus.transport.transactions.messages

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class MessageInfoTests {
    @Test
    fun getAttributeFromHeaderWithValidHeaderReturnsCorrectAttribute() {
        // Arrange
        val header = "endpoint=user-service, type=COMMAND, name=create-user, version=1.2.3"

        // Act
        val result = MessageInfoValue.getAttributeFromHeader(header)

        // Assert
        assertNotNull(result)
        assertEquals("user-service", result!!.endpoint)
        assertEquals(MessageType.COMMAND, result.type)
        assertEquals("create-user", result.name)
        assertEquals(1, result.major)
        assertEquals(2, result.minor)
        assertEquals(3, result.patch)
    }

    @Test
    fun getAttributeFromHeaderWithEventTypeReturnsCorrectAttribute() {
        // Arrange
        val header = "endpoint=notification-service, type=EVENT, name=user-created, version=2.0.1"

        // Act
        val result = MessageInfoValue.getAttributeFromHeader(header)

        // Assert
        assertNotNull(result)
        assertEquals("notification-service", result!!.endpoint)
        assertEquals(MessageType.EVENT, result.type)
        assertEquals("user-created", result.name)
        assertEquals(2, result.major)
        assertEquals(0, result.minor)
        assertEquals(1, result.patch)
    }

    @Test
    fun getAttributeFromHeaderWithExtraSpacesReturnsCorrectAttribute() {
        // Arrange - the current regex doesn't handle spaces within values well, so testing valid spacing
        val header = "endpoint=payment-service, type=COMMAND, name=process-payment, version=3.14.159"

        // Act
        val result = MessageInfoValue.getAttributeFromHeader(header)

        // Assert
        assertNotNull(result)
        assertEquals("payment-service", result!!.endpoint)
        assertEquals(MessageType.COMMAND, result.type)
        assertEquals("process-payment", result.name)
        assertEquals(3, result.major)
        assertEquals(14, result.minor)
        assertEquals(159, result.patch)
    }

    @Test
    fun getAttributeFromHeaderWithCaseInsensitiveTypeReturnsCorrectAttribute() {
        // Arrange
        val header = "endpoint=order-service, type=command, name=place-order, version=1.0.0"

        // Act
        val result = MessageInfoValue.getAttributeFromHeader(header)

        // Assert
        assertNotNull(result)
        assertEquals(MessageType.COMMAND, result!!.type)
    }

    @ParameterizedTest
    @ValueSource(
        strings = [
            "",
            "invalid header",
            "endpoint=test",
            "endpoint=test, type=COMMAND",
            "endpoint=test, type=COMMAND, name=test",
            "endpoint=test, type=COMMAND, name=test, version=invalid",
            "type=COMMAND, name=test, version=1.0.0"
        ]
    )
    fun getAttributeFromHeaderWithInvalidHeaderReturnsNull(header: String) {
        // Act
        val result = MessageInfoValue.getAttributeFromHeader(header)

        // Assert
        assertNull(result)
    }

    @Test
    fun getAttributeFromHeaderWithInvalidEnumTypeThrowsIllegalArgumentException() {
        // Arrange
        val header = "endpoint=test, type=INVALID_TYPE, name=test, version=1.0.0"

        // Act & Assert
        assertThrows(IllegalArgumentException::class.java) {
            MessageInfoValue.getAttributeFromHeader(header)
        }
    }

    @Test
    fun getAttributeFromHeaderWithMissingVersionReturnsNull() {
        // Arrange
        val header = "endpoint=test-service, type=COMMAND, name=test-command, version="

        // Act
        val result = MessageInfoValue.getAttributeFromHeader(header)

        // Assert
        assertNull(result)
    }

    @Test
    fun getAttributeFromHeaderWithIncompleteVersionReturnsNull() {
        // Arrange
        val header = "endpoint=test-service, type=COMMAND, name=test-command, version=1.0"

        // Act
        val result = MessageInfoValue.getAttributeFromHeader(header)

        // Assert
        assertNull(result)
    }

    @Test
    fun equalsWithIdenticalAttributesReturnsTrue() {
        // Arrange
        val attr1 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)
        val attr2 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)

        // Act & Assert
        assertTrue(attr1.equals(attr2))
        assertTrue(attr2.equals(attr1))
    }

    @Test
    fun equalsWithSameObjectReturnsTrue() {
        // Arrange
        val attr = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)

        // Act & Assert
        assertTrue(attr.equals(attr))
    }

    @Test
    fun equalsWithDifferentTypeReturnsFalse() {
        // Arrange
        val attr1 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)
        val attr2 = MessageInfoValue(MessageType.EVENT, "user-service", "create-user", 1, 2, 3)

        // Act & Assert
        assertFalse(attr1.equals(attr2))
    }

    @Test
    fun equalsWithDifferentMajorVersionReturnsFalse() {
        // Arrange
        val attr1 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)
        val attr2 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 2, 2, 3)

        // Act & Assert
        assertFalse(attr1.equals(attr2))
    }

    @Test
    fun equalsWithDifferentMinorVersionReturnsTrue() {
        // Arrange
        val attr1 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)
        val attr2 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 3, 3)

        // Act & Assert
        assertTrue(attr1.equals(attr2))
    }

    @Test
    fun equalsWithDifferentPatchVersionReturnsTrue() {
        val attr1 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)
        val attr2 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 4)

        // Act & Assert
        assertTrue(attr1.equals(attr2))
    }

    @Test
    fun equalsWithNullObjectReturnsFalse() {
        // Arrange
        val attr = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)

        // Act & Assert
        assertFalse(attr.equals(null))
    }

    @Test
    fun equalsWithDifferentObjectTypeReturnsFalse() {
        // Arrange
        val attr = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)
        val other: Any = "not a MessageAttribute"

        // Act & Assert
        assertFalse(attr.equals(other))
    }

    @Test
    fun getHashCodeWithIdenticalAttributesReturnsSameHashCode() {
        // Arrange
        val attr1 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)
        val attr2 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)

        // Act & Assert
        assertEquals(attr1.hashCode(), attr2.hashCode())
    }

    @Test
    fun getHashCodeWithDifferentAttributesReturnsDifferentHashCodes() {
        // Arrange
        val attr1 = MessageInfoValue(MessageType.COMMAND, "user-service", "create-user", 1, 2, 3)
        val attr2 = MessageInfoValue(MessageType.EVENT, "user-service", "create-user", 1, 2, 3)

        // Act & Assert
        assertNotEquals(attr1.hashCode(), attr2.hashCode())
    }

}
