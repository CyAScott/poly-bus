using System.Diagnostics;

namespace PolyBus.Transport.Transactions.Messages;

[DebuggerStepThrough]
public class OutgoingMessage(IPolyBus bus, object message, string? endpoint = null, MessageInfo? messageInfo = null) : Message(bus)
{
    /// <summary>
    /// If the transport supports delayed messages, this is the time at which the message should be delivered.
    /// </summary>
    public virtual DateTime? DeliverAt { get; set; }

    /// <summary>
    /// The message info describing metadata about the message.
    /// </summary>
    public virtual MessageInfo MessageInfo { get; set; } = messageInfo ?? bus.Messages.GetMessageInfo(message.GetType());

    /// <summary>
    /// The type of the message.
    /// </summary>
    public virtual Type MessageType { get; set; } = message.GetType();

    /// <summary>
    /// An optional location to explicitly send the message to.
    /// </summary>
    public virtual string? Endpoint { get; set; } = endpoint;

    /// <summary>
    /// The serialized message body contents.
    /// </summary>
    public virtual string Body { get; set; } = string.Empty;

    /// <summary>
    /// The message object.
    /// </summary>
    public virtual object Message { get; set; } = message;
}
