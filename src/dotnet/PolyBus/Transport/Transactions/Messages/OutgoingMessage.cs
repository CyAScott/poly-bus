using System.Diagnostics;

namespace PolyBus.Transport.Transactions.Messages;

[DebuggerStepThrough]
public class OutgoingMessage(IPolyBus bus, object message, string endpoint) : Message(bus)
{
    /// <summary>
    /// If the transport supports delayed messages, this is the time at which the message should be delivered.
    /// </summary>
    public virtual DateTime? DeliverAt { get; set; }

    public virtual Type MessageType { get; set; } = message.GetType();

    /// <summary>
    /// The serialized message body contents.
    /// </summary>
    public virtual string Body { get; set; } = message.ToString() ?? string.Empty;

    /// <summary>
    /// If the message is a command then this is the endpoint the message is being sent to.
    /// If the message is an event then this is the source endpoint the message is being sent from.
    /// </summary>
    public virtual string Endpoint { get; set; } = endpoint;

    /// <summary>
    /// The message object.
    /// </summary>
    public virtual object Message { get; set; } = message;
}
