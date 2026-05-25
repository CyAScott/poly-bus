package polybus.transport.transactions.messages.handlers.error

import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import polybus.transport.transactions.IncomingTransaction
import polybus.transport.transactions.messages.IncomingMessage
import polybus.transport.transactions.messages.handlers.error.ErrorHandler
import java.time.Instant
import java.time.temporal.ChronoUnit

class ErrorHandlerTests {
    private lateinit var testBus: TestBus
    private lateinit var transaction: IncomingTransaction
    private lateinit var errorHandler: TestableErrorHandler

    @BeforeEach
    fun setUp() {
        testBus = TestBus("TestBus")
        testBus.messages.add(ErrorHandlerTestMessage::class.java)
        val incomingMessage = IncomingMessage(
            bus = testBus,
            body = "{}",
            messageInfo = testBus.messages.getMessageInfo(ErrorHandlerTestMessage::class.java)
        )
        transaction = IncomingTransaction(testBus, incomingMessage)
        errorHandler = TestableErrorHandler()
    }

    @Test
    fun retrierSucceedsOnFirstAttemptDoesNotRetry() = runBlocking {
        // Arrange
        var nextCalled = false

        // Act
        errorHandler.retrier(transaction) {
            nextCalled = true
        }

        // Assert
        assertTrue(nextCalled)
        assertEquals(0, transaction.outgoingMessages.size)
    }

    @Test
    fun retrierFailsOnceRetriesImmediately() = runBlocking {
        // Arrange
        var callCount = 0

        // Act
        errorHandler.retrier(transaction) {
            callCount++
            if (callCount == 1) {
                throw RuntimeException("Test error")
            }
        }

        // Assert
        assertEquals(2, callCount)
        assertEquals(0, transaction.outgoingMessages.size)
    }

    @Test
    fun retrierFailsAllImmediateRetriesSchedulesDelayedRetry() = runBlocking {
        // Arrange
        val expectedRetryTime = Instant.now().plusSeconds(300)
        errorHandler.setNextRetryTime(expectedRetryTime)
        var callCount = 0

        // Act
        errorHandler.retrier(transaction) {
            callCount++
            throw RuntimeException("Test error")
        }

        // Assert
        assertEquals(errorHandler.immediateRetryCount, callCount)
        assertEquals(1, transaction.outgoingMessages.size)

        val delayedMessage = transaction.outgoingMessages.first()
        assertEquals(expectedRetryTime, delayedMessage.deliverAt)
        assertEquals("1", delayedMessage.headers[errorHandler.retryCountHeader])
        assertEquals("TestBus", delayedMessage.endpoint)
    }

    @Test
    fun retrierWithExistingRetryCountIncrementsCorrectly() = runBlocking {
        // Arrange
        transaction.incomingMessage.headers[errorHandler.retryCountHeader] = "2"
        val expectedRetryTime = Instant.now().plusSeconds(600)
        errorHandler.setNextRetryTime(expectedRetryTime)

        // Act
        errorHandler.retrier(transaction) {
            throw RuntimeException("Test error")
        }

        // Assert
        assertEquals(1, transaction.outgoingMessages.size)

        val delayedMessage = transaction.outgoingMessages.first()
        assertEquals("3", delayedMessage.headers[errorHandler.retryCountHeader])
        assertEquals(expectedRetryTime, delayedMessage.deliverAt)
    }

    @Test
    fun retrierExceedsMaxDelayedRetriesSendsToDeadLetter() = runBlocking {
        // Arrange
        transaction.incomingMessage.headers[errorHandler.retryCountHeader] =
            errorHandler.delayedRetryCount.toString()
        val testException = RuntimeException("Final error")

        // Act
        errorHandler.retrier(transaction) {
            throw testException
        }

        // Assert
        assertEquals(1, transaction.outgoingMessages.size)

        val deadLetterMessage = transaction.outgoingMessages.first()
        assertEquals(TestTransport.DEFAULT_DEAD_LETTER_ENDPOINT, deadLetterMessage.endpoint)
        assertEquals("Final error", deadLetterMessage.headers[errorHandler.errorMessageHeader])
        assertNotNull(deadLetterMessage.headers[errorHandler.errorStackTraceHeader])
    }

    @Test
    fun retrierClearsOutgoingMessagesOnEachRetry() = runBlocking {
        // Arrange
        var callCount = 0

        // Act
        errorHandler.retrier(transaction) {
            callCount++
            transaction.add(ErrorHandlerTestMessage())
            throw RuntimeException("Test error")
        }

        // Assert
        assertEquals(errorHandler.immediateRetryCount, callCount)
        // Should only have the delayed retry message, not the messages added in next()
        assertEquals(1, transaction.outgoingMessages.size)
        assertTrue(
            transaction.outgoingMessages.first().headers.containsKey(errorHandler.retryCountHeader)
        )
    }

