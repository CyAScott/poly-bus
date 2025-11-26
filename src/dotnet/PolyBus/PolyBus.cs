using PolyBus.Transport;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;
using PolyBus.Transport.Transactions.Messages.Handlers;

namespace PolyBus;

public class PolyBus(PolyBusBuilder builder) : IPolyBus
{
    public IDictionary<string, object> Properties => builder.Properties;

    public ITransport Transport { get; set; } = null!;

    public IList<IncomingHandler> IncomingPipeline { get; } = builder.IncomingPipeline;

    public IList<OutgoingHandler> OutgoingPipeline { get; } = builder.OutgoingPipeline;

    public Messages Messages { get; } = builder.Messages;

    public Task<IncomingTransaction> CreateIncomingTransaction(IncomingMessage message) =>
        builder.IncomingTransactionFactory(builder, this, message);

    public  Task<OutgoingTransaction> CreateOutgoingTransaction() =>
        builder.OutgoingTransactionFactory(builder, this);

    public async Task Send(Transaction transaction)
    {
        var step = () => Transport.Handle(transaction);

        if (transaction is IncomingTransaction incomingTransaction)
        {
            var handlers = transaction.Bus.IncomingPipeline;
            for (var index = handlers.Count - 1; index >= 0; index--)
            {
                var handler = handlers[index];
                var next = step;
                step = () => handler(incomingTransaction, next);
            }
        }
        else if (transaction is OutgoingTransaction outgoingTransaction)
        {
            var handlers = transaction.Bus.OutgoingPipeline;
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
