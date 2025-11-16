using System.Diagnostics;

namespace PolyBus.Transport.Transactions.Messages;

[DebuggerStepThrough]
public class Message(IPolyBus bus)
{
    /// <summary>
    /// State dictionary that can be used to store arbitrary data associated with the message.
    /// </summary>
    public virtual IDictionary<string, object> State { get; } = new Dictionary<string, object>();

    /// <summary>
    /// Message headers from the transport.
    /// </summary>
    public virtual IDictionary<string, string> Headers { get; set; } = new Dictionary<string, string>();

    /// <summary>
    /// The bus instance associated with the message.
    /// </summary>
    public IPolyBus Bus => bus ?? throw new ArgumentNullException(nameof(bus));
}
