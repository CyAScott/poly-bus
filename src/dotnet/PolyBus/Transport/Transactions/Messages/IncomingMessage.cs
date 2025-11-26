using System.Diagnostics;

namespace PolyBus.Transport.Transactions.Messages;

[DebuggerStepThrough]
public class IncomingMessage(IPolyBus bus, string body, MessageInfo messageInfo) : Message(bus)
{
    /// <summary>
    /// The message info describing metadata about the message.
    /// </summary>
    public virtual MessageInfo MessageInfo { get; set; } = messageInfo ?? throw new ArgumentNullException(nameof(messageInfo));

    /// <summary>
    /// The default is string, but can be changed based on deserialization.
    /// </summary>
    public virtual Type MessageType { get; set; } = bus.Messages.GetTypeByMessageInfo(messageInfo);

    /// <summary>
    /// The message body contents.
    /// </summary>
    public virtual string Body { get; set; } = body ?? throw new ArgumentNullException(nameof(body));

    /// <summary>
    /// The deserialized message object, otherwise the same value as Body.
    /// </summary>
    public virtual object Message { get; set; } = body;
}
