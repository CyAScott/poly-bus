using System.Collections.Concurrent;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport.InMemory;

/// <summary>
/// A message broker that uses in-memory transport for message passing.
/// </summary>
public class InMemoryMessageBroker
{
    /// <summary>
    /// The collection of in-memory endpoints managed by this broker.
    /// </summary>
    public ConcurrentDictionary<string, InMemoryEndpoint> Endpoints { get; } = new();

    /// <summary>
    /// The logger for the InMemoryMessageBroker.
    /// </summary>
    public ILogger<InMemoryMessageBroker> Log { get; set; } = NullLogger<InMemoryMessageBroker>.Instance;

    /// <summary>
    /// The ITransport factory method.
    /// </summary>
    public Task<ITransport> AddEndpoint(PolyBusBuilder builder, IPolyBus bus)
    {
        var endpoint = new InMemoryEndpoint(this, bus);
        Endpoints[bus.Name] = endpoint;
        return Task.FromResult<ITransport>(endpoint);
    }

    /// <summary>
    /// Processes the transaction and distributes outgoing messages to the appropriate endpoints.
    /// </summary>
    public async void Send(Transaction transaction)
    {
        if (transaction.OutgoingMessages.Count == 0)
        {
            return;
        }

        try
        {
            await Task.Yield();

            if (Interlocked.Increment(ref _count) == 1)
            {
                while (_emptySignal.CurrentCount > 0)
                {
                    await _emptySignal.WaitAsync(0);
                }
            }

            var tasks = new List<Task>();
            var now = DateTime.UtcNow;

            foreach (var message in transaction.OutgoingMessages)
            {
                foreach (var endpoint in Endpoints.Values)
                {
                    var isDeadLetter = endpoint.DeadLetterEndpoint == message.Endpoint;
                    if (isDeadLetter
                        || endpoint.Bus.Name == message.Endpoint
                        || (message.Endpoint == null
                            && (message.MessageInfo.Endpoint == endpoint.Bus.Name
                                || endpoint.IsSubscribed(message.MessageInfo))))
                    {
                        var incomingMessage = new IncomingMessage(endpoint.Bus, message.Body, message.MessageInfo)
                        {
                            Headers = new Dictionary<string, string>(message.Headers)
                        };
                        if (message.DeliverAt != null)
                        {
                            var wait = message.DeliverAt.Value - now;
                            if (wait > TimeSpan.Zero)
                            {
                                DelayedSend(endpoint, incomingMessage, wait, isDeadLetter);
                                continue;
                            }
                        }

                        var task = endpoint.HandleMessage(incomingMessage, isDeadLetter);
                        tasks.Add(task);
                    }
                }
            }

            await Task.WhenAll(tasks);
        }
        catch (Exception error)
        {
            Log.LogError(error, error.Message);
        }
        finally
        {
            if (Interlocked.Decrement(ref _count) == 0)
            {
                _emptySignal.Release();
            }
        }
    }
    async void DelayedSend(InMemoryEndpoint endpoint, IncomingMessage message, TimeSpan delay, bool isDeadLetter)
    {
        try
        {
            await Task.Delay(delay, _cts.Token);
            await endpoint.HandleMessage(message, isDeadLetter);
        }
        catch (OperationCanceledException)
        {
            // Ignore cancellation
        }
        catch (Exception error)
        {
            Log.LogError(error, error.Message);
        }
    }

    /// <summary>
    /// Stops all endpoints and waits for in-flight messages to be processed.
    /// </summary>
    public async Task Stop()
    {
        foreach (var endpoint in Endpoints.Values)
        {
            await endpoint.Stop();
        }
        _cts.Cancel();
        if (Volatile.Read(ref _count) > 0)
        {
            await _emptySignal.WaitAsync();
        }
    }
    int _count;
    readonly CancellationTokenSource _cts = new();
    readonly SemaphoreSlim _emptySignal = new(0, 1);
}
