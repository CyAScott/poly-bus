namespace PolyBus.Transport.Transactions.Messages.Handlers;

/// <summary>
/// A method for handling incoming messages from the transport.
/// </summary>
public delegate Task IncomingHandler(IncomingTransaction transaction, Func<Task> next);
