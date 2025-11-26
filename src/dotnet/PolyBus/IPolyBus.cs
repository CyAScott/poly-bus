using PolyBus.Transport;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;
using PolyBus.Transport.Transactions.Messages.Handlers;

namespace PolyBus;

public interface IPolyBus
{
    IDictionary<string, object> Properties { get; }

    ITransport Transport { get; }

    IList<IncomingHandler> IncomingPipeline { get; }

    IList<OutgoingHandler> OutgoingPipeline { get; }

    Messages Messages { get; }

    Task<IncomingTransaction> CreateIncomingTransaction(IncomingMessage message);

    Task<OutgoingTransaction> CreateOutgoingTransaction();

    Task Send(Transaction transaction);

    Task Start();

    Task Stop();

    string Name { get; }
}
