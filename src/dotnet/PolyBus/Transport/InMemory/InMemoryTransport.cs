using Microsoft.Extensions.Logging;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport.InMemory;

public class InMemoryTransport
{
    public ITransport AddEndpoint(PolyBusBuilder builder, IPolyBus bus)
    {
        var endpoint = new Endpoint(this, bus);
        _endpoints.Add(bus.Name, endpoint);
        return endpoint;
    }
    readonly Dictionary<string, Endpoint> _endpoints = [];
    class Endpoint(InMemoryTransport transport, IPolyBus bus) : ITransport
    {
        public async Task Handle(OutgoingMessage message)
        {
            if (!transport.UseSubscriptions || _subscriptions.Contains(message.MessageType))
            {
                var incomingMessage = new IncomingMessage(bus, message.Body)
                {
                    Headers = message.Headers
                };

                try
                {
                    var transaction = (IncomingTransaction)await bus.CreateTransaction(incomingMessage);

                    await transaction.Commit();
                }
                catch (Exception error)
                {
                    var logger = incomingMessage.State.Values.OfType<ILogger>().FirstOrDefault();
                    logger?.LogError(error, error.Message);
                }
            }
        }

        readonly List<Type> _subscriptions = [];
        public Task Subscribe(MessageInfo messageInfo)
        {
            var type = bus.Messages.GetTypeByMessageInfo(messageInfo)
                       ?? throw new ArgumentException($"Message type for attribute {messageInfo} is not registered.");
            _subscriptions.Add(type);
            return Task.CompletedTask;
        }

        public bool SupportsCommandMessages => true;

        public bool SupportsDelayedMessages => true;

        public bool SupportsSubscriptions => true;

        public Task Send(Transaction transaction) => transport.Send(transaction);

        public Task Start() => transport.Start();

        public Task Stop() => transport.Stop();
    }

    public async Task Send(Transaction transaction)
    {
        if (!_active)
        {
            throw new InvalidOperationException("Transport is not active.");
        }

        if (transaction.OutgoingMessages.Count == 0)
        {
            return;
        }

        if (Interlocked.Increment(ref _count) == 1)
        {
            while (_emptySignal.CurrentCount > 0)
            {
                await _emptySignal.WaitAsync(0);
            }
        }

        try
        {
            var tasks = new List<Task>();
            var now = DateTime.UtcNow;

            foreach (var message in transaction.OutgoingMessages)
            {
                if (message.DeliverAt != null)
                {
                    var wait = message.DeliverAt.Value - now;
                    if (wait > TimeSpan.Zero)
                    {
                        DelayedSendAsync(message, wait);
                        continue;
                    }
                }

                foreach (var endpoint in _endpoints.Values)
                {
                    var task = endpoint.Handle(message);
                    tasks.Add(task);
                }
            }

            await Task.WhenAll(tasks);
        }
        finally
        {
            if (Interlocked.Decrement(ref _count) == 0)
            {
                _emptySignal.Release();
            }
        }
    }
    async void DelayedSendAsync(OutgoingMessage message, TimeSpan delay)
    {
        try
        {
            await Task.Delay(delay, _cts.Token);
            var transaction = (OutgoingTransaction)await message.Bus.CreateTransaction();
            message.DeliverAt = null;
            transaction.OutgoingMessages.Add(message);
            await Send(transaction);
        }
        catch (OperationCanceledException)
        {
            // Ignore cancellation
        }
        catch (Exception error)
        {
            var logger = message.State.Values.OfType<ILogger>().FirstOrDefault();
            logger?.LogError(error, error.Message);
        }
    }

    public bool UseSubscriptions { get; set; }

    public Task Start()
    {
        _active = true;
        return Task.CompletedTask;
    }
    bool _active;

    public async Task Stop()
    {
        _active = false;
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
