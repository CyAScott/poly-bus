using PolyBus.Transport;
using PolyBus.Transport.InMemory;
using PolyBus.Transport.Transactions;
using PolyBus.Transport.Transactions.Messages;
using PolyBus.Transport.Transactions.Messages.Handlers;

namespace PolyBus;

public class PolyBusBuilder
{
    /// <summary>
    /// The transaction factory will be used to create transactions for message handling.
    /// Transactions are used to ensure that a group of message related to a single request
    /// are sent to the transport in a single atomic operation.
    /// </summary>
    public TransactionFactory TransactionFactory { get; set; } = (_, bus, message) =>
        Task.FromResult<Transaction>(
            message != null
            ? new IncomingTransaction(bus, message)
            : new OutgoingTransaction(bus));

    /// <summary>
    /// The transport factory will be used to create the transport for the PolyBus instance.
    /// The transport is responsible for sending and receiving messages.
    /// </summary>
    public TransportFactory TransportFactory { get; set; } = (builder, bus) =>
    {
        var transport = new InMemoryTransport();

        return Task.FromResult(transport.AddEndpoint(builder, bus));
    };

    public Dictionary<string, object> Properties { get; } = [];

    public IList<IncomingHandler> IncomingHandlers { get; } = [];

    public IList<OutgoingHandler> OutgoingHandlers { get; } = [];

    public Messages Messages { get; } = new();

    public string Name { get; set; } = "PolyBusInstance";

    public virtual async Task<IPolyBus> Build()
    {
        var bus = new PolyBus(this);

        bus.Transport = await TransportFactory(this, bus);

        return bus;
    }
}
