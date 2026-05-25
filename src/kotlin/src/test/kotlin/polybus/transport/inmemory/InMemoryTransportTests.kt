package polybus.transport.inmemory

import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.fail
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import polybus.transport.PolyBusNotStartedError
import java.time.Instant

class InMemoryTransportTests {
    private lateinit var testEnvironment: TestEnvironment

    @BeforeEach
    fun setUp() = runBlocking {
        testEnvironment = TestEnvironment()
        testEnvironment.setup()
    }

    @AfterEach
    fun tearDown() = runBlocking {
        testEnvironment.stop()
    }

    @Test
    fun sendBeforeStarting() = runBlocking {
        // Arrange
        val transaction = testEnvironment.beta.bus.createOutgoingTransaction()
        val called = CompletableDeferred<Boolean>()
        testEnvironment.alpha.onMessageReceived = { called.complete(true) }

        // Act
        transaction.add(AlphaCommand().apply { name = "Test" })

        // Assert - should throw an error because the transport is not started
        try {
            transaction.commit()
            fail("Expected PolyBusNotStartedError to be thrown")
        } catch (e: PolyBusNotStartedError) {
            // Expected - exception was thrown as expected
        }
        assertFalse(called.isCompleted)
    }

    @Test
    fun sendAfterStarted() = runBlocking {
        // Arrange
        val transaction = testEnvironment.beta.bus.createOutgoingTransaction()
        val called = CompletableDeferred<Boolean>()
        testEnvironment.alpha.onMessageReceived = { called.complete(true) }

        // Act - send a command from the beta endpoint to alpha endpoint
        testEnvironment.start()
        transaction.add(AlphaCommand().apply { name = "Test" })
        transaction.commit()

        // Assert
        assertTrue(called.await())
    }

    @Test
    fun sendWithExplicitEndpoint() = runBlocking {
        // Arrange
        val transaction = testEnvironment.alpha.bus.createOutgoingTransaction()
        val result = CompletableDeferred<String>()
        testEnvironment.alpha.onMessageReceived = {
            // This should NOT be called
            result.complete(it.bus.name)
        }
        testEnvironment.alpha.transport.deadLetterHandler = {
            // This should be called
            result.complete(testEnvironment.alpha.transport.deadLetterEndpoint)
        }
        val endpoint = testEnvironment.alpha.transport.deadLetterEndpoint

        // Act - send the alpha command to dead letter endpoint
        testEnvironment.start()
        transaction.add(AlphaCommand().apply { name = "Test" }, endpoint = endpoint)
        transaction.commit()

        // Assert
        assertEquals(endpoint, result.await())
    }

    @Test
    fun sendWithHeaders() = runBlocking {
        // Arrange
        val key = "X-Custom-Header"
        val value = "HeaderValue"
        val transaction = testEnvironment.alpha.bus.createOutgoingTransaction()
        val result = CompletableDeferred<String>()
        testEnvironment.alpha.onMessageReceived = {
            result.complete(it.incomingMessage.headers[key].orEmpty())
        }

        // Act - send a command with a custom header
        testEnvironment.start()
        val message = transaction.add(AlphaCommand().apply { name = "Test" })
        message.headers[key] = value
        transaction.commit()

        // Assert
        assertEquals(value, result.await())
    }

    @Test
    fun sendWithDelay() = runBlocking {
        // Arrange
        val delayMs = 5000L // 5 seconds
        val transaction = testEnvironment.alpha.bus.createOutgoingTransaction()
        val result = CompletableDeferred<Long>()
        var startedAt = 0L
        testEnvironment.alpha.onMessageReceived = {
            result.complete(System.currentTimeMillis() - startedAt)
        }

        // Act - send to the dead letters queue instead of normal processing queue
        testEnvironment.start()
        val message = transaction.add(AlphaCommand().apply { name = "Test" })
        message.deliverAt = Instant.now().plusMillis(delayMs)
        startedAt = System.currentTimeMillis()
        transaction.commit()
        val elapsedMs = result.await()

        // Assert - allow 1 second of leeway
        assertTrue(elapsedMs in (delayMs - 1000)..(delayMs + 1000))
    }

    @Test
    fun sendWithExpiredDelay() = runBlocking {
        // Arrange
        val transaction = testEnvironment.alpha.bus.createOutgoingTransaction()
        val called = CompletableDeferred<Boolean>()
        testEnvironment.alpha.onMessageReceived = {
            called.complete(true)
        }

        // Act - schedule command to be delivered in the past
        testEnvironment.start()
        val message = transaction.add(AlphaCommand().apply { name = "Test" })
        message.deliverAt = Instant.now().minusMillis(1000) // 1 second in the past
        transaction.commit()

        // Assert
        assertTrue(called.await())
    }

    @Test
    fun startWhenAlreadyStarted() = runBlocking {
        // Act
        testEnvironment.start()

        // Assert - starting again should not throw an error
        testEnvironment.start()
    }

    @Test
    fun subscribeBeforeStarted() = runBlocking {
        // Arrange
        val transaction = testEnvironment.alpha.bus.createOutgoingTransaction()
        val called = CompletableDeferred<Boolean>()
        testEnvironment.beta.onMessageReceived = { called.complete(true) }

        // Act + Assert - subscribing and sending before starting should throw
        try {
            testEnvironment.beta.transport.subscribe(
                testEnvironment.beta.bus.messages.getMessageInfo(AlphaEvent::class.java)
            )
            fail("Expected PolyBusNotStartedError to be thrown")
        } catch (e: PolyBusNotStartedError) {
            // Expected - exception was thrown as expected
        }
        transaction.add(AlphaEvent().apply { name = "Test" })
        try {
            transaction.commit()
            fail("Expected PolyBusNotStartedError to be thrown")
        } catch (e: PolyBusNotStartedError) {
            // Expected - exception was thrown as expected
        }

        // Assert
        assertFalse(called.isCompleted)
    }

    @Test
    fun subscribe() = runBlocking {
        // Arrange
        val transaction = testEnvironment.alpha.bus.createOutgoingTransaction()
        val called = CompletableDeferred<Boolean>()
        testEnvironment.beta.onMessageReceived = { called.complete(true) }

        // Act - subscribing before starting should throw an error
        testEnvironment.start()
        testEnvironment.beta.transport.subscribe(
            testEnvironment.beta.bus.messages.getMessageInfo(AlphaEvent::class.java)
        )
        transaction.add(AlphaEvent().apply { name = "Test" })
        transaction.commit()
        assertTrue(called.await())
    }
}
