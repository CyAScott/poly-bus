using PolyBus.Transport;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;
using PolyBus.Transport.Transactions.Messages.Handlers;

namespace PolyBus;

public interface IPolyBus
{
    IDictionary<string, object> Properties { get; }

    ITransport Transport { get; }

    IList<IncomingHandler> IncomingHandlers { get; }

    IList<OutgoingHandler> OutgoingHandlers { get; }

    Messages Messages { get; }

    Task<Transaction> CreateTransaction(IncomingMessage? message = null);

    Task Send(Transaction transaction);

    Task Start();

    Task Stop();

    string Name { get; }
}
