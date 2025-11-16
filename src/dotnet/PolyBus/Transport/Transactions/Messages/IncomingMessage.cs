using System.Diagnostics;

namespace PolyBus.Transport.Transactions.Messages;

[DebuggerStepThrough]
public class IncomingMessage(IPolyBus bus, string body, object? message = null, Type? messageType = null) : Message(bus)
{
    /// <summary>
    /// The default is string, but can be changed based on deserialization.
    /// </summary>
    public virtual Type MessageType { get; set; } = messageType ?? typeof(string);

    /// <summary>
    /// The message body contents.
    /// </summary>
    public virtual string Body { get; set; } = body ?? throw new ArgumentNullException(nameof(body));

    /// <summary>
    /// The deserialized message object, otherwise the same value as Body.
    /// </summary>
    public virtual object Message { get; set; } = message ?? body;
}
