using System.Diagnostics;
using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport.Transactions;

[DebuggerStepThrough]
public class IncomingTransaction(IPolyBus bus, IncomingMessage incomingMessage) : Transaction(bus)
{
    /// <summary>
    /// The incoming message from the transport being processed.
    /// </summary>
    public virtual IncomingMessage IncomingMessage { get; set; } = incomingMessage ?? throw new ArgumentNullException(nameof(incomingMessage));
}
