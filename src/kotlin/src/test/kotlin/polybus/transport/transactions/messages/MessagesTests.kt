package polybus.transport.transactions.messages

import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class MessagesTests {
    private lateinit var messages: Messages

    @BeforeEach
    fun setUp() {
        messages = Messages()
    }

    @Test
    fun addValidMessageTypeReturnsMessageInfo() {
        // Act
        val result = messages.add(Command::class.java)

        // Assert
        assertNotNull(result)
        assertEquals(MessageType.COMMAND, result.type)
        assertEquals("polybus", result.endpoint)
        assertEquals("polybus-command", result.name)
        assertEquals(1, result.major)
        assertEquals(0, result.minor)
        assertEquals(0, result.patch)
    }

    @Test
    fun addMessageTypeWithoutAttributeThrowsError() {
        // Act & Assert
        assertThrows<PolyBusMessageNotFoundError> { messages.add(MessageWithoutAttribute::class.java) }
    }

    @Test
    fun getMessageInfoExistingTypeReturnsCorrectMessageInfo() {
        // Arrange
        messages.add(Command::class.java)

        // Act
        val result = messages.getMessageInfo(Command::class.java)

        // Assert
        assertNotNull(result)
        assertEquals(MessageType.COMMAND, result.type)
        assertEquals("polybus", result.endpoint)
        assertEquals("polybus-command", result.name)
    }

    @Test
    fun getMessageInfoNonExistentTypeThrowsError() {
        // Act & Assert
        assertThrows<PolyBusMessageNotFoundError> { messages.getMessageInfo(Command::class.java) }
    }

    @Test
    fun getTypeByMessageInfoExistingMessageInfoReturnsCorrectType() {
        // Arrange
        messages.add(Event::class.java)
        val messageInfo = MessageInfoValue(MessageType.EVENT, "polybus", "polybus-event", 2, 1, 3)

        // Act
        val result = messages.getTypeByMessageInfo(messageInfo)

        // Assert
        assertEquals(Event::class.java, result)
    }

    @Test
    fun getTypeByMessageInfoNonExistentMessageInfoThrowsError() {
        // Arrange
        val messageInfo = MessageInfoValue(MessageType.COMMAND, "unknown", "unknown-command", 1, 0, 0)

        // Act & Assert
        assertThrows<PolyBusMessageNotFoundError> { messages.getTypeByMessageInfo(messageInfo) }
    }

    @Test
    fun getTypeByMessageInfoDifferentMinorPatchVersionsReturnsType() {
        // Arrange
        messages.add(Event::class.java) // Has version 2.1.3
        val messageInfoDifferentMinor = MessageInfoValue(MessageType.EVENT, "polybus", "polybus-event", 2, 5, 3)
        val messageInfoDifferentPatch = MessageInfoValue(MessageType.EVENT, "polybus", "polybus-event", 2, 1, 9)

        // Act
        val result1 = messages.getTypeByMessageInfo(messageInfoDifferentMinor)
        val result2 = messages.getTypeByMessageInfo(messageInfoDifferentPatch)

        // Assert
        assertEquals(Event::class.java, result1)
        assertEquals(Event::class.java, result2)
    }

    @Test
    fun getTypeByMessageInfoDifferentMajorVersionThrowsError() {
        // Arrange
        messages.add(Event::class.java) // Has version 2.1.3
        val messageInfoDifferentMajor = MessageInfoValue(MessageType.EVENT, "polybus", "polybus-event", 3, 1, 3)

        // Act & Assert
        assertThrows<PolyBusMessageNotFoundError> { messages.getTypeByMessageInfo(messageInfoDifferentMajor) }
    }

    @Test
    fun addSameTypeTwiceThrowsError() {
        // Arrange
        messages.add(Command::class.java)

        // Act & Assert
        assertThrows<PolyBusMessageNotFoundError> { messages.add(Command::class.java) }
    }

    @Test
    fun getHeaderByMessageInfoExistingMessageInfoReturnsCorrectHeader() {
        // Arrange
        messages.add(Command::class.java)
        val messageInfo = MessageInfoValue(MessageType.COMMAND, "polybus", "polybus-command", 1, 0, 0)

        // Act
        val result = messages.getHeaderByMessageInfo(messageInfo)

        // Assert
        assertNotNull(result)
        assertFalse(result.isEmpty())
        assertEquals(messageInfo.toHeaderString(true), result)
    }

    @Test
    fun getHeaderByMessageInfoNonExistentMessageInfoThrowsError() {
        // Arrange
        val messageInfo = MessageInfoValue(MessageType.COMMAND, "unknown", "unknown-command", 1, 0, 0)

        // Act & Assert
        assertThrows<PolyBusMessageNotFoundError> { messages.getHeaderByMessageInfo(messageInfo) }
    }

    @Test
    fun getHeaderByMessageInfoDifferentMajorVersionThrowsError() {
        // Arrange
        messages.add(Event::class.java) // Has version 2.1.3
        val messageInfoDifferentMajor = MessageInfoValue(MessageType.EVENT, "polybus", "polybus-event", 3, 1, 3)

        // Act & Assert
        assertThrows<PolyBusMessageNotFoundError> { messages.getHeaderByMessageInfo(messageInfoDifferentMajor) }
    }
}
