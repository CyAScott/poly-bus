using PolyBus.Transport;
using PolyBus.Transport.InMemory;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;
using PolyBus.Transport.Transactions.Messages.Handlers;

namespace PolyBus;

public class PolyBusBuilder
{
    /// <summary>
    /// The incoming transaction factory will be used to create incoming transactions for handling messages.
    /// </summary>
    public IncomingTransactionFactory IncomingTransactionFactory { get; set; } = (_, bus, message) =>
        Task.FromResult(new IncomingTransaction(bus, message));

    /// <summary>
    /// The outgoing transaction factory will be used to create outgoing transactions for sending messages.
    /// </summary>
    public OutgoingTransactionFactory OutgoingTransactionFactory { get; set; } = (_, bus) =>
        Task.FromResult(new OutgoingTransaction(bus));

    /// <summary>
    /// The transport factory will be used to create the transport for the PolyBus instance.
    /// The transport is responsible for sending and receiving messages.
    /// </summary>
    public TransportFactory TransportFactory { get; set; } = (builder, bus) =>
    {
        var transport = new InMemoryMessageBroker();

        return transport.AddEndpoint(builder, bus);
    };

    public IDictionary<string, object> Properties { get; } = new Dictionary<string, object>();

    public IList<IncomingHandler> IncomingPipeline { get; } = [];

    public IList<OutgoingHandler> OutgoingPipeline { get; } = [];

    public Messages Messages { get; } = new();

    public string Name { get; set; } = "polybus";

    public virtual async Task<IPolyBus> Build()
    {
        var bus = new PolyBus(this);

        bus.Transport = await TransportFactory(this, bus);

        return bus;
    }
}
