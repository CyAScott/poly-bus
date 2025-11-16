using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport;

/// <summary>
/// An interface for a transport mechanism to send and receive messages.
/// </summary>
public interface ITransport
{
    bool SupportsDelayedMessages { get; }

    bool SupportsCommandMessages { get; }

    bool SupportsSubscriptions { get; }

    /// <summary>
    /// Sends messages associated with the given transaction to the transport.
    /// </summary>
    Task Send(Transaction transaction);

    /// <summary>
    /// Subscribes to a messages so that the transport can start receiving them.
    /// </summary>
    Task Subscribe(MessageInfo messageInfo);

    /// <summary>
    /// Enables the transport to start processing messages.
    /// </summary>
    Task Start();

    /// <summary>
    /// Stops the transport from processing messages.
    /// </summary>
    Task Stop();
}
