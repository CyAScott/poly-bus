package polybus.transport.transactions.messages.handlers.error

import polybus.transport.transactions.IncomingTransaction
import polybus.transport.transactions.messages.OutgoingMessage
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.logging.Level
import java.util.logging.Logger

open class ErrorHandler {
    open var log: Logger = Logger.getLogger(ErrorHandler::class.java.name)
    open var delayIncrement: Int = 30
    open var delayedRetryCount: Int = 3
    open var immediateRetryCount: Int = 3
    open var errorMessageHeader: String = "x-error-message"
    open var errorStackTraceHeader: String = "x-error-stack-trace"
    open var retryCountHeader: String = "x-retry-count"

    open suspend fun retrier(transaction: IncomingTransaction, next: suspend () -> Unit) {
        var delayedAttempt = transaction.incomingMessage.headers[retryCountHeader]?.toIntOrNull() ?: 0
        val delayedRetries = maxOf(1, delayedRetryCount)
        val immediateRetries = maxOf(1, immediateRetryCount)

        for (immediateAttempt in 0 until immediateRetries) {
            try {
                next()
                break
            } catch (error: Throwable) {
                log.log(
                    Level.SEVERE,
                    "Error processing message ${transaction.incomingMessage.messageInfo} (immediate attempts: $immediateAttempt, delayed attempts: $delayedAttempt): ${error.message}",
                    error
                )

                transaction.outgoingMessages.clear()

                if (immediateAttempt < immediateRetries - 1) {
                    continue
                }

                if (transaction.incomingMessage.bus.transport.supportsDelayedCommands && delayedAttempt < delayedRetries) {
                    delayedAttempt += 1
                    val delayedMessage = OutgoingMessage(
                        transaction.bus,
                        transaction.incomingMessage.message,
                        transaction.bus.name,
                        transaction.incomingMessage.messageInfo
                    )
                    delayedMessage.deliverAt = getNextRetryTime(delayedAttempt)
                    delayedMessage.headers = transaction.incomingMessage.headers.toMutableMap()
                    delayedMessage.headers[retryCountHeader] = delayedAttempt.toString()
                    transaction.outgoingMessages.add(delayedMessage)
                    continue
                }

                val deadLetterMessage = OutgoingMessage(
                    transaction.bus,
                    transaction.incomingMessage.message,
                    transaction.bus.transport.deadLetterEndpoint,
                    transaction.incomingMessage.messageInfo
                )
                deadLetterMessage.headers = transaction.incomingMessage.headers.toMutableMap()
                deadLetterMessage.headers[errorMessageHeader] = error.message.orEmpty()
                deadLetterMessage.headers[errorStackTraceHeader] =
                    if (error.stackTrace.isEmpty()) "" else error.stackTraceToString()
                transaction.outgoingMessages.add(deadLetterMessage)
            }
        }
    }

    open fun getNextRetryTime(attempt: Int): Instant =
        Instant.now().plus((attempt * delayIncrement).toLong(), ChronoUnit.SECONDS)
}
