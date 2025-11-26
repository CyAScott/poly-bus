using System.Diagnostics;
using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport.Transactions;

[DebuggerStepThrough]
public class Transaction(IPolyBus bus)
{
    /// <summary>
    /// The bus instance associated with the transaction.
    /// </summary>
    public IPolyBus Bus => bus ?? throw new ArgumentNullException(nameof(bus));

    /// <summary>
    /// State dictionary that can be used to store arbitrary data associated with the transaction.
    /// </summary>
    public virtual IDictionary<string, object> State { get; } = new Dictionary<string, object>();

    /// <summary>
    /// A list of outgoing messages to be sent when the transaction is committed.
    /// </summary>
    public virtual IList<OutgoingMessage> OutgoingMessages { get; } = [];

    public virtual OutgoingMessage Add(object message, string? endpoint = null)
    {
        var outgoingMessage = new OutgoingMessage(bus, message, endpoint);
        OutgoingMessages.Add(outgoingMessage);
        return outgoingMessage;
    }

    /// <summary>
    /// If an exception occurs during processing, the transaction will be aborted.
    /// </summary>
    public virtual Task Abort() => Task.CompletedTask;

    /// <summary>
    /// If no exception occurs during processing, the transaction will be committed.
    /// </summary>
    public virtual Task Commit() => Bus.Send(this);
}
