namespace PolyBus.Transport.Transactions.Messages.Handlers;

/// <summary>
/// A method for handling outgoing messages to the transport.
/// </summary>
public delegate Task OutgoingHandler(OutgoingTransaction transaction, Func<Task> next);
