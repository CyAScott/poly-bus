using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport;

/// <summary>
/// An interface for a transport mechanism to send and receive messages.
/// </summary>
public interface ITransport
{
    /// <summary>
    /// Where messages that cannot be delivered are sent.
    /// </summary>
    string DeadLetterEndpoint { get; }

    /// <summary>
    /// Sends messages associated with the given transaction to the transport.
    /// </summary>
    Task Handle(Transaction transaction);

    /// <summary>
    /// If the transport supports sending delayed commands, this will be true.
    /// </summary>
    bool SupportsDelayedCommands { get; }

    /// <summary>
    /// If the transport supports sending command messages, this will be true.
    /// </summary>
    bool SupportsCommandMessages { get; }

    /// <summary>
    /// Subscribes to a messages so that the transport can start receiving them.
    /// </summary>
    Task Subscribe(MessageInfo messageInfo);

    /// <summary>
    /// If the transport supports event message subscriptions, this will be true.
    /// </summary>
    bool SupportsSubscriptions { get; }

    /// <summary>
    /// Starts the transport to start processing messages.
    /// </summary>
    Task Start();

    /// <summary>
    /// Stops the transport from processing messages.
    /// </summary>
    Task Stop();
}
