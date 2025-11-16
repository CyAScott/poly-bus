using System.Diagnostics;

namespace PolyBus.Transport.Transactions;

[DebuggerStepThrough]
public class OutgoingTransaction(IPolyBus bus) : Transaction(bus);
