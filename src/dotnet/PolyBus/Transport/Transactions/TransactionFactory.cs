using PolyBus.Transport.Transactions.Messages;

namespace PolyBus.Transport.Transactions;

/// <summary>
/// A method for creating a new transaction for processing a request.
/// This should be used to integrate with external transaction systems to ensure message processing
/// is done within the context of a transaction.
/// </summary>
public delegate Task<Transaction> TransactionFactory(PolyBusBuilder builder, IPolyBus bus, IncomingMessage? message = null);
