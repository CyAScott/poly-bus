using System.Collections.Concurrent;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport.InMemory;

/// <summary>
/// An implementation of an in-memory transport endpoint.
/// </summary>
public class InMemoryEndpoint(InMemoryMessageBroker broker, IPolyBus bus) : ITransport
{
    /// <summary>
    /// The associated PolyBus instance.
    /// </summary>
    public IPolyBus Bus => bus;

    public Action<IncomingMessage>? DeadLetterHandler { get; set; }

    public bool Active { get; private set; }

    public string DeadLetterEndpoint => $"{bus.Name}.dead.letters";

    /// <summary>
    /// If active, handles an incoming message by creating a transaction and executing the handlers for the bus.
    /// </summary>
    public async Task HandleMessage(IncomingMessage message, bool isDeadLetter)
    {
        if (Active)
        {
            if (isDeadLetter)
            {
                DeadLetterHandler?.Invoke(message);
            }
            else
            {
                var transaction = await bus.CreateIncomingTransaction(message);

                await bus.Send(transaction);
            }
        }
    }

    public Task Handle(Transaction transaction)
    {
        if (!Active)
        {
            throw new PolyBusNotStartedError();
        }

        broker.Send(transaction);

        return Task.CompletedTask;
    }
    public bool SupportsDelayedCommands => true;
    public bool SupportsCommandMessages => true;

    public Task Subscribe(MessageInfo messageInfo)
    {
        if (!Active)
        {
            throw new PolyBusNotStartedError();
        }

        _subscriptions[messageInfo.ToString(false)] = true;

        return Task.CompletedTask;
    }
    public bool IsSubscribed(MessageInfo messageInfo) => _subscriptions.ContainsKey(messageInfo.ToString(false));
    public bool SupportsSubscriptions => true;
    readonly ConcurrentDictionary<string, bool> _subscriptions = new();

    public Task Start()
    {
        Active = true;
        return Task.CompletedTask;
    }

    public Task Stop()
    {
        Active = false;
        return Task.CompletedTask;
    }
}
