package polybus.transport.inmemory

import polybus.IPolyBus
import polybus.PolyBusBuilder
import polybus.transport.ITransport
import polybus.transport.transactions.Transaction
import polybus.transport.transactions.messages.IncomingMessage
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.time.Duration
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger
import java.util.logging.Level
import java.util.logging.Logger

open class InMemoryMessageBroker {
    val endpoints: ConcurrentHashMap<String, InMemoryEndpoint> = ConcurrentHashMap()
    var log: Logger = Logger.getLogger(InMemoryMessageBroker::class.java.name)

    private val _scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private val _activeSends = AtomicInteger(0)
    private val _jobs: ConcurrentHashMap.KeySetView<kotlinx.coroutines.Job, Boolean> = ConcurrentHashMap.newKeySet()

    open suspend fun addEndpoint(builder: PolyBusBuilder, bus: IPolyBus): ITransport {
        val endpoint = InMemoryEndpoint(this, bus)
        endpoints[bus.name] = endpoint
        return endpoint
    }

    open fun send(transaction: Transaction) {
        if (transaction.outgoingMessages.isEmpty()) {
            return
        }

        val job = _scope.launch {
            _activeSends.incrementAndGet()
            try {
                val now = Instant.now()
                transaction.outgoingMessages.forEach { message ->
                    endpoints.values.forEach { endpoint ->
                        val isDeadLetter = endpoint.deadLetterEndpoint == message.endpoint
                        val shouldSend = isDeadLetter ||
                            endpoint.bus.name == message.endpoint ||
                            (message.endpoint == null &&
                                (message.messageInfo.endpoint == endpoint.bus.name ||
                                    endpoint.isSubscribed(message.messageInfo)))

                        if (!shouldSend) {
                            return@forEach
                        }

                        val incomingMessage = IncomingMessage(endpoint.bus, message.body, message.messageInfo)
                        incomingMessage.headers = message.headers.toMutableMap()

                        val deliverAt = message.deliverAt
                        if (deliverAt != null) {
                            val wait = Duration.between(now, deliverAt)
                            if (!wait.isNegative && !wait.isZero) {
                                delayedSend(endpoint, incomingMessage, wait, isDeadLetter)
                                return@forEach
                            }
                        }

                        endpoint.handleMessage(incomingMessage, isDeadLetter)
                    }
                }
            } catch (error: Throwable) {
                log.log(Level.SEVERE, error.message, error)
            } finally {
                _activeSends.decrementAndGet()
            }
        }

        _jobs.add(job)
        job.invokeOnCompletion { _jobs.remove(job) }
    }

    private fun delayedSend(
        endpoint: InMemoryEndpoint,
        message: IncomingMessage,
        delayBy: Duration,
        isDeadLetter: Boolean
    ) {
        val job = _scope.launch {
            try {
                delay(delayBy.toMillis())
                endpoint.handleMessage(message, isDeadLetter)
            } catch (_: CancellationException) {
            } catch (error: Throwable) {
                log.log(Level.SEVERE, error.message, error)
            }
        }

        _jobs.add(job)
        job.invokeOnCompletion { _jobs.remove(job) }
    }

    open suspend fun stop() {
        endpoints.values.forEach { it.stop() }
        _jobs.forEach { it.cancel() }
        _jobs.toList().forEach { it.join() }
        while (_activeSends.get() > 0) {
            delay(10)
        }
    }
}
