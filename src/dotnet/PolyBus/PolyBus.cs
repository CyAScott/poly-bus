using PolyBus.Transport;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;
using PolyBus.Transport.Transactions.Messages.Handlers;

namespace PolyBus;

public class PolyBus(PolyBusBuilder builder) : IPolyBus
{
    public IDictionary<string, object> Properties => builder.Properties;

    public ITransport Transport { get; set; } = null!;

    public IList<IncomingHandler> IncomingHandlers { get; } = builder.IncomingHandlers;

    public IList<OutgoingHandler> OutgoingHandlers { get; } = builder.OutgoingHandlers;

    public Messages Messages { get; } = builder.Messages;

    public Task<Transaction> CreateTransaction(IncomingMessage? message = null) =>
        builder.TransactionFactory(builder, this, message);

    public async Task Send(Transaction transaction)
    {
        var step = () => Transport.Send(transaction);

        if (transaction is IncomingTransaction incomingTransaction)
        {
            var handlers = transaction.Bus.IncomingHandlers;
            for (var index = handlers.Count - 1; index >= 0; index--)
            {
                var handler = handlers[index];
                var next = step;
                step = () => handler(incomingTransaction, next);
            }
        }
        else if (transaction is OutgoingTransaction outgoingTransaction)
        {
            var handlers = transaction.Bus.OutgoingHandlers;
            for (var index = handlers.Count - 1; index >= 0; index--)
            {
                var handler = handlers[index];
                var next = step;
                step = () => handler(outgoingTransaction, next);
            }
        }

        try
        {
            await step();
        }
        catch
        {
            await transaction.Abort();
            throw;
        }
    }

    public Task Start() => Transport.Start();

    public Task Stop() => Transport.Stop();

    public string Name => builder.Name;
}
