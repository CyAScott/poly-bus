namespace PolyBus.Transport.Transactions.Messages;

public enum MessageType
{
    /// <summary>
    /// Command message type.
    /// Commands are messages that are sent to and processed by a single endpoint.
    /// </summary>
    Command,

    /// <summary>
    /// Event message type.
    /// Events are messages that can be processed by multiple endpoints and sent from a single endpoint.
    /// </summary>
    Event
}