    @Test
    fun retrierWithZeroImmediateRetriesSchedulesDelayedRetryImmediately() = runBlocking {
        // Arrange
        errorHandler.immediateRetryCount = 0
        val expectedRetryTime = Instant.now().plusSeconds(300)
        errorHandler.setNextRetryTime(expectedRetryTime)
        var callCount = 0

        // Act
        errorHandler.retrier(transaction) {
            callCount++
            throw RuntimeException("Test error")
        }

        // Assert
        assertEquals(1, callCount) // Should enforce minimum of 1
        assertEquals(1, transaction.outgoingMessages.size)
        assertEquals("1", transaction.outgoingMessages.first().headers[errorHandler.retryCountHeader])
    }

    @Test
    fun retrierWithZeroDelayedRetriesStillGetsMinimumOfOne() = runBlocking {
        // Arrange
        errorHandler.delayedRetryCount = 0
        val expectedRetryTime = Instant.now().plusSeconds(300)
        errorHandler.setNextRetryTime(expectedRetryTime)

        // Act
        errorHandler.retrier(transaction) {
            throw RuntimeException("Test error")
        }

        // Assert
        assertEquals(1, transaction.outgoingMessages.size)
        assertEquals("1", transaction.outgoingMessages.first().headers[errorHandler.retryCountHeader])
        assertEquals(expectedRetryTime, transaction.outgoingMessages.first().deliverAt)
    }

    @Test
    fun getNextRetryTimeDefaultImplementationUsesDelayCorrectly() {
        // Arrange
        val handler = ErrorHandler().apply { delayIncrement = 60 }
        val beforeTime = Instant.now()

        // Act
        val result1 = handler.getNextRetryTime(1)
        val result2 = handler.getNextRetryTime(2)
        val result3 = handler.getNextRetryTime(3)

        val afterTime = Instant.now()

        // Assert
        assertTrue(result1 >= beforeTime.plus(60, ChronoUnit.SECONDS))
        assertTrue(result1 <= afterTime.plus(60, ChronoUnit.SECONDS))

        assertTrue(result2 >= beforeTime.plus(120, ChronoUnit.SECONDS))
        assertTrue(result2 <= afterTime.plus(120, ChronoUnit.SECONDS))

        assertTrue(result3 >= beforeTime.plus(180, ChronoUnit.SECONDS))
        assertTrue(result3 <= afterTime.plus(180, ChronoUnit.SECONDS))
    }

    @Test
    fun retrierSucceedsAfterSomeImmediateRetriesStopsRetrying() = runBlocking {
        // Arrange
        var callCount = 0

        // Act
        errorHandler.retrier(transaction) {
            callCount++
            if (callCount < 3) {
                throw RuntimeException("Test error")
            }
        }

        // Assert
        assertEquals(3, callCount)
        assertEquals(0, transaction.outgoingMessages.size)
    }

    @Test
    fun retrierInvalidRetryCountHeaderTreatsAsZero() = runBlocking {
        // Arrange
        transaction.incomingMessage.headers[errorHandler.retryCountHeader] = "invalid"
        val expectedRetryTime = Instant.now().plusSeconds(300)
        errorHandler.setNextRetryTime(expectedRetryTime)

        // Act
        errorHandler.retrier(transaction) {
            throw RuntimeException("Test error")
        }

        // Assert
        assertEquals(1, transaction.outgoingMessages.size)
        val delayedMessage = transaction.outgoingMessages.first()
        assertEquals("1", delayedMessage.headers[errorHandler.retryCountHeader])
    }

    @Test
    fun retrierExceptionStackTraceIsStoredInHeader() = runBlocking {
        // Arrange
        transaction.incomingMessage.headers[errorHandler.retryCountHeader] =
            errorHandler.delayedRetryCount.toString()

        val exceptionWithStackTrace = RuntimeException("Error with stack trace")

        // Act
        errorHandler.retrier(transaction) {
            throw exceptionWithStackTrace
        }

        // Assert
        assertEquals(1, transaction.outgoingMessages.size)
        val deadLetterMessage = transaction.outgoingMessages.first()
        val storedStackTrace = deadLetterMessage.headers[errorHandler.errorStackTraceHeader]
        assertNotNull(storedStackTrace)
        assertFalse(storedStackTrace.isNullOrEmpty())
    }

    @Test
    fun retrierExceptionWithNullStackTraceUsesEmptyString() = runBlocking {
        // Arrange
        transaction.incomingMessage.headers[errorHandler.retryCountHeader] =
            errorHandler.delayedRetryCount.toString()

        // Create an exception with null StackTrace using custom exception
        val exceptionWithoutStackTrace = RuntimeException("Error without stack trace")
        exceptionWithoutStackTrace.stackTrace = emptyArray()

        // Act
        errorHandler.retrier(transaction) {
            throw exceptionWithoutStackTrace
        }

        // Assert
        assertEquals(1, transaction.outgoingMessages.size)
        val deadLetterMessage = transaction.outgoingMessages.first()
        assertEquals("", deadLetterMessage.headers[errorHandler.errorStackTraceHeader])
    }

    private class TestableErrorHandler : ErrorHandler() {
        private var _nextRetryTime: Instant? = null

        fun setNextRetryTime(retryTime: Instant) {
            _nextRetryTime = retryTime
        }

        override fun getNextRetryTime(attempt: Int): Instant {
            return _nextRetryTime ?: super.getNextRetryTime(attempt)
        }
    }
}
